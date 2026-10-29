from django.urls import path
from rest_framework import routers

from apps.control_panel.api.v1 import views

app_name = "control_panel"

router = routers.DefaultRouter()
router.register("users/admins", views.AdminViewSet, basename="admin-user")
router.register("categories", views.AdminCategoryViewSet, basename="admin-category")
router.register("institutes", views.AdminInstituteViewSet, basename="admin-institute")
router.register("trainings", views.AdminTrainingViewSet, basename="admin-training")

urlpatterns = [
    path(
        "institutes/<int:institute_id>/documents/<int:pk>/",
        views.AdminDocumentView.as_view(),
        name="admin-document",
    ),
    path(
        "institutes/<int:institute_id>/documents/<int:pk>/download/",
        views.AdminDocumentDownloadView.as_view(),
        name="admin-document-download",
    ),
] + router.urls
