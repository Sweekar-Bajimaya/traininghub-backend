import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django_q.tasks import async_task

from apps.institutes.constants import (
    DocumentStatus,
    InstituteStatus,
    InvitationStatus,
    MemberRole,
)
from apps.institutes.models import (
    Institute,
    InstituteDocument,
    InstituteGalleryImage,
    InstituteInvitation,
    InstituteLocation,
    InstituteMember,
)
from apps.institutes.validators import validate_institute_location
from apps.users import services as user_services
from apps.users.constants import Role

User = get_user_model()


# ---------------------------------------------------------------- status workflow


def _transition(institute, to, *, reason="", check=None):
    """Move an institute to a new status. Caller must be inside transaction.atomic()."""
    institute = Institute.objects.select_for_update().get(pk=institute.pk)
    if to not in InstituteStatus.TRANSITIONS[institute.status]:
        raise ValidationError(f"Cannot move from {institute.status} to {to}.")
    if to in InstituteStatus.REASON_REQUIRED and not reason.strip():
        raise ValidationError({"reason": "A reason is required."})
    if check:
        check(institute)
    institute.status = to
    institute.status_reason = reason
    institute.save(update_fields=["status", "status_reason", "modified_at"])
    return institute


def _ready_for_approval(institute):
    if not institute.locations.filter(is_active=True).exists():
        raise ValidationError("Add at least one active location before approval.")
    if not institute.documents.exists():
        raise ValidationError(
            "Upload at least one verification document before approval."
        )


@transaction.atomic
def approve(institute, *, by):
    # TODO(audit) + TODO(notify): the institute owner
    return _transition(institute, InstituteStatus.APPROVED, check=_ready_for_approval)


@transaction.atomic
def reject(institute, *, by, reason):
    return _transition(institute, InstituteStatus.REJECTED, reason=reason)


@transaction.atomic
def request_info(institute, *, by, reason):
    return _transition(institute, InstituteStatus.INFO_REQUESTED, reason=reason)


@transaction.atomic
def suspend(institute, *, by, reason):
    # Staff keep their accounts (they can still log in); the public queries hide the institute.
    return _transition(institute, InstituteStatus.SUSPENDED, reason=reason)


@transaction.atomic
def reinstate(institute, *, by):
    return _transition(institute, InstituteStatus.APPROVED)


@transaction.atomic
def resubmit(institute):
    """The owner answers an info request, or re-applies after a rejection."""
    return _transition(institute, InstituteStatus.PENDING)


# ---------------------------------------------------------------- registration and locations


@transaction.atomic
def register(*, institute_data, owner, locations=()):
    """Create an institute, its owner account and its locations in one transaction.

    owner = {"email", "password", "full_name", optional "phone_number"}; the owner is always
    INSTITUTE_STAFF. Documents are uploaded afterwards through the portal.
    """
    for item in locations:
        validate_institute_location(item["location"])  # bulk_create skips model validation
    institute = Institute.objects.create(**institute_data)
    owner_user = User.objects.create_user(role=Role.INSTITUTE_STAFF, **owner)
    InstituteMember.objects.create(
        user=owner_user, institute=institute, role=MemberRole.OWNER
    )
    InstituteLocation.objects.bulk_create(
        [
            InstituteLocation(
                institute=institute, is_main=(i == 0), **item
            )  # the first one is the main office
            for i, item in enumerate(locations)
        ]
    )
    # TODO(notify): admins with manage_institutes
    return institute


@transaction.atomic
def add_location(institute, *, location, address, contact_phone=""):
    validate_institute_location(location)
    Institute.objects.select_for_update().get(pk=institute.pk)  # serialise per institute
    first = not institute.locations.filter(is_active=True).exists()
    return InstituteLocation.objects.create(
        institute=institute,
        location=location,
        address=address,
        contact_phone=contact_phone,
        is_main=first,
    )


@transaction.atomic
def update_location(instance, **fields):
    if "location" in fields:
        validate_institute_location(fields["location"])
    instance = InstituteLocation.objects.select_for_update().get(pk=instance.pk)
    for name, value in fields.items():
        setattr(instance, name, value)
    instance.save(update_fields=[*fields, "modified_at"])
    return instance


@transaction.atomic
def set_main_location(location):
    Institute.objects.select_for_update().get(pk=location.institute_id)
    location = InstituteLocation.objects.get(pk=location.pk)
    if not location.is_active:
        raise ValidationError("An inactive location cannot be the main office.")
    InstituteLocation.objects.filter(
        institute_id=location.institute_id, is_main=True
    ).exclude(pk=location.pk).update(is_main=False)  # clear first, then set (partial unique index)
    location.is_main = True
    location.save(update_fields=["is_main", "modified_at"])
    return location


