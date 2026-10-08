import hashlib

from rest_framework.throttling import ScopedRateThrottle


class IdentityScopedRateThrottle(ScopedRateThrottle):
    """ScopedRateThrottle, but keyed on the *account being targeted*
    instead of client IP.

    Why this exists: the frontend is being rebuilt as a Next.js
    Backend-For-Frontend, so every request Django sees will arrive from
    Next's server IP, not the end user's browser. Plain ScopedRateThrottle
    keys anonymous requests on `get_ident(request)` (the request IP by
    default) - under a BFF that throttles *all* users behind the BFF
    together as one bucket, not the one account actually being guessed
    against. Keying on the submitted email (falling back to the
    authenticated user's pk, then a hash of a submitted refresh token, then
    finally IP as a last resort) keeps the limit scoped to the credential
    actually under attack.

    Views opt in with `throttle_scope = "<scope name>"` - a view with no
    `throttle_scope` set is not throttled by this class at all (inherited
    from ScopedRateThrottle.allow_request).
    """

    def get_cache_key(self, request, view):
        ident = self._get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}

    def _get_ident(self, request):
        if request.user and request.user.is_authenticated:
            return request.user.pk

        data = request.data if isinstance(request.data, dict) else {}

        email = data.get("email")
        if email:
            return str(email).strip().lower()

        # token/refresh/ has no email in its body - key on the refresh
        # token itself (hashed so the cache key doesn't store the raw
        # token value) so refresh-abuse is scoped per session, not per IP.
        refresh = data.get("refresh")
        if refresh:
            return hashlib.sha256(str(refresh).encode()).hexdigest()

        return self.get_ident(request)
