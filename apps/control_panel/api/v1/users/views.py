from django.contrib.auth import get_user_model

from apps.common.viewsets import CreateListRetrieveUpdateViewSet
from apps.control_panel.api.v1.users.serializers import AdminSerializer
from apps.users.constants import Role
from apps.users.permissions import HasPlatformPermission

User = get_user_model()


class AdminViewSet(CreateListRetrieveUpdateViewSet):
    """Super Admin only. No DELETE: suspend through users/{id}/status/."""

    serializer_class = AdminSerializer
    permission_classes = [HasPlatformPermission]
    required_permission = "users.manage_admins"
    queryset = (
        User.objects.filter(role=Role.ADMIN)
        .prefetch_related("user_permissions")
        .order_by("-created_at", "-pk")
    )
    http_method_names = ["get", "post", "patch", "head", "options"]
