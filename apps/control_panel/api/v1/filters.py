import django_filters
from django.db.models import Q

from apps.common.models.category import Category
from apps.enquiries.models import Enquiry
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


class AdminEnquiryFilter(django_filters.FilterSet):
    institute = django_filters.CharFilter(field_name="institute__slug")
    category = django_filters.CharFilter(method="filter_category")

    class Meta:
        model = Enquiry
        fields = ("status", "type", "institute")

        def filter_category(self, queryset, name, value):
            """The top-level category's slug: the training's own category or its parents."""
            return queryset.filter(
                Q(training__category__slug=value)
                | Q(training__category__parent__slug=value)
            )