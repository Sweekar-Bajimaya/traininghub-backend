from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.common.constants import LocationLevel
from apps.common.models.location import Location
from apps.common.serializers import DynamicFieldsModelSerializer
from apps.common.validators import validate_phone_number
from apps.institutes import services
from apps.institutes.constants import DocumentStatus
from apps.institutes.models import (
    Institute,
    InstituteCEO,
    InstituteContact,
    InstituteDocument,
    InstituteGalleryImage,
    InstituteInvitation,
    InstituteLocation,
    InstituteMember,
    InstituteSocialLink,
)
from apps.users.constants import SocialPlatform

User = get_user_model()


def active_municipalities():
    return Location.objects.filter(level=LocationLevel.MUNICIPALITY, is_active=True)


class InstituteContactSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = InstituteContact
        fields = ("contact_person", "contact_phone", "contact_email")


class InstituteCEOSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = InstituteCEO
        fields = ("name", "message", "photo", "linkedin_url")

        # used by PUT institute/ceo/ (create or replace)
        def update(self, instance, validated_data):
            return services.save_ceo(
                self.request.user.membership.institute, **validated_data
            )


class InstituteSocialLinkSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = InstituteSocialLink
        fields = ("id", "platform", "url", "label")
        read_only_fields = ("id",)

    def create(self, validated_data):
        return services.add_social_link(
            self.request.user.membership.institute, **validated_data
        )

    def update(self, instance, validated_data):
        return services.update_social_link(instance, **validated_data)


# registration (public)
class UserRegistrationSerializer(serializers.Serializer):
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


class InstituteRegistrationSerializer(DynamicFieldsModelSerializer):
    """Registration requires contact person + phone."""

    owner = UserRegistrationSerializer(write_only=True)
    locations = LocationInputSerializer(
        many=True, write_only=True, required=True, allow_empty=False
    )
    contact = InstituteContactSerializer(write_only=True)
    ceo = InstituteCEOSerializer(
        write_only=True, required=False, exclude_fields=("photo",)
    )
    social_links = InstituteSocialLinkSerializer(
        many=True, write_only=True, required=False
    )

    class Meta:
        model = Institute
        fields = (
            "id",
            "slug",
            "status",
            "name",
            "registration_number",
            "type",
            "established_year",
            "description",
            "owner",
            "locations",
            "contact",
            "ceo",
            "social_links",
        )
        read_only_fields = (
            "id",
            "slug",
            "status",
        )  # no logo: it's uploaded later through the portal

    def validate_social_links(self, value):
        platforms = [
            l["platform"] for l in value if l["platform"] != SocialPlatform.OTHER
        ]
        if len(platforms) != len(set(platforms)):
            raise serializers.ValidationError("Each platform can be added only once.")
        return value

    def create(self, validated_data):
        return services.register(
            owner=validated_data.pop("owner"),
            locations=validated_data.pop("locations"),
            contact=validated_data.pop("contact"),
            ceo=validated_data.pop("ceo", None),
            social_links=validated_data.pop("social_links", []),
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
    contact = InstituteContactSerializer(read_only=True, allow_null=True)
    # to hide the person's name publicly: InstituteContactSerializer(read_only=True, allow_null=True, exclude_fields=("contact_person",))
    ceo = InstituteCEOSerializer(read_only=True, allow_null=True)
    social_links = InstituteSocialLinkSerializer(many=True, read_only=True)
    class Meta(PublicInstituteListSerializer.Meta):

        fields = PublicInstituteListSerializer.Meta.fields + (
            "established_year",
            "description",
            "contact",
            "ceo",
            "social_links",
            "locations",
            "gallery",
        )


# admin review
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


class InstituteProfileSerializer(DynamicFieldsModelSerializer):
    """Institute Profile used for registration and profile view through portal."""

    contact = InstituteContactSerializer(read_only=True, allow_null=True)
    ceo = InstituteCEOSerializer(
        read_only=True, allow_null=True
    )  # allow_null: no CEO row → null, not a 500
    social_links = InstituteSocialLinkSerializer(many=True, read_only=True)

    class Meta:
        model = Institute
        fields = (
            "id",
            "slug",
            "name",
            "registration_number",
            "type",
            "status",
            "status_reason",
            "established_year",
            "description",
            "logo",
            "contact",
            "ceo",
            "social_links",
        )
        read_only_fields = (
            "id",
            "slug",
            "registration_number",
            "status",
            "status_reason",
        )

    def update(self, instance, validated_data):
        return services.update_profile(instance, **validated_data)  # unchanged


class InstituteLocationSerializer(DynamicFieldsModelSerializer):
    location = serializers.PrimaryKeyRelatedField(queryset=active_municipalities())
    municipality_name = serializers.CharField(source="location.name", read_only=True)
    district_name = serializers.CharField(
        source="location.district.name", read_only=True
    )
    province_name = serializers.CharField(
        source="location.province.name", read_only=True
    )

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
