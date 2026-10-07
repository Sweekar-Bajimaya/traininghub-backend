from django.urls import path

from apps.common.api.v1 import views

app_name = "categories"
urlpatterns = [path("", views.CategoryTreeView.as_view(), name="category-tree")]