@transaction.atomic
def deactivate_location(location):
    Institute.objects.select_for_update().get(pk=location.institute_id)
    location = InstituteLocation.objects.get(pk=location.pk)
    if location.is_main:
        raise ValidationError("Choose another main office first.")
    # TODO(catalog): refuse while non-terminal trainings use it (409)
    location.is_active = False
    location.save(update_fields=["is_active", "modified_at"])
    return location


# ---------------------------------------------------------------- documents and gallery


@transaction.atomic
def add_document(institute, *, name, file):
    return InstituteDocument.objects.create(institute=institute, name=name, file=file)


@transaction.atomic
def review_document(document, *, status, by):
    if status not in (DocumentStatus.VERIFIED, DocumentStatus.REJECTED):
        raise ValidationError({"status": "Choose VERIFIED or REJECTED."})
    document = InstituteDocument.objects.select_for_update().get(pk=document.pk)
    document.status = status
    document.save(update_fields=["status", "modified_at"])
    return document


@transaction.atomic
def add_gallery_image(institute, *, image, caption=""):
    Institute.objects.select_for_update().get(pk=institute.pk)
    return InstituteGalleryImage.objects.create(
        institute=institute,
        image=image,
        caption=caption,
        position=institute.gallery.count(),  # appended at the end
    )


@transaction.atomic
def reorder_gallery(institute, ids):
    images = {
        i.pk: i
        for i in InstituteGalleryImage.objects.select_for_update().filter(
            institute=institute
        )
    }
    if sorted(images) != sorted(ids):
        raise ValidationError("Send every gallery image id exactly once.")
    for position, pk in enumerate(ids):
        images[pk].position = position
    InstituteGalleryImage.objects.bulk_update(images.values(), ["position"])


# ---------------------------------------------------------------- staff and invitations


def _hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


@transaction.atomic
def invite(*, institute, email, by):
    """Invite a new staff member. The raw token exists only in the email and in memory:
    the database keeps a hash, and the queued task is not saved in django-q's results table."""
    email = email.strip()
    Institute.objects.select_for_update().get(pk=institute.pk)
    institute.invitations.filter(  # an expired invite must not block a new one
        email__iexact=email,
        status=InvitationStatus.PENDING,
        expires_at__lt=timezone.now(),
    ).update(status=InvitationStatus.REVOKED)
    if User.objects.filter(email__iexact=email).exists():
        raise ValidationError(
            {"email": "This email already has an account."}
        )  # one institute per user
    if institute.invitations.filter(
        email__iexact=email, status=InvitationStatus.PENDING
    ).exists():
        raise ValidationError(
            {"email": "An invitation is already pending for this email."}
        )
    token = secrets.token_urlsafe(32)
    invitation = InstituteInvitation.objects.create(
        institute=institute,
        email=email,
        role=MemberRole.STAFF,
        invited_by=by,
        token_hash=_hash(token),
        expires_at=timezone.now()
        + timedelta(days=settings.INSTITUTE_INVITATION_TTL_DAYS),
    )
    transaction.on_commit(
        lambda: async_task(
            "apps.institutes.tasks.send_invitation_email",
            invitation.pk,
            token,
            save=False,
        )
    )
    return invitation


@transaction.atomic
def accept_invitation(*, token, full_name, password):
    invitation = (
        InstituteInvitation.objects.select_for_update(of=("self",))
        .select_related("institute")
        .filter(token_hash=_hash(token), status=InvitationStatus.PENDING)
        .first()
    )
    if invitation is None or invitation.expires_at < timezone.now():
        raise ValidationError("This invitation is invalid or has expired.")
    if User.objects.filter(email__iexact=invitation.email).exists():
        raise ValidationError("This email already has an account.")
    user = User.objects.create_user(
        email=invitation.email,
        password=password,
        full_name=full_name,
        role=Role.INSTITUTE_STAFF,
    )
    InstituteMember.objects.create(
        user=user, institute=invitation.institute, role=invitation.role
    )
    invitation.status = InvitationStatus.ACCEPTED
    invitation.save(update_fields=["status", "modified_at"])
    return user


@transaction.atomic
def revoke_invitation(invitation, *, by):
    invitation = InstituteInvitation.objects.select_for_update().get(pk=invitation.pk)
    if invitation.status != InvitationStatus.PENDING:
        raise ValidationError("Only a pending invitation can be revoked.")
    invitation.status = InvitationStatus.REVOKED
    invitation.save(update_fields=["status", "modified_at"])
    return invitation


@transaction.atomic
def remove_staff(member, *, by):
    member = (
        InstituteMember.objects.select_for_update()
        .select_related("user")
        .get(pk=member.pk)
    )
    if member.role == MemberRole.OWNER:
        raise ValidationError("The owner cannot be removed.")
    user = member.user
    member.delete()
    # deactivates the account and revokes its refresh tokens
    user_services.set_status(user, active=False, by=by)
