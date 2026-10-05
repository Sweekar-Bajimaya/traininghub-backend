from django.urls import path

from apps.catalog.api.v1 import views

app_name = "categories"
urlpatterns = [path("", views.CategoryTreeView.as_view(), name="category-tree")]
