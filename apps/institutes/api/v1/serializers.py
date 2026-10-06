from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.catalog.constants import LocationLevel
from apps.catalog.models import Location
from apps.common.serializers import DynamicFieldsModelSerializer
from apps.common.validators import validate_phone_number
from apps.institutes import services
from apps.institutes.constants import DocumentStatus
from apps.institutes.models import (
    Institute,
    InstituteDocument,
    InstituteGalleryImage,
    InstituteInvitation,
    InstituteLocation,
    InstituteMember,
)

User = get_user_model()


def active_municipalities():
    return Location.objects.filter(level=LocationLevel.MUNICIPALITY, is_active=True)



# registration (public)
class OwnerSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                lookup="iexact",
                message="A user with that email already exists.",
            )
        ]
    )
    full_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(
        max_length=25,
        required=False,
        validators=[
            validate_phone_number,
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with that phone number already exists.",
            ),
        ],
    )

    def validate_password(self, value):
        validate_password(value)
        return value


class LocationInputSerializer(serializers.Serializer):
    location = serializers.PrimaryKeyRelatedField(queryset=active_municipalities())
    address = serializers.CharField(max_length=255)
    map_url = serializers.URLField(required=False, allow_blank=True)
    contact_phone = serializers.CharField(
        max_length=25,
        required=False,
        allow_blank=True,
        validators=[validate_phone_number],
    )


class RegisterSerializer(DynamicFieldsModelSerializer):
    """Public registration. Role and status are never read from the payload."""

    owner = OwnerSerializer(write_only=True)
    locations = LocationInputSerializer(many=True, write_only=True, required=True, allow_empty=False)

    class Meta:
        model = Institute
        fields = (
            "id",
            "slug",
            "name",
            "type",
            "established_year",
            "description",
            "status",
            "owner",
            "locations",
        )
        read_only_fields = ("id", "slug", "status")

    def create(self, validated_data):
        return services.register(
            owner=validated_data.pop("owner"),
            locations=validated_data.pop("locations", []),
            institute_data=validated_data,
        )



# public pages
class PublicInstituteListSerializer(DynamicFieldsModelSerializer):
    location = serializers.SerializerMethodField()

    class Meta:
        model = Institute
        fields = ("id", "slug", "name", "type", "logo", "location")

    def get_location(self, obj):
        # locations are prefetched (active only, with their municipality / district / province)
        main = next((l for l in obj.locations.all() if l.is_main), None)
        if main is None:
            return None
        return {
            "municipality": main.location.name,
            "district": main.location.district.name,
            "province": main.location.province.name,
            "address": main.address,
            "map_url": main.map_url,
        }


class PublicInstituteDetailSerializer(PublicInstituteListSerializer):
    locations = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()

    class Meta(PublicInstituteListSerializer.Meta):
        fields = PublicInstituteListSerializer.Meta.fields + (
            "established_year",
            "description",
            "ceo_name",
            "ceo_message",
            "website",
            "contact_email",
            "contact_phone",
            "facebook_url",
            "linkedin_url",
            "locations",
            "gallery",
        )

    def get_locations(self, obj):
        return [
            {
                "municipality": l.location.name,
                "district": l.location.district.name,
                "province": l.location.province.name,
                "address": l.address,
                "map_url": l.map_url,
                "contact_phone": l.contact_phone,
                "is_main": l.is_main,
            }
            for l in obj.locations.all()
        ]

    def get_gallery(self, obj):
        return [{"image": i.image.url, "caption": i.caption} for i in obj.gallery.all()]


# ---------------------------------------------------------------- admin review


class ReasonSerializer(serializers.Serializer):
    reason = serializers.CharField()


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


# ---------------------------------------------------------------- portal (the institute's own staff)


class InstituteProfileSerializer(DynamicFieldsModelSerializer):
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
            "logo",
            "ceo_name",
            "ceo_message",
            "website",
            "contact_email",
            "contact_phone",
            "facebook_url",
            "linkedin_url",
        )
        read_only_fields = ("id", "slug", "status", "status_reason")

    def update(self, instance, validated_data):
        return services.update_profile(instance, **validated_data)


class InstituteLocationSerializer(DynamicFieldsModelSerializer):
    location = serializers.PrimaryKeyRelatedField(queryset=active_municipalities())
    municipality_name = serializers.CharField(source="location.name", read_only=True)
    district_name = serializers.CharField(source="location.district.name", read_only=True)
    province_name = serializers.CharField(source="location.province.name", read_only=True)

    class Meta:
        model = InstituteLocation
        fields = (
            "id",
            "location",
            "municipality_name",
            "district_name",
            "province_name",
            "address",
            "map_url",
            "contact_phone",
            "is_main",
            "is_active",
        )
        read_only_fields = ("id", "is_main", "is_active")

    def create(self, validated_data):
        return services.add_location(
            self.request.user.membership.institute, **validated_data
        )

    def update(self, instance, validated_data):
        return services.update_location(instance, **validated_data)


class InstituteDocumentSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = InstituteDocument
        fields = ("id", "name", "file", "status", "created_at")
        read_only_fields = ("id", "status", "created_at")
        extra_kwargs = {"file": {"write_only": True}}  # never echoed back

    def create(self, validated_data):
        return services.add_document(
            self.request.user.membership.institute, **validated_data
        )


class GalleryImageSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = InstituteGalleryImage
        fields = ("id", "image", "caption", "position")
        read_only_fields = ("id", "position")

    def create(self, validated_data):
        return services.add_gallery_image(
            self.request.user.membership.institute, **validated_data
        )


class GalleryReorderSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class StaffSerializer(DynamicFieldsModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = InstituteMember
        fields = ("id", "email", "full_name", "role", "created_at")


class InvitationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = InstituteInvitation
        fields = ("id", "email", "role", "status", "expires_at", "created_at")
        # the token is never returned
        read_only_fields = ("id", "role", "status", "expires_at", "created_at")

    def create(self, validated_data):
        return services.invite(
            institute=self.request.user.membership.institute,
            email=validated_data["email"],
            by=self.request.user,
        )


class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    full_name = serializers.CharField(max_length=150, write_only=True)
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return services.accept_invitation(**validated_data)

    def to_representation(self, instance):
        return {"email": instance.email}
