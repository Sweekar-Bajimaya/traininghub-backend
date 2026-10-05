from rest_framework.permissions import BasePermission

from apps.users.constants import Role


class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.is_platform_admin)


class HasPlatformPermission(IsPlatformAdmin):
    """Set `required_permission = "users.manage_enquiries"` on the view."""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_perm(
            view.required_permission
        )


class IsInstituteStaff(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role == Role.INSTITUTE_STAFF)
