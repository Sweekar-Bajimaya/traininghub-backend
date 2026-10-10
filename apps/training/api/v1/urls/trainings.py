from rest_framework import routers

from apps.training.api.v1 import views

app_name = "trainings"

router = routers.DefaultRouter()
router.register("", views.PublicTrainingViewSet, basename="training")

urlpatterns = router.urls
