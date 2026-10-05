from rest_framework import routers

from apps.training.api.v1 import views

app_name = "training_admin"

router = routers.SimpleRouter()
router.register("trainings", views.AdminTrainingViewSet, basename="admin-training")

urlpatterns = router.urls
