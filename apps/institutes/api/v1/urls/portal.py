from django.urls import path
from rest_framework import routers

from apps.institutes.api.v1 import views

app_name = "institutes_portal"

router = routers.SimpleRouter()
router.register("locations", views.PortalLocationViewSet, basename="portal-location")
router.register("documents", views.PortalDocumentViewSet, basename="portal-document")
router.register("gallery", views.PortalGalleryViewSet, basename="portal-gallery")
router.register("staff", views.PortalStaffViewSet, basename="portal-staff")
router.register(
    "invitations", views.PortalInvitationViewSet, basename="portal-invitation"
)
router.register(
    "social-links", views.PortalSocialLinkViewSet, basename="portal-social-link"
)

# register/ and invitations/accept/ come before the router; the routers use numeric ids, so
# "accept" is never read as an id.
urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "register/send-otp/",
        views.RegisterSendOTPView.as_view(),
        name="register-send-otp",
    ),
    path(
        "register/verify-otp/",
        views.RegisterVerifyOTPView.as_view(),
        name="register-verify-otp",
    ),
    path(
        "invitations/accept/",
        views.AcceptInvitationView.as_view(),
        name="invitation-accept",
    ),
    path("profile/", views.InstituteProfileView.as_view(), name="profile"),
    path("resubmit/", views.ResubmitView.as_view(), name="resubmit"),
    path(
        "documents/<int:pk>/download/",
        views.PortalDocumentDownloadView.as_view(),
        name="document-download",
    ),
    path("contact/", views.PortalContactView.as_view(), name="contact"),
    path("ceo/", views.PortalCEOView.as_view(), name="ceo"),
] + router.urls
