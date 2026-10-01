from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from apps.users.constants import GRANTABLE_PERMISSIONS, Role

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
        raise ValidationError(f"Cannot change {sorted(protected & fields.keys())} here.")
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
