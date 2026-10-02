from django.urls import path
from rest_framework import routers

from apps.catalog.api.v1 import views

app_name = "locations"

# SimpleRouter, not DefaultRouter: DefaultRouter adds an API-root view at "" that would
# compete with the list route, because this module is mounted under its own prefix.
router = routers.SimpleRouter()
router.register("", views.LocationViewSet, basename="location")

urlpatterns = [
    path("tree/", views.LocationTreeView.as_view(), name="location-tree"),
] + router.urls
