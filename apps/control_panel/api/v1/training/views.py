from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from apps.common.viewsets import ReadOnlyViewSet
from apps.control_panel.api.v1.filters import AdminTrainingFilter
from apps.control_panel.api.v1.training.serializers import (
    AdminTrainingListSerializer,
    AdminTrainingSerializer,
    TrainingReasonSerializer,
)
from apps.training import services
from apps.training.api.v1.views import CHILDREN
from apps.training.models import Training
from apps.users.permissions import HasPlatformPermission


class AdminTrainingViewSet(ReadOnlyViewSet):
    """Review queue: ?status=SUBMITTED."""

    permission_classes = [HasPlatformPermission]
    required_permission = "users.manage_trainings"
    lookup_value_regex = r"[0-9]+"
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = AdminTrainingFilter
    search_fields = ("title", "institute__name")
    queryset = Training.objects.select_related(
        "institute", "category__parent", "institute_location__location"
    ).order_by("-created_at", "-pk")

    def get_serializer_class(self):
        if self.action == "list":
            return AdminTrainingListSerializer
        if self.action in ("request_changes", "reject"):
            return TrainingReasonSerializer
        return AdminTrainingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            return queryset
        return queryset.prefetch_related(*CHILDREN)

    def _review(self, request, service, *, with_reason):
        kwargs = {}
        if with_reason:
            serializer = TrainingReasonSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            kwargs["reason"] = serializer.validated_data["reason"]
        training = service(self.get_object(), by=request.user, **kwargs)
        return Response(
            AdminTrainingSerializer(
                self.get_queryset().get(pk=training.pk),
                context=self.get_serializer_context(),
            ).data
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._review(request, services.approve, with_reason=False)

    @action(detail=True, methods=["post"], url_path="request-changes")
    def request_changes(self, request, pk=None):
        return self._review(request, services.request_changes, with_reason=True)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._review(request, services.reject, with_reason=True)
