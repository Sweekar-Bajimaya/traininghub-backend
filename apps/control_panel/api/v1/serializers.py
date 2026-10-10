from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.common import services as common_services
from apps.common.models.category import Category
from apps.common.serializers import (
    DynamicFieldsModelSerializer,
    DynamicFieldsSerializer,
)
from apps.institutes.constants import DocumentStatus
from apps.institutes.models import Institute, InstituteDocument
from apps.training.api.v1.serializers import (
    LearningOutcomeSerializer,
    PortalTrainingListSerializer,
    PortalTrainingSerializer,
    TrainingContentFields,
    TrainingModuleSerializer,
    TrainingSessionSerializer,
)
from apps.training.models import Training
from apps.users import services as user_services
from apps.users.api.v1.serializers import ProfileSerializer
from apps.users.constants import GRANTABLE_PERMISSIONS

User = get_user_model()


class ReasonSerializer(DynamicFieldsSerializer):
    """The body of every review action that needs a reason (reject, request changes or info, suspend)."""

    reason = serializers.CharField()


# admins
class AdminSerializer(ProfileSerializer):
    """Admin serializer class for admin related work"""

    password = serializers.CharField(write_only=True, required=False)
    permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=GRANTABLE_PERMISSIONS), required=False
    )

    class Meta(ProfileSerializer.Meta):
        fields = ProfileSerializer.Meta.fields + ("password", "is_active")
        read_only_fields = ("id", "role", "created_at", "last_login", "is_active")
        create_only_fields = ("email", "password")  # read-only after password creation
        extra_kwargs = {
            **ProfileSerializer.Meta.extra_kwargs,
            "email": {
                "validators": [
                    UniqueValidator(
                        queryset=User.objects.all(),
                        lookup="iexact",
                        message="A user with that email already exists.",
                    )
                ]
            },
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["permissions"] = self.get_permissions(instance)
        return data

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if self.instance is None and "password" not in attrs:
            raise serializers.ValidationError({"password": "This field is required."})
        if self.instance is not None and "password" in attrs:
            raise serializers.ValidationError(
                {"password": "The password cannot be changed here."}
            )
        return attrs

    def create(self, validated_data):
        return user_services.create_admin(**validated_data)

    def update(self, instance, validated_data):
        return user_services.update_admin(instance, **validated_data)


# categories
class AdminCategorySerializer(DynamicFieldsModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(parent__isnull=True),
        required=False,
        allow_null=True,
    )
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "slug",
            "name",
            "parent",
            "parent_name",
            "icon",
            "hue",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "slug", "created_at")
        extra_kwargs = {
            "hue": {"max_value": 360}
        }  # the database constraint says the same

    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent_id else None

    def validate(self, attrs):
        name = attrs.get("name", getattr(self.instance, "name", "")).strip()
        parent = attrs.get("parent", getattr(self.instance, "parent", None))
        clash = Category.objects.filter(name__iexact=name, parent=parent)
        if self.instance:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise serializers.ValidationError(
                {"name": "A category with this name already exists here."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("is_active", None)
        return common_services.create_category(**validated_data)

    def update(self, instance, validated_data):
        return common_services.update_category(instance, **validated_data)


# institutes
class AdminDocumentSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = InstituteDocument
        fields = ("id", "name", "status", "created_at")  # never the file path or URL
        read_only_fields = ("id", "name", "created_at")


class DocumentReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=(DocumentStatus.VERIFIED, DocumentStatus.REJECTED)
    )


class AdminInstituteSerializer(DynamicFieldsModelSerializer):
    documents = AdminDocumentSerializer(many=True, read_only=True)
    owner_email = serializers.SerializerMethodField()

    class Meta:
        model = Institute
        fields = (
            "id",
            "slug",
            "name",
            "type",
            "status",
            "status_reason",
            "established_year",
            "description",
            "created_at",
            "owner_email",
            "documents",
        )

    def get_owner_email(self, obj):
        owners = getattr(obj, "owner_members", [])  # prefetched by the admin viewset
        return owners[0].user.email if owners else None


# trainings
class AdminTrainingListSerializer(PortalTrainingListSerializer):
    institute_name = serializers.CharField(source="institute.name", read_only=True)

    class Meta(PortalTrainingListSerializer.Meta):
        fields = PortalTrainingListSerializer.Meta.fields + ("institute_name",)


class AdminTrainingSerializer(TrainingContentFields, DynamicFieldsModelSerializer):
    """Read-only view of a whole training for the reviewer."""

    institute = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    institute_location = serializers.SerializerMethodField()
    sessions = TrainingSessionSerializer(many=True, read_only=True)
    modules = TrainingModuleSerializer(many=True, read_only=True)
    outcomes = LearningOutcomeSerializer(many=True, read_only=True)

    class Meta:
        model = Training
        fields = PortalTrainingSerializer.Meta.fields + ("institute",)
        read_only_fields = fields

    def get_institute(self, obj):
        return {
            "id": obj.institute_id,
            "name": obj.institute.name,
            "status": obj.institute.status,
        }

    def get_category(self, obj):
        parent = obj.category.parent
        return {
            "id": obj.category_id,
            "name": obj.category.name,
            "parent": parent.name if parent else None,
        }

    def get_institute_location(self, obj):
        place = obj.institute_location
        if place is None:
            return None
        return {
            "id": place.id,
            "municipality": place.location.name,
            "address": place.address,
        }
