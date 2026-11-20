from uuid import UUID

from django.core.cache import cache

from apps.app_key.models import DistributedAppKey

# A key that checked out is remembered this long, so a busy endpoint does not query the database on
# every request. Deleting the key forgets it at once (`signals.py`); the timeout is only a backstop.
CACHE_TTL_SECONDS = 300


def _cache_key(app_key):
    return f"app_key_valid_{app_key.hex}"


def parse_app_key(value):
    """The UUID in the `App-Key` header, or None when the header is missing or not a UUID.
    Dashes and letter case do not matter."""
    try:
        return UUID(value)
    except (AttributeError, TypeError, ValueError):
        return None


def is_valid_key(value):
    """True when `value` (the raw header) is the key of a `DistributedAppKey` row. Only a key that
    exists is cached, so guessing keys never fills the cache."""
    app_key = parse_app_key(value)
    if app_key is None:
        return False
    if cache.get(_cache_key(app_key)):
        return True
    if not DistributedAppKey.objects.filter(app_key=app_key).exists():
        return False
    cache.set(_cache_key(app_key), True, CACHE_TTL_SECONDS)
    return True


def forget_key(app_key):
    """Drop a key from the cache, called when its row is deleted so it stops working immediately."""
    parsed = parse_app_key(None if app_key is None else str(app_key))  # a row just saved holds a str
    if parsed is not None:
        cache.delete(_cache_key(parsed))
