from django.contrib import admin
from django.db.models import Prefetch

from apps.institutes.models import Institute, InstituteContact, InstituteSocialLink
from apps.users.constants import SocialPlatform


class InstituteContactInline(admin.StackedInline):
    model = InstituteContact
    extra = 0
    can_delete = False


class InstituteSocialLinkInline(admin.TabularInline):  # optional: shows the website
    model = InstituteSocialLink
    extra = 0


@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
        "status",
        "contact_person",
        "telephone_number",
        "website",
        "created_at",
    )
    list_filter = ("status", "type")
    search_fields = (
        "name",
        "slug",
        "contact__contact_person",
        "contact__contact_email",
    )
    ordering = ("-created_at", "-pk")
    inlines = [InstituteContactInline, InstituteSocialLinkInline]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("contact")
            .prefetch_related(
                Prefetch(
                    "social_links",
                    queryset=InstituteSocialLink.objects.filter(
                        platform=SocialPlatform.WEBSITE
                    ),
                    to_attr="website_links",
                )
            )
        )

    @admin.display(description="Contact person", ordering="contact__contact_person")
    def contact_person(self, obj):
        return obj.contact.contact_person

    @admin.display(description="Telephone", ordering="contact__telephone_number")
    def telephone_number(self, obj):
        return obj.contact.telephone_number

    @admin.display(description="Website")
    def website(self, obj):
        return obj.website_links[0].url if obj.website_links else "-"
