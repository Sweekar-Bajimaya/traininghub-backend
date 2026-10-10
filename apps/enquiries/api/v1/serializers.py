import uuid

from rest_framework import serializers

from apps.common.serializers import DynamicFieldsModelSerializer
from apps.enquiries import services
from apps.enquiries.constants import (
    DEVICE_TOKEN_HEADER,
    MESSAGE_MAX_LENGTH,
    EnquiryStatus,
)
from apps.enquiries.models import Enquiry, EnquiryNote
from apps.enquiries.validators import normalize_phone
from apps.institutes.constants import InstituteStatus
from apps.training.constants import TrainingStatus
from apps.training.models import Training


def device_token_from(request):
    """The browser's device token (a UUID4 in the X-Device-Token header) as a string. A missing,
    malformed or non-random one (the all-zero UUID, say) is a 400: a token shared by several
    browsers would show them each other's enquiries."""
    try:
        token = uuid.UUID(request.headers.get(DEVICE_TOKEN_HEADER, ""))
    except ValueError:
        token = None
    if token is None or token.version != 4:
        raise serializers.ValidationError(
            {"device_token": [f"Send a random UUID4 in the {DEVICE_TOKEN_HEADER} header."]}
        )
    return str(token)


class NepalMobileField(serializers.CharField):
    default_error_messages = {
        "invalid": "Enter a 10-digit mobile number starting with 96, 97 or 98."
    }

    def to_internal_value(self, data):
        phone = normalize_phone(super().to_internal_value(data))
        if phone is None:
            self.fail("invalid")
        return phone


# visitor
class VisitorEnquirySerializer(serializers.ModelSerializer):
    """What the visitor who sent it sees: the training, the institute and a plain-language
    status. Never the phone number, the notes or the institute's internal status."""

    training = serializers.SerializerMethodField()
    institute_name = serializers.CharField(source="institute.name", read_only=True)
    status_label = serializers.SerializerMethodField()

    class Meta:
        model = Enquiry
        fields = (
            "id",
            "type",
            "training",
            "institute_name",
            "status_label",
            "created_at",
        )

    def get_training(self, obj):
        return {
            "id": obj.training_id,
            "slug": obj.training.slug,
            "title": obj.training.title,
        }

    def get_status_label(self, obj):
        return EnquiryStatus.VISITOR_LABELS[obj.status]


class EnquiryCreateSerializer(DynamicFieldsModelSerializer):
    """The public form. The training is its slug, and only a published training of an approved
    institute is found; the answer is the visitor's own view of the new enquiry."""

    training = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Training.objects.filter(
            status=TrainingStatus.APPROVED, institute__status=InstituteStatus.APPROVED
        ).select_related("institute"),
        error_messages={"does_not_exist": "This training is not accepting enquiries."},
    )
    phone = NepalMobileField()

    class Meta:
        model = Enquiry
        fields = (
            "training",
            "name",
            "phone",
            "email",
            "message",
            "type",
            "preferred_time",
        )
        extra_kwargs = {"name": {"min_length": 2}}

    def validate_email(self, value):
        return value.lower()

    def validate(self, attrs):
        attrs["device_token"] = device_token_from(self.request)
        return attrs

    def create(self, validated_data):
        return services.submit_enquiry(**validated_data)

    def to_representation(self, instance):
        return VisitorEnquirySerializer(instance, context=self.context).data


# portal
class EnquiryNoteSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    text = serializers.CharField(max_length=MESSAGE_MAX_LENGTH)

    class Meta:
        model = EnquiryNote
        fields = ("id", "text", "author", "created_at")
        read_only_fields = ("id", "created_at")

    def get_author(self, obj):
        # a former member's notes stay, without a name
        return (obj.author.full_name or obj.author.email) if obj.author else None

    def create(self, validated_data):  # `enquiry` and `author` come from the view's save()
        return services.add_note(**validated_data)


class PortalEnquiryListSerializer(DynamicFieldsModelSerializer):
    """One table row: no message and no notes, and the training comes from select_related."""

    training_title = serializers.CharField(source="training.title", read_only=True)

    class Meta:
        model = Enquiry
        fields = (
            "id",
            "name",
            "phone",
            "email",
            "type",
            "status",
            "training",
            "training_title",
            "created_at",
        )


class PortalEnquirySerializer(DynamicFieldsModelSerializer):
    """The drawer. Only `status` can be written."""

    training_title = serializers.CharField(source="training.title", read_only=True)
    notes = serializers.SerializerMethodField()

    class Meta:
        model = Enquiry
        fields = (
            "id",
            "name",
            "phone",
            "email",
            "message",
            "type",
            "preferred_time",
            "status",
            "training",
            "training_title",
            "notes",
            "created_at",
            "modified_at",
        )
        read_only_fields = tuple(
            name
            for name in fields
            if name not in ("status", "training_title", "notes")
        )

    def get_notes(self, obj):
        # one query with the authors, newest first; it does not depend on a prefetch, which DRF
        # throws away after an update
        notes = obj.notes.select_related("author")
        return EnquiryNoteSerializer(notes, many=True, context=self.context).data

    def update(self, instance, validated_data):
        if "status" not in validated_data:
            return instance
        return services.change_status(
            instance, status=validated_data["status"], by=self.request.user
        )
