from uuid import UUID

from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission

from apps.app_key.models import DistributedAppKey


class DistributedKeyAuthentication(BasePermission):
    """
    Allows access only to developers having this key.
    """

    def has_permission(self, request, view):
        """
        check 'APP_KEY  in request headers to give permission
        :param request: request object
        :param view:
        :return: boolean
        """
        if request.session.get('_auth_user_id') and str(request.user.id) == str(request.session.get('_auth_user_id')):
            return True
        
        if settings.DEBUG or request.META.get('HTTP_ORIGIN') == settings.TRAININGHUB_FRONTEND_URL:
            return True

        cached_http_app_key_list = cache.get('HTTP_APP_KEY_LIST')
        try:
            HTTP_APP_KEY = request.META.get('HTTP_APP_KEY')
            try:
                UUID(HTTP_APP_KEY, version=4)
            except Exception:
                return False
            if cached_http_app_key_list and HTTP_APP_KEY in cached_http_app_key_list:
                return True
            DistributedAppKey.objects.get(app_key__iexact=HTTP_APP_KEY)
            if cached_http_app_key_list and HTTP_APP_KEY not in cached_http_app_key_list:
                cached_http_app_key_list.append(HTTP_APP_KEY)
            if not cached_http_app_key_list:
                cache.set('HTTP_APP_KEY_LIST', [HTTP_APP_KEY])
            return True
        except (DistributedAppKey.DoesNotExist, ValidationError):
            return False
