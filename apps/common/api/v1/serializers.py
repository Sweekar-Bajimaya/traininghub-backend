from rest_framework import serializers

from apps.common.constants import LocationLevel
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
