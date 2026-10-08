from rest_framework import serializers

from apps.common.constants import LocationLevel
from apps.common import services
from apps.common.models.category import Category
from apps.common.models.location import Location
from apps.common.serializers import DynamicFieldsModelSerializer
from apps.common.validators import validate_phone_number


def active_municipalities():
    """Municipalities that may be selected by a domain-owned location record."""
    return Location.objects.filter(
        level=LocationLevel.MUNICIPALITY,
        is_active=True,
    )


class LocationInputSerializer(serializers.Serializer):
    """Shared input shape for a location selected from the reference-data tree."""

    location = serializers.PrimaryKeyRelatedField(queryset=active_municipalities())
    address = serializers.CharField(max_length=255)
    map_url = serializers.URLField(required=False, allow_blank=True)
    contact_phone = serializers.CharField(
        max_length=25,
        required=False,
        allow_blank=True,
        validators=[validate_phone_number],
    )


class LocationSerializer(DynamicFieldsModelSerializer):
    district_name = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = (
            "id",
            "name",
            "level",
            "type",
            "parent",
            "province",
            "district",
            "province_name",
            "district_name",
        )

    # both read from select_related rows, so they add no queries
    def get_district_name(self, obj):
        return obj.district.name if obj.district_id else None

    def get_province_name(self, obj):
        return obj.province.name if obj.province_id else None


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
        return services.create_category(**validated_data)

    def update(self, instance, validated_data):
        return services.update_category(instance, **validated_data)
