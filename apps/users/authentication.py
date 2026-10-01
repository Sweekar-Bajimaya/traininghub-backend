from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class ActiveAccountJWTAuthentication(JWTAuthentication):
    """JWT authentication that treats a deactivated (suspended) account's
    still-valid token as anonymous on public views.

    simplejwt already rejects tokens of users with ``is_active=False``, but
    it does so on every view, including public ones. Institute staff and
    admins are the only users who log in, and the public site (browse
    trainings, send an enquiry) is called by the Next.js frontend with
    whatever token it has stored. A suspended institute's leftover token
    would therefore break browsing with a 401 instead of leaving it exactly
    as reachable as for an anonymous visitor.

    The check lives here instead of per-view ``authentication_classes``
    overrides so a future public view cannot forget it.
    """

    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except AuthenticationFailed as exc:
            if exc.get_codes() == "user_inactive" and self._view_is_public(request):
                return None
            raise

    @staticmethod
    def _view_is_public(request):
        parser_context = getattr(request, "parser_context", None) or {}
        view = parser_context.get("view")
        if view is None:
            return False
        permissions = view.get_permissions()
        return not permissions or any(isinstance(p, AllowAny) for p in permissions)
