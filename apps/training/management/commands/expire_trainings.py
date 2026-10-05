from django.core.management.base import BaseCommand

from apps.training import services


class Command(BaseCommand):
    help = "Set EXPIRED on approved or unpublished trainings whose end date has passed. Safe to run any time."

    def handle(self, *args, **options):
        count = services.expire_trainings()
        self.stdout.write(self.style.SUCCESS(f"Expired {count} training(s)"))
