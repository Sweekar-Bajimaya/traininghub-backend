from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.models.category import Category
from apps.common.viewsets import CreateListRetrieveUpdateViewSet, ReadOnlyViewSet
from apps.control_panel.api.v1.filters import AdminCategoryFilter, AdminTrainingFilter
from apps.control_panel.api.v1.serializers import (
    AdminCategorySerializer,
    AdminDocumentSerializer,
    AdminInstituteSerializer,
    AdminSerializer,
    AdminTrainingListSerializer,
    AdminTrainingSerializer,
    DocumentReviewSerializer,
    ReasonSerializer,
)
from apps.institutes import services as institute_services
from apps.institutes.api.v1.views import private_file_response
from apps.institutes.constants import MemberRole
from apps.institutes.models import Institute, InstituteDocument, InstituteMember
from apps.training import services as training_services
from apps.training.api.v1.views import with_content
from apps.training.models import Training
from apps.users.constants import Role
from apps.users.permissions import HasPlatformPermission

User = get_user_model()


# admins
class AdminViewSet(CreateListRetrieveUpdateViewSet):
    """Super Admin only. No DELETE: suspend through user/users/{id}/status/."""

    serializer_class = AdminSerializer
    permission_classes = [HasPlatformPermission]
    required_permission = "users.manage_admins"
    queryset = (
        User.objects.filter(role=Role.ADMIN)
        .prefetch_related("user_permissions")
        .order_by("-created_at", "-pk")
    )
    http_method_names = ["get", "post", "patch", "head", "options"]


# categories
class AdminCategoryViewSet(CreateListRetrieveUpdateViewSet):
    """No DELETE: deactivate with PATCH {"is_active": false}."""

    serializer_class = AdminCategorySerializer
    permission_classes = [HasPlatformPermission]
    required_permission = "users.manage_categories"
    lookup_value_regex = r"[0-9]+"
    http_method_names = ["get", "post", "patch", "head", "options"]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = AdminCategoryFilter
    search_fields = ("name",)
    queryset = Category.objects.select_related("parent").order_by("name", "pk")


# institutes
class AdminInstituteViewSet(ReadOnlyViewSet):
    serializer_class = AdminInstituteSerializer
    permission_classes = [HasPlatformPermission]
    required_permission = "users.manage_institutes"
    lookup_value_regex = r"[0-9]+"
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ("status", "type")
    search_fields = ("name",)
    queryset = Institute.objects.prefetch_related(
        "documents",
        Prefetch(
            "members",
            queryset=InstituteMember.objects.filter(
                role=MemberRole.OWNER
            ).select_related("user"),
            to_attr="owner_members",
        ),
    ).order_by("-created_at", "-pk")

    def _review(self, request, service, *, with_reason):
        kwargs = {}
        if with_reason:
            serializer = ReasonSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            kwargs["reason"] = serializer.validated_data["reason"]
        institute = service(self.get_object(), by=request.user, **kwargs)
        # re-read through the viewset queryset so documents and owner are prefetched
        return Response(
            self.get_serializer(self.get_queryset().get(pk=institute.pk)).data
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._review(request, institute_services.approve, with_reason=False)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._review(request, institute_services.reject, with_reason=True)

    @action(detail=True, methods=["post"], url_path="request-info")
    def request_info(self, request, pk=None):
        return self._review(request, institute_services.request_info, with_reason=True)

    @action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        return self._review(request, institute_services.suspend, with_reason=True)

    @action(detail=True, methods=["post"])
    def reinstate(self, request, pk=None):
        return self._review(request, institute_services.reinstate, with_reason=False)


class AdminDocumentView(GenericAPIView):
    permission_classes = [HasPlatformPermission]
    required_permission = "users.manage_institutes"
    serializer_class = DocumentReviewSerializer
    queryset = (
        InstituteDocument.objects.none()
    )  # only for schema generation; patch() looks the row up itself

    def patch(self, request, institute_id, pk):
        document = get_object_or_404(
            InstituteDocument, pk=pk, institute_id=institute_id
        )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = institute_services.review_document(
            document, status=serializer.validated_data["status"], by=request.user
        )
        return Response(
            AdminDocumentSerializer(
                document, context=self.get_serializer_context()
            ).data
        )


class AdminDocumentDownloadView(APIView):
    permission_classes = [HasPlatformPermission]
    required_permission = "users.manage_institutes"

    def get(self, request, institute_id, pk):
        return private_file_response(
            get_object_or_404(InstituteDocument, pk=pk, institute_id=institute_id)
        )


# trainings
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
            return ReasonSerializer
        return AdminTrainingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            return queryset
        return with_content(queryset)

    def _review(self, request, service, *, with_reason):
        kwargs = {}
        if with_reason:
            serializer = ReasonSerializer(data=request.data)
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
        return self._review(request, training_services.approve, with_reason=False)

    @action(detail=True, methods=["post"], url_path="request-changes")
    def request_changes(self, request, pk=None):
        return self._review(
            request, training_services.request_changes, with_reason=True
        )

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._review(request, training_services.reject, with_reason=True)
