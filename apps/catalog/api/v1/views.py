from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.api.v1.filters import AdminCategoryFilter, LocationFilter
from apps.catalog.api.v1.serializers import AdminCategorySerializer, LocationSerializer
from apps.catalog.constants import CATEGORY_TREE_CACHE_KEY, TREE_CACHE_KEY
from apps.catalog.models import Category, Location
from apps.common.viewsets import CreateListRetrieveUpdateViewSet, ReadOnlyViewSet
from apps.users.permissions import HasPlatformPermission


class LocationViewSet(ReadOnlyViewSet):
    """Dependent selects: GET locations/?level=DISTRICT&parent=<province id>."""

    serializer_class = LocationSerializer
    permission_classes = []  # public
    pagination_class = None  # at most ~850 small rows
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = LocationFilter
    search_fields = ("name",)
    lookup_value_regex = (
        r"[0-9]+"  # detail URLs only match numbers, so "tree/" is never an id
    )
    queryset = (
        Location.objects.filter(is_active=True)
        .select_related("district", "province")  # one query for the whole list
        .order_by("name", "pk")
    )


def build_tree():
    rows = list(
        Location.objects.filter(is_active=True)
        .order_by("name", "pk")
        .values("id", "name", "level", "type", "parent_id")
    )
    nodes = {r["id"]: {**r, "children": []} for r in rows}
    roots = []
    for r in rows:
        node = nodes[r["id"]]
        if r["parent_id"] is None:
            roots.append(node)
        elif r["parent_id"] in nodes:  # skip children of a retired parent
            nodes[r["parent_id"]]["children"].append(node)
    return roots


class LocationTreeView(APIView):
    """Province > district > municipality, cached until a location changes."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(cache.get_or_set(TREE_CACHE_KEY, build_tree, timeout=None))


def build_category_tree():
    rows = list(
        Category.objects.filter(is_active=True)
        .order_by("name", "pk")
        .values("id", "name", "slug", "icon", "hue", "parent_id")
    )
    nodes = {r["id"]: {**r, "children": []} for r in rows}
    roots = []
    for r in rows:
        node = nodes[r["id"]]
        if r["parent_id"] is None:
            roots.append(node)
        elif r["parent_id"] in nodes:  # skip children of a retired parent
            nodes[r["parent_id"]]["children"].append(node)
    return roots


class CategoryTreeView(APIView):
    """Category > sub-category, cached until a category changes."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            cache.get_or_set(CATEGORY_TREE_CACHE_KEY, build_category_tree, timeout=None)
        )


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
