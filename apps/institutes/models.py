from django.conf import settings
from django.db import models
from django.db.models.functions import Lower

from apps.common.models.base import BaseModel, SlugModel
from apps.common.utils.helpers import get_upload_path
from apps.common.validators import validate_phone_number
from apps.institutes.constants import (
    DocumentStatus,
    InstituteStatus,
    InstituteType,
    InvitationStatus,
    MemberRole,
)
from apps.institutes.storage import PrivateStorage
from apps.institutes.validators import validate_document_file, validate_image_file


class Institute(BaseModel, SlugModel):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=30, choices=InstituteType.CHOICES)
    established_year = models.PositiveSmallIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to=get_upload_path, blank=True, validators=[validate_image_file]
    )
    status = models.CharField(
        max_length=20, choices=InstituteStatus.CHOICES, default=InstituteStatus.PENDING
    )
    status_reason = models.TextField(blank=True)

    # profile
    ceo_name = models.CharField(max_length=150, blank=True)
    ceo_message = models.TextField(blank=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(
        max_length=25, blank=True, validators=[validate_phone_number]
    )
    facebook_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["status"], name="institutes_status_idx")]

    def __str__(self):
        return self.name


class InstituteMember(BaseModel):
    # OneToOne: a staff user belongs to ONE institute only, enforced by the database.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="membership"
    )
    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE, related_name="members"
    )
    role = models.CharField(max_length=10, choices=MemberRole.CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["institute"],
                condition=models.Q(role=MemberRole.OWNER),
                name="institutes_one_owner_per_institute",
            ),
        ]


class InstituteInvitation(BaseModel):
    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE, related_name="invitations"
    )
    email = models.EmailField()
    role = models.CharField(
        max_length=10, choices=MemberRole.CHOICES, default=MemberRole.STAFF
    )
    token_hash = models.CharField(
        max_length=64, unique=True
    )  # sha256 of the emailed token
    status = models.CharField(
        max_length=10,
        choices=InvitationStatus.CHOICES,
        default=InvitationStatus.PENDING,
    )
    expires_at = models.DateTimeField()
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(  # one pending invite per institute and email
                Lower("email"),
                "institute",
                condition=models.Q(status=InvitationStatus.PENDING),
                name="institutes_one_pending_invite",
            ),
        ]
        indexes = [
            models.Index(fields=["expires_at"], name="institutes_invite_expiry_idx")
        ]


class InstituteDocument(BaseModel):
    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE, related_name="documents"
    )
    name = models.CharField(max_length=150)
    file = models.FileField(
        upload_to=get_upload_path,
        storage=PrivateStorage,
        validators=[validate_document_file],
    )
    status = models.CharField(
        max_length=10, choices=DocumentStatus.CHOICES, default=DocumentStatus.PENDING
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["institute", "status"], name="institutes_doc_status_idx"
            )
        ]


class InstituteLocation(BaseModel):
    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE, related_name="locations"
    )
    # must be an active MUNICIPALITY-level Location; checked by validate_institute_location
    location = models.ForeignKey(
        "common.Location", on_delete=models.PROTECT, related_name="+"
    )
    address = models.CharField(max_length=255)
    map_url = models.URLField(blank=True)  # "Google Map location" link
    contact_phone = models.CharField(
        max_length=25, blank=True, validators=[validate_phone_number]
    )
    is_main = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["institute"],
                condition=models.Q(is_main=True, is_active=True),
                name="institutes_one_main_location",
            ),
            models.CheckConstraint(
                condition=~models.Q(is_main=True, is_active=False),
                name="institutes_main_location_is_active",
            ),
        ]
        indexes = [
            models.Index(
                fields=["institute", "is_active"], name="institutes_loc_active_idx"
            )
        ]


class InstituteGalleryImage(BaseModel):
    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE, related_name="gallery"
    )
    image = models.ImageField(
        upload_to=get_upload_path, validators=[validate_image_file]
    )
    caption = models.CharField(max_length=200, blank=True)
    position = models.PositiveSmallIntegerField(
        default=0
    )  # no unique: a reorder is one bulk_update

    class Meta:
        indexes = [
            models.Index(
                fields=["institute", "position"], name="institutes_gallery_pos_idx"
            )
        ]
