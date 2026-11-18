from django.contrib import admin
from apps.faq.models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "training",
        "question",
        "answer",
        "created_at",
    )
    search_fields = (
        "question",
        "answer",
        "training__title",
    )
    list_filter = ("created_at", "training")
    ordering = ("-created_at",)
    list_per_page = 10
