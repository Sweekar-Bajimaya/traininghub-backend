from rest_framework.permissions import BasePermission

from apps.institutes.constants import MemberRole
from apps.users.constants import Role


class IsInstituteMember(BasePermission):
    """Institute staff who belong to an institute (owner or staff)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role == Role.INSTITUTE_STAFF
            and hasattr(user, "membership")  # one query per request, then cached on the user
        )


class IsInstituteOwner(IsInstituteMember):
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.membership.role == MemberRole.OWNER
        )


class InstituteScopedMixin:
    """Limit the queryset to the caller's institute, so another institute's rows are a 404."""

    def get_queryset(self):
        queryset = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return queryset.none()
        return queryset.filter(institute_id=self.request.user.membership.institute_id)
