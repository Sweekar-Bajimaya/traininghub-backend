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
    list_select_related = ("training",)
    search_fields = (
        "question",
        "answer",
        "training__title",
    )
    list_filter = ("created_at", "training")
    raw_id_fields = ("training",) 
    ordering = ("-created_at",)
    list_per_page = 10
