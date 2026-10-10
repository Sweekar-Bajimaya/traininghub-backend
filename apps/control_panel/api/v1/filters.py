import django_filters

from apps.common.models.category import Category
from apps.training.models import Training


class AdminCategoryFilter(django_filters.FilterSet):
    parent = django_filters.NumberFilter(field_name="parent_id")

    class Meta:
        model = Category
        fields = ("parent", "is_active")


class AdminTrainingFilter(django_filters.FilterSet):
    institute = django_filters.NumberFilter(field_name="institute_id")

    class Meta:
        model = Training
        fields = ("status", "mode", "institute")
