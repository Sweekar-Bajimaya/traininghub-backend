from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.common.viewsets import ListRetrieveUpdateViewSet
from apps.enquiries import services
from apps.enquiries.api.v1.filters import PortalEnquiryFilter
from apps.enquiries.api.v1.serializers import (
    EnquiryCreateSerializer,
    EnquiryNoteSerializer,
    PortalEnquiryListSerializer,
    PortalEnquirySerializer,
    VisitorEnquirySerializer,
    device_token_from,
)
from apps.enquiries.models import Enquiry, EnquiryNote
from apps.institutes.permissions import InstituteScopedMixin, IsInstituteMember


# public (no account: the device token is the only identity)
class EnquiryCreateView(CreateAPIView):
    serializer_class = EnquiryCreateSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "enquiry"  # per client IP; the per-phone limit is in the service


class MyEnquiriesView(ListAPIView):
    """The enquiries sent from this browser in the last 90 days."""

    serializer_class = VisitorEnquirySerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Enquiry.objects.none()
        return services.device_enquiries(device_token_from(self.request))


# portal (the institute's own staff and owner)
class PortalEnquiryViewSet(InstituteScopedMixin, ListRetrieveUpdateViewSet):
    """Another institute's enquiry is a 404. PATCH changes the status (any to any) and nothing
    else; ?status= and ?training= filter, ?q= searches name, phone and email."""

    permission_classes = [IsInstituteMember]
    lookup_value_regex = r"[0-9]+"
    http_method_names = ["get", "patch", "head", "options"]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PortalEnquiryFilter
    queryset = Enquiry.objects.select_related("training").order_by("-created_at", "-pk")

    def get_serializer_class(self):
        if self.action == "list":
            return PortalEnquiryListSerializer
        return PortalEnquirySerializer

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        """Counts for the tabs, the sidebar badge and the cards. The search and training filters
        apply, so the tab counts follow them like the prototype's; leave ?status= out."""
        return Response(services.summary(self.filter_queryset(self.get_queryset())))


class PortalEnquiryNoteView(ListCreateAPIView):
    """The internal notes of one enquiry, newest first."""

    serializer_class = EnquiryNoteSerializer
    permission_classes = [IsInstituteMember]
    pagination_class = None  # a few notes per enquiry, and the drawer shows them all

    @cached_property
    def enquiry(self):
        return get_object_or_404(
            Enquiry,
            pk=self.kwargs["enquiry_id"],
            institute_id=self.request.user.membership.institute_id,
        )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return EnquiryNote.objects.none()
        return EnquiryNote.objects.filter(enquiry=self.enquiry).select_related("author")

    def perform_create(self, serializer):
        serializer.save(enquiry=self.enquiry, author=self.request.user)
