from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from apps.common.viewsets import CustomModelViewSet, ReadOnlyViewSet
from apps.institutes.constants import InstituteStatus
from apps.institutes.permissions import InstituteScopedMixin, IsInstituteMember
from apps.training import services
from apps.training.api.v1.filters import TrainingFilter
from apps.training.api.v1.serializers import (
    CoverSerializer,
    PortalTrainingListSerializer,
    PortalTrainingSerializer,
    PublicTrainingDetailSerializer,
    PublicTrainingListSerializer,
)
from apps.training.constants import TrainingStatus
from apps.training.models import Training

# Child models are ordered in their Meta, so these prefetches come back in display order.
CHILDREN = ("sessions", "modules", "outcomes")


def with_content(queryset):
    """Everything the full training serializers read: the detail and contact rows, and the children."""
    return queryset.select_related("detail", "contact").prefetch_related(*CHILDREN)


# public
class PublicTrainingViewSet(ReadOnlyViewSet):
    """Approved trainings of approved institutes. Sort for the UI: Newest is
    ?ordering=-published_at, Upcoming is ?ordering=start_date, Price is ?ordering=fee_npr or
    -fee_npr; with ?search= and no ordering, the best match comes first."""

    permission_classes = []  # public
    lookup_field = "slug"
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = TrainingFilter
    ordering_fields = ("published_at", "start_date", "fee_npr")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PublicTrainingDetailSerializer
        return PublicTrainingListSerializer

    def get_queryset(self):
        queryset = Training.objects.filter(
            status=TrainingStatus.APPROVED, institute__status=InstituteStatus.APPROVED
        ).select_related(
            "institute",
            "category__parent",
            "institute_location__location__district",
            "institute_location__location__province",
            "institute__contact",
            "detail",  # the cards show the skills
        )
        if self.action == "retrieve":
            return queryset.select_related("contact").prefetch_related(*CHILDREN)
        return queryset.order_by("-published_at", "-pk")


# portal (the institute's own staff)
def transition(service):
    """A POST action that runs one workflow service and answers with the training.
    Assign it to the service's own name (`submit = transition(services.submit)`): that name
    becomes the URL, and DRF refuses to start if the two differ."""

    def run(self, request, pk=None):
        return self._respond(service(self.get_object(), by=request.user))

    # `action()` reads the name when it decorates, so set it first
    run.__name__ = service.__name__
    run.__doc__ = service.__doc__
    return action(detail=True, methods=["post"])(run)


class PortalTrainingViewSet(InstituteScopedMixin, CustomModelViewSet):
    """Staff and the owner can do everything here; another institute's training is a 404.
    PATCH on an approved or unpublished training sends it back to review."""

    permission_classes = [IsInstituteMember]
    lookup_value_regex = r"[0-9]+"
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("status",)
    queryset = Training.objects.select_related(
        "category__parent", "institute_location__location"
    ).order_by("-created_at", "-pk")

    def get_serializer_class(self):
        if self.action == "list":
            return PortalTrainingListSerializer
        if self.action == "cover":
            return CoverSerializer
        return PortalTrainingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()  # scoped to the caller's institute
        if self.action == "retrieve":
            return with_content(queryset)
        # Every other action either lists (cards need no children), counts, or hands the row to a
        # service that locks and re-reads it, so a prefetch here would be thrown away.
        return queryset

    def perform_destroy(self, instance):
        services.delete_training(instance)

    def _respond(self, training):
        # The services return a bare row: re-read it once, with the children, for the response.
        # Named serializer: `get_serializer()` would give `cover` its CoverSerializer.
        training = with_content(self.get_queryset()).get(pk=training.pk)
        return Response(
            PortalTrainingSerializer(
                training, context=self.get_serializer_context()
            ).data
        )

    # Workflow moves: one POST each, answering with the training. The attribute name is the URL.
    submit = transition(services.submit)
    withdraw = transition(services.withdraw)
    unpublish = transition(services.unpublish)
    republish = transition(services.republish)
    cancel = transition(services.cancel)

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def cover(self, request, pk=None):
        serializer = self.get_serializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._respond(serializer.save())

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        return Response(services.institute_counts(self.get_queryset()))
