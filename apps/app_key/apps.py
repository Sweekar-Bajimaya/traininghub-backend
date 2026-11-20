from django.apps import AppConfig


class AppKeyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.app_key"

    def ready(self):
        from apps.app_key import signals  # noqa: F401
