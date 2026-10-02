from django.apps import AppConfig


class CatalogConfig(AppConfig):
    name = 'apps.catalog'

    def ready(self):
        from apps.catalog import signals  # noqa: F401  (registers the cache-clearing receivers)
