from django.urls import include, path

app_name = "api_v1"

urlpatterns = [
    path("user/", include("apps.users.api.v1.urls.users")),
    path("locations/", include("apps.common.api.v1.urls.locations")),
    path("categories/", include("apps.common.api.v1.urls.categories")),
    path("trainings/", include("apps.training.api.v1.urls.trainings")),
    path("institutes/", include("apps.institutes.api.v1.urls.public")),
    path("enquiries/", include("apps.enquiries.api.v1.urls.public")),
    # before "institute/" so the more specific prefix is matched first
    path("institute/trainings/", include("apps.training.api.v1.urls.portal")),
    path("institute/enquiries/", include("apps.enquiries.api.v1.urls.portal")),
    path("institute/", include("apps.institutes.api.v1.urls.portal")),
    # every admin endpoint lives in the control panel: one include
    path("admin/", include("apps.control_panel.api.v1.urls")),
]
