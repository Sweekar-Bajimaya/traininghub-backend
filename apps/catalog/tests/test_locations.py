from io import StringIO

from django.core.cache import cache
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.db.models import F
from django.test import TestCase
from rest_framework.test import APITestCase

from apps.catalog.constants import TREE_CACHE_KEY, LocationLevel, MunicipalityType
from apps.catalog.models import Location

P, D, M = LocationLevel.PROVINCE, LocationLevel.DISTRICT, LocationLevel.MUNICIPALITY
LOADED = {P: 7, D: 77, M: 752}
LIST_URL = "/api/v1/locations/"
TREE_URL = "/api/v1/locations/tree/"


def load():
    call_command("load_locations", stdout=StringIO())


def level_counts():
    return {level: Location.objects.filter(level=level).count() for level in (P, D, M)}


class LocationModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.province = Location.objects.create(code=1, name="Province A", level=P)
        cls.district = Location.objects.create(code=1, name="District A", level=D, parent=cls.province)
        cls.municipality = Location.objects.create(
            code=1, name="Municipality A", level=M, parent=cls.district,
            type=MunicipalityType.MUNICIPALITY,
        )

    def test_save_derives_ancestors(self):
        self.assertEqual(self.district.province_id, self.province.pk)
        self.assertIsNone(self.district.district_id)
        self.assertEqual(self.municipality.district_id, self.district.pk)
        self.assertEqual(self.municipality.province_id, self.province.pk)

    def test_province_cannot_have_a_parent(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Location.objects.create(code=2, name="Province B", level=P, parent=self.province)

    def test_municipality_must_sit_under_a_district(self):
        # Under a province, save() derives province=None, which the shape check rejects.
        with self.assertRaises(IntegrityError), transaction.atomic():
            Location.objects.create(code=2, name="Municipality B", level=M, parent=self.province)

    def test_duplicate_name_under_the_same_parent_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Location.objects.create(code=2, name="Municipality A", level=M, parent=self.district)

    def test_duplicate_code_within_a_level_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Location.objects.create(code=1, name="Municipality B", level=M, parent=self.district)

    def test_same_code_allowed_on_different_levels(self):
        self.assertEqual(Location.objects.filter(code=1).count(), 3)


class LoadLocationsTests(TestCase):
    def test_loads_expected_counts_and_is_idempotent(self):
        load()
        self.assertEqual(level_counts(), LOADED)
        load()
        self.assertEqual(level_counts(), LOADED)

    def test_ancestor_columns_are_consistent(self):
        load()
        districts = Location.objects.filter(level=D)
        municipalities = Location.objects.filter(level=M)
        self.assertFalse(districts.exclude(province_id=F("parent_id")).exists())
        self.assertFalse(municipalities.exclude(district_id=F("parent_id")).exists())
        self.assertFalse(municipalities.exclude(province_id=F("district__province_id")).exists())

    def test_every_municipality_has_a_type(self):
        load()
        self.assertFalse(Location.objects.filter(level=M, type="").exists())

    def test_reload_restores_names_from_the_files(self):
        load()
        district = Location.objects.filter(level=D).order_by("pk").first()
        original = district.name
        Location.objects.filter(pk=district.pk).update(name="Renamed")
        load()
        district.refresh_from_db()
        self.assertEqual(district.name, original)

    def test_reload_keeps_a_retired_location_retired(self):
        load()
        retired = Location.objects.filter(level=M).order_by("pk").first()
        Location.objects.filter(pk=retired.pk).update(is_active=False)
        load()
        retired.refresh_from_db()
        self.assertFalse(retired.is_active)


class LocationApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        load()

    def setUp(self):
        cache.delete(TREE_CACHE_KEY)  # the tree is cached in Redis

    def test_list_is_public_and_filters_by_parent_in_one_query(self):
        province = Location.objects.filter(level=P).order_by("pk").first()
        with self.assertNumQueries(1):
            res = self.client.get(LIST_URL, {"level": D, "parent": province.pk})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data)
        self.assertTrue(all(row["level"] == D and row["province"] == province.pk for row in res.data))

    def test_list_hides_retired_locations(self):
        retired = Location.objects.filter(level=M).order_by("pk").first()
        Location.objects.filter(pk=retired.pk).update(is_active=False)
        res = self.client.get(LIST_URL, {"district": retired.district_id})
        self.assertEqual(res.status_code, 200)
        self.assertNotIn(retired.pk, [row["id"] for row in res.data])

    def test_municipality_rows_carry_district_and_province_names(self):
        res = self.client.get(LIST_URL, {"search": "Kathmandu Metropolitan"})
        self.assertEqual(res.status_code, 200)
        row = next(r for r in res.data if r["level"] == M)
        self.assertEqual(row["district_name"], "Kathmandu")
        self.assertEqual(row["province_name"], "Bagmati Province")

    def test_detail_and_unknown_id(self):
        province = Location.objects.filter(level=P).order_by("pk").first()
        self.assertEqual(self.client.get(f"{LIST_URL}{province.pk}/").status_code, 200)
        self.assertEqual(self.client.get(f"{LIST_URL}999999/").status_code, 404)

    def test_writes_are_not_allowed(self):
        self.assertEqual(self.client.post(LIST_URL, {"name": "X"}).status_code, 405)

    def test_tree_is_cached_and_cleared_when_a_location_changes(self):
        res = self.client.get(TREE_URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 7)
        self.assertTrue(res.data[0]["children"][0]["children"])
        self.assertIsNotNone(cache.get(TREE_CACHE_KEY))

        with self.assertNumQueries(0):
            self.client.get(TREE_URL)

        Location.objects.filter(level=M).order_by("pk").first().save()  # post_save clears the cache
        self.assertIsNone(cache.get(TREE_CACHE_KEY))
