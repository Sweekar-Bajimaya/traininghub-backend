from django.urls import path
from rest_framework import routers

from apps.enquiries.api.v1 import views

app_name = "enquiries_portal"

router = routers.DefaultRouter()
router.register("", views.PortalEnquiryViewSet, basename="portal-enquiry")

# the notes path is not a router route, so it goes first; the router's ids are numeric
urlpatterns = [
    path(
        "<int:enquiry_id>/notes/",
        views.PortalEnquiryNoteView.as_view(),
        name="portal-enquiry-notes",
    ),
] + router.urls
