from django.contrib import admin

from apps.training.models import Training


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    """Read-only: trainings change through the services, which keep the search vector and the
    review workflow."""

    list_display = ("title", "institute", "category", "mode", "status", "start_date")
    list_filter = ("status", "mode", "level")
    search_fields = ("title", "institute__name")
    list_select_related = ("institute", "category")
    exclude = ("search_vector",)
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
