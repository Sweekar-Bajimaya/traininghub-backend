from rest_framework import serializers

from apps.catalog.models import Location
from apps.common.serializers import DynamicFieldsModelSerializer


class LocationSerializer(DynamicFieldsModelSerializer):
    district_name = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ("id", "name", "level", "type", "parent", "province", "district",
                  "province_name", "district_name")

    # both read from select_related rows, so they add no queries
    def get_district_name(self, obj):
        return obj.district.name if obj.district_id else None

    def get_province_name(self, obj):
        return obj.province.name if obj.province_id else None
