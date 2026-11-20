from django.conf import settings
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from apps.app_key import services


class DistributedKeyAuthentication(BasePermission):
    """Lets a request through when it comes from a signed-in user, from one of our own frontend
    origins, or carries the `App-Key` header of a `DistributedAppKey` (the keys handed to other
    clients, for example a mobile app or the frontend's server). Anything else is a 403.

    The origin check trusts the browser's `Origin` header, which a script outside a browser can
    set to anything: it keeps other websites out, it does not authenticate the caller. The key does."""

    message = "A valid App-Key header is required."

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return True
        if request.META.get("HTTP_ORIGIN") in settings.CORS_ALLOWED_ORIGINS:
            return True
        if services.is_valid_key(request.META.get("HTTP_APP_KEY")):
            return True
        # Raised here, not returned: DRF turns a refusal for an anonymous caller into a 401
        # "credentials were not provided", which hides that the missing piece is the key.
        raise PermissionDenied(self.message, code="app_key_required")
