from rest_framework import routers

from apps.training.api.v1 import views

app_name = "training_portal"

router = routers.DefaultRouter()
router.register("", views.PortalTrainingViewSet, basename="portal-training")

urlpatterns = router.urls
