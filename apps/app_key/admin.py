from django.contrib import admin

# Register your models here.
from apps.app_key.models import DistributedAppKey


class DistributedAppKeyAdmin(admin.ModelAdmin):
    readonly_fields = ("app_key",)
    list_display = (
        "client_name",
        "app_key",
    )


admin.site.register(DistributedAppKey, DistributedAppKeyAdmin)
