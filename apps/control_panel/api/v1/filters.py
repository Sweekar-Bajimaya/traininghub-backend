import django_filters

from apps.common.models.category import Category
from apps.training.models import Training


class AdminCategoryFilter(django_filters.FilterSet):
    parent = django_filters.CharFilter(field_name="parent__slug")

    class Meta:
        model = Category
        fields = ("parent", "is_active")


class AdminTrainingFilter(django_filters.FilterSet):
    institute = django_filters.CharFilter(field_name="institute__slug")

    class Meta:
        model = Training
        fields = ("status", "mode", "institute")
