from django.urls import path
from rest_framework import routers

from apps.institutes.api.v1 import views

app_name = "institutes_admin"

router = routers.DefaultRouter()
router.register("institutes", views.AdminInstituteViewSet, basename="admin-institute")

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
