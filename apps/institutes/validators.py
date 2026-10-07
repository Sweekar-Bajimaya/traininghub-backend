import os

from django.conf import settings
from django.core.exceptions import ValidationError

from apps.common.constants import LocationLevel


def validate_institute_location(location):
    if location.level != LocationLevel.MUNICIPALITY or not location.is_active:
        raise ValidationError("Choose an active municipality.")


def _validate_upload(file, extensions):
    extension = os.path.splitext(file.name)[1].lower().lstrip(".")
    if extension not in extensions:
        raise ValidationError(f"Allowed file types: {', '.join(extensions)}")
    if file.size > settings.INSTITUTE_UPLOAD_MAX_BYTES:
        raise ValidationError(
            f"The file is larger than {settings.INSTITUTE_UPLOAD_MAX_BYTES // (1024 * 1024)} MB."
        )


def validate_document_file(file):
    _validate_upload(file, settings.INSTITUTE_DOCUMENT_EXTENSIONS)


def validate_image_file(file):
    _validate_upload(file, settings.INSTITUTE_IMAGE_EXTENSIONS)
