import django_filters

from apps.catalog.models import Category, Location


class LocationFilter(django_filters.FilterSet):
    # NumberFilter on the raw *_id column: the default ModelChoiceFilter would run an
    # extra query on every request just to check that the parent exists.
    parent = django_filters.NumberFilter(field_name="parent_id")
    province = django_filters.NumberFilter(field_name="province_id")
    district = django_filters.NumberFilter(field_name="district_id")

    class Meta:
        model = Location
        fields = ("level", "parent", "province", "district")


class AdminCategoryFilter(django_filters.FilterSet):
    parent = django_filters.NumberFilter(field_name="parent_id")

    class Meta:
        model = Category
        fields = ("parent", "is_active")
