from django.db.models.signals import post_delete
from django.dispatch import receiver

from apps.app_key import services
from apps.app_key.models import DistributedAppKey


@receiver(post_delete, sender=DistributedAppKey)
def forget_deleted_key(instance, **kwargs):
    """A deleted key must stop working now, not when its cache entry times out."""
    services.forget_key(instance.app_key)
