import os

from django.db.models import Prefetch
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.viewsets import (
    CreateListDestroyViewSet,
    CreateListRetrieveUpdateViewSet,
    CreateListUpdateDestroyViewSet,
    CreateListViewSet,
    DestroyViewSet,
    ListViewSet,
    ReadOnlyViewSet,
)
from apps.institutes import services
from apps.institutes.api.v1.serializers import (
    AcceptInvitationSerializer,
    AdminDocumentSerializer,
    AdminInstituteSerializer,
    DocumentReviewSerializer,
    GalleryImageSerializer,
    GalleryReorderSerializer,
    InstituteDocumentSerializer,
    InstituteLocationSerializer,
    InstituteProfileSerializer,
    InvitationSerializer,
    PublicInstituteDetailSerializer,
    PublicInstituteListSerializer,
    ReasonSerializer,
    RegisterSerializer,
    StaffSerializer,
)
from apps.institutes.constants import InstituteStatus, MemberRole
from apps.institutes.models import (
    Institute,
    InstituteDocument,
    InstituteGalleryImage,
    InstituteInvitation,
    InstituteLocation,
    InstituteMember,
)
from apps.institutes.permissions import (
    InstituteScopedMixin,
    IsInstituteMember,
    IsInstituteOwner,
)
from apps.users.permissions import HasPlatformPermission


def private_file_response(document):
    """Stream a private document. Documents never get a URL."""
    return FileResponse(
        document.file.open("rb"),
        as_attachment=True,
        filename=os.path.basename(document.file.name),
    )


# ---------------------------------------------------------------- public


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "institute_register"


class AcceptInvitationView(CreateAPIView):
    serializer_class = AcceptInvitationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "invitation_accept"


class PublicInstituteViewSet(ReadOnlyViewSet):
    """Approved institutes only. A constant number of queries, whatever the page size."""

    permission_classes = []  # public
    lookup_field = "slug"
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ("type",)
    search_fields = ("name",)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PublicInstituteDetailSerializer
        return PublicInstituteListSerializer

    def get_queryset(self):
        return (
            Institute.objects.filter(status=InstituteStatus.APPROVED)
            .prefetch_related(
                Prefetch(
                    "locations",
                    queryset=InstituteLocation.objects.filter(is_active=True)
                    .select_related("location", "location__district", "location__province")
                    .order_by("-is_main", "pk"),
                ),
                Prefetch(
                    "gallery",
                    queryset=InstituteGalleryImage.objects.order_by("position", "pk"),
                ),
            )
            .order_by("name", "pk")
        )


# ---------------------------------------------------------------- admin console


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
            queryset=InstituteMember.objects.filter(role=MemberRole.OWNER).select_related("user"),
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
        return Response(self.get_serializer(self.get_queryset().get(pk=institute.pk)).data)

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
    queryset = InstituteDocument.objects.none()  # only for schema generation; patch() looks the row up itself

    def patch(self, request, institute_id, pk):
        document = get_object_or_404(InstituteDocument, pk=pk, institute_id=institute_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = services.review_document(
            document, status=serializer.validated_data["status"], by=request.user
        )
        return Response(AdminDocumentSerializer(document).data)


class AdminDocumentDownloadView(APIView):
    permission_classes = [HasPlatformPermission]
    required_permission = "users.manage_institutes"

    def get(self, request, institute_id, pk):
        return private_file_response(
            get_object_or_404(InstituteDocument, pk=pk, institute_id=institute_id)
        )


# ---------------------------------------------------------------- portal (the institute's own staff)


class InstituteProfileView(RetrieveUpdateAPIView):
    serializer_class = InstituteProfileSerializer
    permission_classes = [IsInstituteMember]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user.membership.institute


class ResubmitView(GenericAPIView):
    """Answer an info request, or re-apply after a rejection."""

    permission_classes = [IsInstituteMember]
    serializer_class = InstituteProfileSerializer

    def post(self, request):
        institute = services.resubmit(request.user.membership.institute)
        return Response(self.get_serializer(institute).data)


class PortalLocationViewSet(InstituteScopedMixin, CreateListRetrieveUpdateViewSet):
    serializer_class = InstituteLocationSerializer
    permission_classes = [IsInstituteMember]
    lookup_value_regex = r"[0-9]+"
    http_method_names = ["get", "post", "patch", "head", "options"]
    queryset = InstituteLocation.objects.select_related(
        "location", "location__district", "location__province"
    ).order_by("-is_main", "pk")

    @action(detail=True, methods=["post"], url_path="set-main")
    def set_main(self, request, pk=None):
        location = services.set_main_location(self.get_object())
        return Response(self.get_serializer(location).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        location = services.deactivate_location(self.get_object())
        return Response(self.get_serializer(location).data)


class PortalDocumentViewSet(InstituteScopedMixin, CreateListViewSet):
    serializer_class = InstituteDocumentSerializer
    permission_classes = [IsInstituteMember]
    queryset = InstituteDocument.objects.order_by("-created_at", "-pk")


class PortalDocumentDownloadView(APIView):
    permission_classes = [IsInstituteMember]

    def get(self, request, pk):
        return private_file_response(
            get_object_or_404(
                InstituteDocument,
                pk=pk,
                institute_id=request.user.membership.institute_id,
            )
        )


class PortalGalleryViewSet(InstituteScopedMixin, CreateListUpdateDestroyViewSet):
    serializer_class = GalleryImageSerializer
    permission_classes = [IsInstituteMember]
    lookup_value_regex = r"[0-9]+"
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    queryset = InstituteGalleryImage.objects.order_by("position", "pk")

    @action(detail=False, methods=["post"])
    def reorder(self, request):
        serializer = GalleryReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.reorder_gallery(
            request.user.membership.institute, serializer.validated_data["ids"]
        )
        return Response(self.get_serializer(self.get_queryset(), many=True).data)


class PortalStaffViewSet(InstituteScopedMixin, ListViewSet, DestroyViewSet):
    serializer_class = StaffSerializer
    permission_classes = [IsInstituteOwner]
    lookup_value_regex = r"[0-9]+"
    queryset = InstituteMember.objects.select_related("user").order_by("role", "pk")

    def perform_destroy(self, instance):
        services.remove_staff(instance, by=self.request.user)


class PortalInvitationViewSet(InstituteScopedMixin, CreateListDestroyViewSet):
    serializer_class = InvitationSerializer
    permission_classes = [IsInstituteOwner]
    lookup_value_regex = r"[0-9]+"
    queryset = InstituteInvitation.objects.order_by("-created_at", "-pk")

    def perform_destroy(self, instance):
        services.revoke_invitation(instance, by=self.request.user)
