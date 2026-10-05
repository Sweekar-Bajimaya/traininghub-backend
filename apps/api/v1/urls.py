from django.urls import include, path

app_name = "api_v1"

urlpatterns = [
    path("user/", include("apps.users.api.v1.urls.users")),
    path("locations/", include("apps.catalog.api.v1.urls.locations")),
    path("categories/", include("apps.catalog.api.v1.urls.categories")),
    path("trainings/", include("apps.training.api.v1.urls.trainings")),
    path("institutes/", include("apps.institutes.api.v1.urls.public")),
    # before "institute/" so the more specific prefix is matched first
    path("institute/trainings/", include("apps.training.api.v1.urls.portal")),
    path("institute/", include("apps.institutes.api.v1.urls.portal")),
    # one admin/ include per app; their routes do not overlap
    path("admin/", include("apps.institutes.api.v1.urls.admin")),
    path("admin/", include("apps.catalog.api.v1.urls.admin")),
    path("admin/", include("apps.training.api.v1.urls.admin")),
]
