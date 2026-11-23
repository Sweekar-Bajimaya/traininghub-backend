from django.core.management.base import BaseCommand

from apps.notification import services


class Command(BaseCommand):
    help = (
        "Delete read notifications older than 90 days and any older than 180. "
        "The once-only (dedupe) records are kept. Safe to run any time."
    )

    def handle(self, *args, **options):
        deleted = services.purge_old()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} notification(s)"))
