from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    GenericAPIView,
    get_object_or_404,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.viewsets import ReadOnlyViewSet
from apps.control_panel.api.v1.institutes.serializers import (
    AdminDocumentSerializer,
    AdminInstituteSerializer,
    DocumentReviewSerializer,
    ReasonSerializer,
)
from apps.institutes import services
from apps.institutes.api.v1.views import private_file_response
from apps.institutes.constants import MemberRole
from apps.institutes.models import Institute, InstituteDocument, InstituteMember
from apps.users.permissions import HasPlatformPermission


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
        return self._review(request, services.approve, with_reason=False)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._review(request, services.reject, with_reason=True)

    @action(detail=True, methods=["post"], url_path="request-info")
    def request_info(self, request, pk=None):
        return self._review(request, services.request_info, with_reason=True)

    @action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        return self._review(request, services.suspend, with_reason=True)

    @action(detail=True, methods=["post"])
    def reinstate(self, request, pk=None):
        return self._review(request, services.reinstate, with_reason=False)


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
        document = services.review_document(
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
