from django.urls import path
from rest_framework import routers

from apps.users.api.v1 import views

app_name = "users"

router = routers.DefaultRouter()
router.register("admins", views.AdminViewSet, basename="admin")

urlpatterns = [
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/refresh/", views.RefreshView.as_view(), name="refresh"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("me/", views.MeView.as_view(), name="me"),
    path("me/password/", views.PasswordChangeView.as_view(), name="me-password"),
    path("users/<int:pk>/status/", views.UserStatusView.as_view(), name="user-status"),
]
urlpatterns += router.urls
