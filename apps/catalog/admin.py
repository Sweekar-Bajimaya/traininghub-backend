from django.contrib import admin

from apps.catalog.models import Location


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
