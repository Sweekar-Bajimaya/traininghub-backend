from rest_framework import routers

from apps.notification.api.v1 import views

app_name = "notifications"

router = routers.DefaultRouter()
router.register("", views.NotificationViewset, basename="notification")

urlpatterns = router.urls
