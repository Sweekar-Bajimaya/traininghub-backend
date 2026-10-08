from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.common.throttling import IdentityScopedRateThrottle
from apps.common.viewsets import ActionAPIView, CreateListRetrieveUpdateViewSet
from apps.control_panel.api.v1.users.serializers import AdminSerializer
from apps.users.api.v1.serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    ProfileSerializer,
    SendOTPSerializer,
    UpdateStatusSerializer,
    VerifyOTPSerializer,
)
from apps.users.constants import Role
from apps.users.permissions import HasPlatformPermission

User = get_user_model()


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "login"


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "token_refresh"


class LogoutView(TokenBlacklistView):
    throttle_scope = "token_refresh"


class MeView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user


class PasswordChangeView(UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    http_method_names = ["put"]

    def get_object(self):
        return self.request.user


class UserStatusView(UpdateAPIView):
    permission_classes = [HasPlatformPermission]
    required_permission = "users.manage_account_status"
    queryset = User.objects.all()
    serializer_class = UpdateStatusSerializer
    http_method_names = ["patch"]


class SendOTPView(ActionAPIView):
    """Emails a one-time code to an address that has an account (password reset)."""

    serializer_class = SendOTPSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [IdentityScopedRateThrottle]
    throttle_scope = "otp"


class VerifyOTPView(ActionAPIView):
    """Checks a code without using it up."""

    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [IdentityScopedRateThrottle]
    throttle_scope = "otp"
