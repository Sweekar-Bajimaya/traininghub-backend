"""Run by django-q (`python manage.py qcluster`)."""

from django.db.models import Q

from apps.training import services
from apps.training.models import Training


def refresh_institute_trainings(institute_id):
    services.refresh_search_vectors(Training.objects.filter(institute_id=institute_id))


def refresh_category_trainings(category_id):
    services.refresh_search_vectors(
        Training.objects.filter(Q(category_id=category_id) | Q(category__parent_id=category_id))
    )


def refresh_location_trainings(institute_location_id):
    services.refresh_search_vectors(
        Training.objects.filter(institute_location_id=institute_location_id)
    )


def expire_trainings():
    """Schedule daily (Django admin > Django Q > Scheduled tasks)."""
    return services.expire_trainings()
