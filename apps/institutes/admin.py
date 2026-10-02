from django.contrib import admin

from apps.institutes.models import Institute


@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "status", "created_at")
    list_filter = ("status", "type")
    search_fields = ("name", "slug")
    ordering = ("-created_at", "-pk")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False