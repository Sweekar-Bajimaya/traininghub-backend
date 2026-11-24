from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.viewsets import ListViewSet
from apps.notification import services
from apps.notification.api.v1.serializers import NotificationSerializer
from apps.notification.models import Notification


class NotificationViewset(ListViewSet):
    """The signed-in user's own inbox (institute staff and admins alike). Another user's row is
    a 404. `?unread=true` keeps the unread ones."""

    serializer_class = NotificationSerializer
    lookup_value_regex = r"[0-9]+"
    throttle_scope = "notifications"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        queryset = Notification.objects.filter(recipient=self.request.user).order_by(
            "-created_at", "-pk"
        )
        if self.request.query_params.get("unread", "").lower() in ("1", "true"):
            queryset = queryset.filter(read_at__isnull=True)
        return queryset

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        return Response({"count": services.unread_count(request.user)})

    @action(detail=False, methods=["post"], url_path="read-all")
    def read_all(self, request):
        return Response({"updated": services.mark_all_read(request.user)})

    @action(detail=True, methods=["post"], url_path="read")
    def read(self, request, pk=None):
        notification = self.get_object()  # 404 for someone else's row
        services.mark_read(notification)
        notification.refresh_from_db()
        return Response(self.get_serializer(notification).data)