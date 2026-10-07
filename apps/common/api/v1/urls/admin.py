from rest_framework import routers

from apps.common.api.v1 import views

app_name = "common_admin"
router = routers.SimpleRouter()
router.register("categories", views.AdminCategoryViewSet, basename="admin-category")
urlpatterns = router.urls
