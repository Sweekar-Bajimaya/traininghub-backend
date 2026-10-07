import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext as _

from apps.common.models.base import BaseModel
from apps.common.utils.helpers import get_upload_path
from apps.common.validators import validate_phone_number
from apps.users.constants import GENDER_CHOICES, Role
from apps.users.manager import UserManager


class User(AbstractUser, BaseModel):
    username = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    first_name = None
    last_name = None
    full_name = models.CharField(
        _('full name'),
        max_length=150,
        blank=True, null=True
    )

    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        }
    )

    # Below fields are optional
    profile_picture = models.ImageField(
        upload_to=get_upload_path,
        blank=True
    )

    role = models.CharField(max_length=20, choices=Role.CHOICES, default=Role.INSTITUTE_STAFF)

    phone_number = models.CharField(
        _('phone number'),
        null=True,
        blank=True,
        validators=[validate_phone_number],
        max_length=25,
        error_messages={
            'unique': _("A user with that phone number already exists."),
        },
        unique=True
    )
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True, null=True
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        permissions = [
            ("manage_enquiries", "Can handle enquiries"),
            ("manage_account_status", "Can activate/suspend accounts"),
            ("manage_institutes", "Can review institutes"),
            ("manage_trainings", "Can review trainings"),
            ("manage_categories", "Can manage categories and locations"),
            ("manage_admins", "Can manage admin users"),
        ]
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="users_user_email_ci_unique",
                violation_error_message=_("A user with that email already exists."),
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(role=Role.SUPER_ADMIN, is_superuser=True)
                    | (~models.Q(role=Role.SUPER_ADMIN) & models.Q(is_superuser=False))
                ),
                name="users_user_superuser_matches_role",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(role__in=(Role.SUPER_ADMIN, Role.ADMIN), is_staff=True)
                    | models.Q(role=Role.INSTITUTE_STAFF, is_staff=False)
                ),
                name="users_user_staff_matches_role",
            ),
            models.UniqueConstraint(
                fields=["role"],
                condition=models.Q(role=Role.SUPER_ADMIN),
                name="users_user_single_super_admin",
                violation_error_message=_("There can be only one super admin."),
            ),
        ]
        indexes = [
            models.Index(fields=["role", "is_active"], name="users_user_role_active_idx"),
        ]

    def __str__(self):
        return self.full_name or self.email

    def save(self, *args, **kwargs):
        # phone_number is unique, so "no phone" must be NULL, never ''.
        self.phone_number = self.phone_number or None
        # The role is the source of truth; the Django flags follow it so they
        # can never be set independently (e.g. from client input).
        self.is_superuser = self.role == Role.SUPER_ADMIN
        self.is_staff = self.role in (Role.SUPER_ADMIN, Role.ADMIN)
        super().save(*args, **kwargs)

    @property
    def is_super_admin(self):
        return self.role == Role.SUPER_ADMIN

    @property
    def is_platform_admin(self):
        return self.role in (Role.SUPER_ADMIN, Role.ADMIN)

