from rest_framework import routers

from apps.catalog.api.v1 import views

app_name = "catalog_admin"
router = routers.SimpleRouter()
router.register("categories", views.AdminCategoryViewSet, basename="admin-category")
urlpatterns = router.urls
