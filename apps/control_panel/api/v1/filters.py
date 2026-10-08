import django_filters

from apps.training.models import Training


class AdminTrainingFilter(django_filters.FilterSet):
    institute = django_filters.NumberFilter(field_name="institute_id")

    class Meta:
        model = Training
        fields = ("status", "mode", "institute")
