import django_filters
from django.db.models import Q

from apps.enquiries.models import Enquiry


class PortalEnquiryFilter(django_filters.FilterSet):
    # not django-filter's default ModelChoiceFilter: that checks the row with a query per request
    training = django_filters.NumberFilter(field_name="training_id")
    q = django_filters.CharFilter(method="filter_q")

    class Meta:
        model = Enquiry
        fields = ("status",)

    def filter_q(self, queryset, name, value):
        """The portal's search box: name, phone or email, anywhere in the text."""
        value = value.strip()
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(phone__icontains=value)
            | Q(email__icontains=value)
        )
