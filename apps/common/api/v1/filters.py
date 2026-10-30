import django_filters

from apps.common.models.location import Location


class LocationFilter(django_filters.FilterSet):
    # NumberFilter on the raw *_id column: the default ModelChoiceFilter would run an
    # extra query on every request just to check that the parent exists.
    parent = django_filters.NumberFilter(field_name="parent_id")
    province = django_filters.NumberFilter(field_name="province_id")
    district = django_filters.NumberFilter(field_name="district_id")

    class Meta:
        model = Location
        fields = ("level", "parent", "province", "district")
