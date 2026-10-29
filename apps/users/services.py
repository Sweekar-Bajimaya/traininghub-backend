import secrets

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django_q.tasks import async_task
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from apps.common.exceptions import TooManyRequests
from apps.users.constants import (
    GRANTABLE_PERMISSIONS,
    OTP_COOLDOWN_SECONDS,
    OTP_LENGTH,
    OTP_MAX_ATTEMPTS,
    OTP_TTL_SECONDS,
    OTPPurpose,
    Role,
)

User = get_user_model()


def _set_permissions(admin, codenames):
    codenames = set(codenames)
    invalid = codenames - set(GRANTABLE_PERMISSIONS)
    if invalid:
        raise ValidationError({"permissions": f"Not grantable: {sorted(invalid)}"})

    admin.user_permissions.set(
        Permission.objects.filter(
            content_type__app_label="users", codename__in=codenames
        )
    )


def _revoke_refresh_tokens(user):
    tokens = OutstandingToken.objects.filter(user=user, blacklistedtoken__isnull=True)
    BlacklistedToken.objects.bulk_create(
        [BlacklistedToken(token=t) for t in tokens], ignore_conflicts=True
    )


@transaction.atomic
def create_admin(*, email, password, full_name, permissions=(), **extra):
    extra.pop("role", None)  # always forced below; never from client input
    admin = User.objects.create_user(
        email=email,
        password=password,
        full_name=full_name,
        role=Role.ADMIN,
        **extra,
    )
    _set_permissions(admin, permissions)
    # TODO(audit): AuditService.record(actor, "admin.created", admin)
    return admin


@transaction.atomic
def update_admin(admin, *, permissions=None, **fields):
    protected = {"email", "password", "role", "is_active", "is_staff", "is_superuser"}
    if protected & fields.keys():
        raise ValidationError(
            f"Cannot change {sorted(protected & fields.keys())} here."
        )
    admin = User.objects.select_for_update().get(pk=admin.pk)
    for name, value in fields.items():
        setattr(admin, name, value)
    admin.save(update_fields=[*fields, "modified_at"])
    if permissions is not None:
        _set_permissions(admin, permissions)
    return admin


@transaction.atomic
def set_status(user, *, active, by):
    user = User.objects.select_for_update().get(pk=user.pk)  # re-read under lock
    if user.pk == by.pk:
        raise ValidationError("You cannot change your own status.")
    if user.is_super_admin:
        raise PermissionDenied("The super admin cannot be suspended.")
    if user.role == Role.ADMIN and not by.is_super_admin:
        raise PermissionDenied("Only the super admin can change an admin's status.")

    user.is_active = active
    user.save(update_fields=["is_active", "modified_at"])

    if not active:
        _revoke_refresh_tokens(user)
    # TODO(audit): AuditService.record(by, "user.status", user, {"active": active})
    return user


@transaction.atomic
def change_password(user, new_password):
    user.set_password(new_password)
    user.save(update_fields=["password", "modified_at"])
    _revoke_refresh_tokens(user)


# one-time codes (password reset, email verification at institute registration)
# The code lives only in the cache, never in the queued task: the task gets the address and
# reads the code when it runs, so django-q's results table never stores a code.
OTP_EMAIL_TASKS = {
    OTPPurpose.PASSWORD_RESET: "apps.users.tasks.send_otp_email_task",
    OTPPurpose.INSTITUTE_REGISTRATION: "apps.users.tasks.send_registration_otp_email_task",
}


def normalize_email(email):
    return email.strip().lower()


def _otp_keys(email, purpose):
    """The three cache keys of one code. Built here only, from the normalised address, so a code
    written by one request is always found by the next."""
    email = normalize_email(email)
    return {
        "otp": f"{purpose}_otp_{email}",
        "attempts": f"{purpose}_otp_attempts_{email}",
        "cooldown": f"{purpose}_otp_cooldown_{email}",
    }


