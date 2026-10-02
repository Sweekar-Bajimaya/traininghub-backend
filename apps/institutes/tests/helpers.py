import io
import tempfile

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from PIL import Image

from apps.catalog.models import Location
from apps.institutes.constants import InstituteStatus, InstituteType, MemberRole
from apps.institutes.models import Institute, InstituteLocation, InstituteMember
from apps.users.constants import Role

User = get_user_model()
PASSWORD = "Str0ng-pass-123!"


def make_municipality(code=1, name="Municipality"):
    province, _ = Location.objects.get_or_create(
        level="PROVINCE", code=1, defaults={"name": "Province"}
    )
    district, _ = Location.objects.get_or_create(
        level="DISTRICT", code=1, defaults={"name": "District", "parent": province}
    )
    return Location.objects.create(
        level="MUNICIPALITY", code=code, name=name, parent=district, type="MUNICIPALITY"
    )


def make_institute(
    name="Alpha Institute", status=InstituteStatus.PENDING, email="owner@example.com"
):
    institute = Institute.objects.create(
        name=name, type=InstituteType.COMPANY, status=status
    )
    owner = User.objects.create_user(
        email, PASSWORD, full_name="Owner", role=Role.INSTITUTE_STAFF
    )
    InstituteMember.objects.create(
        user=owner, institute=institute, role=MemberRole.OWNER
    )
    return institute, owner


def add_location(institute, municipality, *, is_main=False, is_active=True):
    return InstituteLocation.objects.create(
        institute=institute,
        location=municipality,
        address="Main Road",
        is_main=is_main,
        is_active=is_active,
    )


def pdf(name="license.pdf"):
    return SimpleUploadedFile(name, b"%PDF-1.4 test", content_type="application/pdf")


class TempMediaMixin:
    """Put MEDIA_ROOT and PRIVATE_MEDIA_ROOT in temporary folders for the test."""

    def setUp(self):
        super().setUp()
        for setting in ("MEDIA_ROOT", "PRIVATE_MEDIA_ROOT"):
            folder = tempfile.TemporaryDirectory()
            self.addCleanup(folder.cleanup)
            override = override_settings(**{setting: folder.name})
            override.enable()
            self.addCleanup(override.disable)


def png(name="a.png"):
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), "white").save(buffer, "PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def reset_throttles():
    """Clear only the throttle counters; the same Redis database also holds the django-q broker."""
    cache.delete_pattern("throttle_*")


def count_queries(call):
    with CaptureQueriesContext(connection) as captured:
        call()
    return len(captured)
