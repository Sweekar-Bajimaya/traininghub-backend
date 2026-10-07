from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.common.constants import CATEGORY_TREE_CACHE_KEY, TREE_CACHE_KEY
from apps.common.models.category import Category
from apps.common.models.location import Location


@receiver([post_save, post_delete], sender=Location)
def clear_location_tree_cache(**kwargs):
    cache.delete(TREE_CACHE_KEY)

@receiver([post_save, post_delete], sender=Category)
def clear_category_tree_cache(**kwargs):
    cache.delete(CATEGORY_TREE_CACHE_KEY)