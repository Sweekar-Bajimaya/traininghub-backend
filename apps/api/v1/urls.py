from django.urls import include, path

app_name = "api_v1"

urlpatterns = [
    path('user/', include('apps.users.api.v1.urls.users')),
    path("locations/", include("apps.catalog.api.v1.urls.locations")),
]
