from django.contrib import admin

from apps.common.models.category import Category
from apps.common.models.location import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "type", "parent", "is_active")
    list_filter = ("level", "type", "is_active")
    search_fields = ("name",)
    list_select_related = ("parent",)
    ordering = ("level", "name")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Read-only: categories change through the admin API, which checks the two-level rule
    and queues the search refresh."""

    list_display = ("name", "parent", "icon", "hue", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_select_related = ("parent",)
    ordering = ("name",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
