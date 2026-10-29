from rest_framework import routers

from apps.institutes.api.v1 import views

app_name = "institutes_public"

router = routers.DefaultRouter()
router.register("", views.PublicInstituteViewSet, basename="institute")

urlpatterns = router.urls
