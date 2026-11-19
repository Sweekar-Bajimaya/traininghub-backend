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


class HasAnyPlatformPermission(IsPlatformAdmin):
    """Set `required_permissions = ("users.manage_a", "users.manage_b")` on the view: an admin passes
    with at least one. For a view that answers in sections and leaves out the ones the caller
    may not see."""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and any(
            request.user.has_perm(permission) for permission in view.required_permissions
        )


class IsInstituteStaff(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role == Role.INSTITUTE_STAFF)
