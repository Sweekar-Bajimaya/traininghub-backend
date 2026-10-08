from django.urls import include, path
from rest_framework import routers

from apps.common.api.v1.views import AdminCategoryViewSet
from apps.control_panel.api.v1.users.views import AdminViewSet
from apps.control_panel.api.v1.institutes.views import (
    AdminInstituteViewSet,
    AdminDocumentView,
    AdminDocumentDownloadView,
)
from apps.control_panel.api.v1.training.views import AdminTrainingViewSet

app_name = "control_panel"

router = routers.SimpleRouter()
router.register("categories", AdminCategoryViewSet, basename="admin-category")
router.register("users/admins", AdminViewSet, basename="admin-user")
router.register("institutes", AdminInstituteViewSet, basename="admin-institute")
router.register("trainings", AdminTrainingViewSet, basename="admin-training")

urlpatterns = [
    path(
        "institutes/<int:institute_id>/documents/<int:pk>/",
        AdminDocumentView.as_view(),
        name="admin-document",
    ),
    path(
        "institutes/<int:institute_id>/documents/<int:pk>/download/",
        AdminDocumentDownloadView.as_view(),
        name="admin-document-download",
    ),
] + router.urls