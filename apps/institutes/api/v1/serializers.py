from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.common.api.v1.serializers import (
    LocationInputSerializer,
    active_municipalities,
)
from apps.common.serializers import DynamicFieldsModelSerializer
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
from apps.users.api.v1.serializers import (
    OTPField,
    UserRegistrationSerializer,
)
from apps.users.constants import SocialPlatform

User = get_user_model()


class InstituteContactSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = InstituteContact
        fields = ("contact_person", "contact_phone", "contact_email")


class InstituteCEOSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = InstituteCEO
        fields = ("name", "message", "photo", "linkedin_url")

    def update(self, instance, validated_data):
        # used by PUT institute/ceo/ (create or replace); the instance may not be saved yet
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


class InstituteRegistrationSerializer(DynamicFieldsModelSerializer):
    """Registration requires contact person + phone. `owner.email` and `owner.password` are the
    institute's login; the email is verified with `otp`, the code sent to it by
    RegistrationOTPSerializer."""

    otp = OTPField()
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
            "otp",
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
            otp=validated_data.pop("otp"),
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
    locations = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()

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

    def get_locations(self, obj):
        # prefetched: active only, with municipality / district / province, main office first
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


class InstituteProfileSerializer(DynamicFieldsModelSerializer):
    """The institute's own profile in the portal. Only its own columns are edited here; the
    contact person, CEO and social links are shown and edited through their own endpoints."""

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
