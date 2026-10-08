import re

import django_filters
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F, Q
from django.utils import timezone

from apps.training.constants import SEARCH_CONFIG
from apps.training.models import Training

# the hub's own buckets: under 1 month, 1 to 3 months, 3 months or more
DURATION_BUCKETS = {
    "short": Q(duration_weeks__lt=4),
    "mid": Q(duration_weeks__gte=4, duration_weeks__lt=13),
    "long": Q(duration_weeks__gte=13),
}


def prefix_query(text):
    """'Pyth boot!' gives 'pyth:* & boot:*'. Only letters and digits survive, so user input can
    never break the raw tsquery."""
    words = re.findall(r"[^\W_]+", text.lower())[:8]
    return " & ".join(f"{word}:*" for word in words)


class TrainingFilter(django_filters.FilterSet):
    # a top-level id also finds the trainings of its sub-categories
    category = django_filters.NumberFilter(method="filter_category")
    sub_category = django_filters.NumberFilter(field_name="category_id")
    # an online training has no location, so a location filter excludes it
    province = django_filters.NumberFilter(
        field_name="institute_location__location__province_id"
    )
    district = django_filters.NumberFilter(
        field_name="institute_location__location__district_id"
    )
    municipality = django_filters.NumberFilter(field_name="institute_location__location_id")
    fee_min = django_filters.NumberFilter(field_name="fee_npr", lookup_expr="gte")
    fee_max = django_filters.NumberFilter(field_name="fee_npr", lookup_expr="lte")
    start_from = django_filters.DateFilter(field_name="start_date", lookup_expr="gte")
    start_to = django_filters.DateFilter(field_name="start_date", lookup_expr="lte")
    duration = django_filters.ChoiceFilter(
        choices=[(key, key) for key in DURATION_BUCKETS], method="filter_duration"
    )
    duration_weeks_min = django_filters.NumberFilter(
        field_name="duration_weeks", lookup_expr="gte"
    )
    duration_weeks_max = django_filters.NumberFilter(
        field_name="duration_weeks", lookup_expr="lte"
    )
    institute = django_filters.CharFilter(field_name="institute__slug")
    registration_open = django_filters.BooleanFilter(method="filter_registration_open")
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Training
        fields = ("mode", "level")

    def filter_category(self, queryset, name, value):
        return queryset.filter(Q(category_id=value) | Q(category__parent_id=value))

    def filter_duration(self, queryset, name, value):
        return queryset.filter(DURATION_BUCKETS[value])

    def filter_registration_open(self, queryset, name, value):
        """The deadline has not passed, or there is none and the training has not started."""
        if not value:
            return queryset
        today = timezone.localdate()
        return queryset.filter(
            Q(registration_deadline__gte=today)
            | Q(registration_deadline__isnull=True, start_date__gte=today)
        )

    def filter_search(self, queryset, name, value):
        query = prefix_query(value)
        if not query:
            return queryset
        search_query = SearchQuery(query, config=SEARCH_CONFIG, search_type="raw")
        # best match first; an explicit ?ordering= replaces this (OrderingFilter runs after)
        return (
            queryset.filter(search_vector=search_query)
            .annotate(rank=SearchRank(F("search_vector"), search_query))
            .order_by("-rank", "-published_at", "-pk")
        )