def send_otp(email, *, purpose, check=None):
    """Store a fresh code for `email` and queue the email. At most one code per address per
    OTP_COOLDOWN_SECONDS (TooManyRequests otherwise).

    `check` is an optional callable that raises ValidationError when no code should be sent
    (for example "no such account"). It runs after the cooldown is claimed, so an address that
    fails it still burns the cooldown: that keeps one address from being used to fan out mail.
    """
    email = normalize_email(email)
    keys = _otp_keys(email, purpose)
    # cache.add is an atomic set-if-absent: a get-then-set would let two parallel requests both
    # pass the cooldown and each send a code.
    if not cache.add(keys["cooldown"], True, timeout=OTP_COOLDOWN_SECONDS):
        raise TooManyRequests(
            "Please wait before requesting another code.",
            wait=cache.ttl(keys["cooldown"]) or OTP_COOLDOWN_SECONDS,
        )
    if check:
        check()
    otp = f"{secrets.randbelow(10**OTP_LENGTH):0{OTP_LENGTH}d}"
    cache.set(keys["otp"], otp, timeout=OTP_TTL_SECONDS)
    cache.set(
        keys["attempts"], 0, timeout=OTP_TTL_SECONDS
    )  # a new code starts a new count
    async_task(OTP_EMAIL_TASKS[purpose], email)


def send_password_reset_otp(email):
    def account_exists():
        # Existence is deliberately revealed: a reset form that says "sent" for an address with
        # no account leaves the user waiting for mail that never comes. The throttle is keyed
        # on the submitted address, so it does not stop someone walking a list of addresses.
        if not User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                {"email": "The e-mail address is not assigned to any user account."}
            )

    send_otp(email, purpose=OTPPurpose.PASSWORD_RESET, check=account_exists)


def send_registration_otp(email):
    """Email a verification code to the address that will be an institute owner's login, before
    the institute registers."""
    email = normalize_email(email)

    def not_taken():
        # Revealed on purpose: the registration itself would fail with the same message.
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError({"email": "A user with this email already exists."})

    send_otp(email, purpose=OTPPurpose.INSTITUTE_REGISTRATION, check=not_taken)


def verify_registration_otp(email, otp):
    """Check a registration code without using it up, so a form can confirm the email before it
    is submitted. The registration itself checks it again and uses it up."""
    verify_otp(email, otp, purpose=OTPPurpose.INSTITUTE_REGISTRATION)


def get_otp(email, *, purpose):
    """The current code, or None once it expired. Used by the email task."""
    return cache.get(_otp_keys(email, purpose)["otp"])


def verify_otp(email, otp, *, purpose):
    """Check a code without using it up. Wrong guesses count against OTP_MAX_ATTEMPTS."""
    keys = _otp_keys(email, purpose)
    expired = ValidationError(
        {"otp": "This code has expired or was never sent. Request a new one."}
    )
    expected = cache.get(keys["otp"])
    if expected is None:
        raise expired
    cache.add(keys["attempts"], 0, timeout=OTP_TTL_SECONDS)
    try:
        # counted before the comparison, so parallel guesses cannot slip past the limit
        attempts = cache.incr(keys["attempts"])
    except ValueError:  # the code expired a moment ago
        raise expired from None
    if attempts > OTP_MAX_ATTEMPTS:
        raise TooManyRequests(
            "Too many wrong codes. Request a new code.",
            wait=cache.ttl(keys["attempts"]) or None,
        )
    if not secrets.compare_digest(str(expected), str(otp)):
        raise ValidationError({"otp": "Invalid code."})
    try:
        cache.decr(keys["attempts"])  # a right code does not count as a guess
    except ValueError:
        pass


def consume_otp(email, *, purpose):
    """Use a verified code up so it cannot be replayed. cache.delete is True for only one of two
    parallel callers, which makes this the gate that lets a single request through."""
    keys = _otp_keys(email, purpose)
    if not cache.delete(keys["otp"]):
        raise ValidationError(
            {"otp": "This code was already used or has expired. Request a new one."}
        )
    cache.delete(keys["attempts"])


def send_otp_email(email, otp):
    html_message = render_to_string("email/otp_email.html", {"otp": otp})
    send_mail(
        subject="Your OTP Code - Merojob Mentor",
        message=f"Your OTP is {otp}. It expires in 5 minutes.",
        from_email=None,
        recipient_list=[email],
        html_message=html_message,
    )


def send_registration_otp_email(email, otp):
    html_message = render_to_string("email/registration_otp_email.html", {"otp": otp})
    send_mail(
        subject="Verify your email - Merojob Mentor",
        message=f"Your verification code is {otp}. It expires in 5 minutes.",
        from_email=None,
        recipient_list=[email],
        html_message=html_message,
    )
