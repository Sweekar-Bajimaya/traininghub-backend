from django.urls import path
from rest_framework import routers

from apps.common.api.v1 import views

app_name = "locations"

router = routers.DefaultRouter()
router.register("", views.LocationViewSet, basename="location")

urlpatterns = [
    path("tree/", views.LocationTreeView.as_view(), name="location-tree"),
] + router.urls
