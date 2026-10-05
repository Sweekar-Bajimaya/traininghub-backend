from django.urls import include, path

app_name = "api_v1"

urlpatterns = [
    path("user/", include("apps.users.api.v1.urls.users")),
    path("locations/", include("apps.catalog.api.v1.urls.locations")),
    path("institutes/", include("apps.institutes.api.v1.urls.public")),
    path("institute/", include("apps.institutes.api.v1.urls.portal")),
    path("admin/", include("apps.institutes.api.v1.urls.admin")),
]
