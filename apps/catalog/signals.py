from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.catalog.constants import TREE_CACHE_KEY
from apps.catalog.models import Location


@receiver([post_save, post_delete], sender=Location)
def clear_location_tree_cache(**kwargs):
    cache.delete(TREE_CACHE_KEY)
