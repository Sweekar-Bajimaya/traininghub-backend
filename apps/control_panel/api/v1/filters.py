import django_filters

from apps.common.models.category import Category
from apps.training.models import Training


class AdminCategoryFilter(django_filters.FilterSet):
    parent = django_filters.NumberFilter(field_name="parent_id")
    # ?top_level=true -> only main categories, ?top_level=false -> only sub-categories
    top_level = django_filters.BooleanFilter(field_name="parent", lookup_expr="isnull")

    class Meta:
        model = Category
        fields = ("parent", "top_level", "is_active")


class AdminTrainingFilter(django_filters.FilterSet):
    institute = django_filters.NumberFilter(field_name="institute_id")

    class Meta:
        model = Training
        fields = ("status", "mode", "institute")
