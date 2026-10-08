from django.urls import include, path
from rest_framework import routers

from apps.control_panel.api.v1.users.views import AdminViewSet

app_name = "api_v1"

# Backward compatibility router for /user/admins/ (was in users app)
user_admin_router = routers.SimpleRouter()
user_admin_router.register("admins", AdminViewSet, basename="admin-user")

urlpatterns = [
    path("user/", include("apps.users.api.v1.urls.users")),
    path("locations/", include("apps.common.api.v1.urls.locations")),
    path("categories/", include("apps.common.api.v1.urls.categories")),
    path("trainings/", include("apps.training.api.v1.urls.trainings")),
    path("institutes/", include("apps.institutes.api.v1.urls.public")),
    # before "institute/" so the more specific prefix is matched first
    path("institute/trainings/", include("apps.training.api.v1.urls.portal")),
    path("institute/", include("apps.institutes.api.v1.urls.portal")),
    # admin routes consolidated under control_panel
    path("admin/", include("apps.control_panel.api.v1.urls")),
    # backward compatibility: user admin at /user/admins/ (was in users app)
    path("user/", include(user_admin_router.urls)),
]
