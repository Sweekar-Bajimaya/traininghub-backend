import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.common.models.category import Category


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "categories.json"


class Command(BaseCommand):
    help = "Load the starter categories (the UI's list). Safe to run twice."

    @transaction.atomic
    def handle(self, *args, **options):
        for entry in json.loads(DATA_FILE.read_text(encoding="utf-8")):
            top, _ = Category.objects.get_or_create(
                name=entry["name"],
                parent=None,
                defaults={"icon": entry["icon"], "hue": entry["hue"]},
            )
            for child in entry["children"]:
                Category.objects.get_or_create(name=child, parent=top)
        self.stdout.write(self.style.SUCCESS(f"Categories: {Category.objects.count()}"))
