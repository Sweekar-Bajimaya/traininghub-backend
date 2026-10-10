from django.contrib import admin

from apps.enquiries.models import Enquiry


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    """Read-only: enquiries change through the services, which guard the seats and the limits."""

    list_display = ("name", "training", "institute", "type", "status", "created_at")
    list_filter = ("status", "type")
    search_fields = ("name", "phone", "training__title", "institute__name")
    list_select_related = ("training", "institute")
    exclude = ("device_token",)
    ordering = ("-created_at", "-pk")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
