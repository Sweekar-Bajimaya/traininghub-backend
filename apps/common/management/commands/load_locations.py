import json
from pathlib import Path

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.common.constants import TREE_CACHE_KEY, LocationLevel
from apps.common.models.location import Location

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# An unknown category raises Keyerror on purpose, so data fails loudly
TYPE_MAP = {
    "Metropolitan City": "METROPOLITAN",
    "Sub-Metropolitan City": "SUB_METROPOLITAN",
    "Municipality": "MUNICIPALITY",
    "Rural Municipality": "RURAL_MUNICIPALITY",
    "Gaunpalika": "RURAL_MUNICIPALITY",  # 2 rows; Gaunpalika = rural municipality
}


class Command(BaseCommand):
    help = "Load or update the Nepal province / district / municipality list. Safe to run twice."

    @transaction.atomic
    def handle(self, *args, **options):
        read = lambda name: json.loads((DATA_DIR / name).read_text(encoding="utf-8"))
        P, D, M = (
            LocationLevel.PROVINCE,
            LocationLevel.DISTRICT,
            LocationLevel.MUNICIPALITY,
        )

        self._upsert(
            [
                dict(code=p["id"], name=p["name"].strip(), level=P)
                for p in read("provinces.json")
            ]
        )
        province = dict(Location.objects.filter(level=P).values_list("code", "pk"))

        self._upsert(
            [
                dict(
                    code=d["id"],
                    name=d["name"].strip(),
                    level=D,
                    parent_id=province[d["province"]],
                    province_id=province[d["province"]],
                )
                for d in read("districts.json")
            ]
        )
        district = {
            c: (pk, prov)
            for c, pk, prov in Location.objects.filter(level=D).values_list(
                "code", "pk", "province_id"
            )
        }

        self._upsert(
            [
                dict(
                    code=m["id"],
                    name=m["name"].strip(),
                    level=M,
                    type=TYPE_MAP[m["category"]],
                    parent_id=district[m["district"]][0],
                    district_id=district[m["district"]][0],
                    province_id=district[m["district"]][1],
                )
                for m in read("cities.json")
            ]
        )

        # bulk_create sends no signals, so clear the cached tree ourselves
        transaction.on_commit(lambda: cache.delete(TREE_CACHE_KEY))
        counts = {lvl: Location.objects.filter(level=lvl).count() for lvl in (P, D, M)}
        self.stdout.write(self.style.SUCCESS(f"Locations loaded: {counts}"))

    @staticmethod
    def _upsert(rows):
        Location.objects.bulk_create(
            [Location(**r) for r in rows],
            update_conflicts=True,
            unique_fields=["level", "code"],
            update_fields=[
                "name",
                "type",
                "parent",
                "province",
                "district",
                "modified_at",
            ],
        )
