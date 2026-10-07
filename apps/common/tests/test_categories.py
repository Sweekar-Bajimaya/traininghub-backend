from io import StringIO
from unittest import mock

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APITestCase

from apps.common import services
from apps.common.constants import CATEGORY_TREE_CACHE_KEY
from apps.common.models.category import Category
from apps.common.tests.helpers import make_category
from apps.institutes.tests.helpers import PASSWORD, User, make_institute
from apps.users import services as user_services

TREE_URL = "/api/v1/categories/"
ADMIN_URL = "/api/v1/admin/categories/"


class CategoryConstraintTests(TestCase):
    def assertRejected(self, **fields):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.create(**fields)

    def test_top_level_names_are_unique_ignoring_case(self):
        Category.objects.create(name="Hospitality")
        self.assertRejected(name="hospitality")

    def test_names_are_unique_per_parent_ignoring_case(self):
        top = Category.objects.create(name="Hospitality")
        Category.objects.create(name="Culinary", parent=top)
        self.assertRejected(name="CULINARY", parent=top)

    def test_the_same_name_under_two_parents_is_allowed(self):
        a = Category.objects.create(name="Hospitality")
        b = Category.objects.create(name="Healthcare")
        Category.objects.create(name="Basics", parent=a)
        Category.objects.create(name="Basics", parent=b)

    def test_a_category_cannot_be_its_own_parent(self):
        top = Category.objects.create(name="Hospitality")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.filter(pk=top.pk).update(parent=top)

    def test_hue_above_360_is_rejected(self):
        self.assertRejected(name="Hospitality", hue=361)


class CategoryServiceTests(TestCase):
    def setUp(self):
        self.top = services.create_category(name="Hospitality")
        self.sub = services.create_category(name="Culinary", parent=self.top)

    def test_a_sub_category_cannot_have_sub_categories(self):
        with self.assertRaises(ValidationError):
            services.create_category(name="Baking", parent=self.sub)

    def test_a_category_with_children_must_stay_top_level(self):
        other = services.create_category(name="Healthcare")
        with self.assertRaises(ValidationError):
            services.update_category(self.top, parent=other)

    def test_a_sub_category_can_move_to_another_top_level(self):
        other = services.create_category(name="Healthcare")
        services.update_category(self.sub, parent=other)
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.parent, other)

    def test_renaming_or_moving_queues_the_training_refresh(self):
        other = services.create_category(name="Healthcare")
        for fields in ({"name": "Cooking"}, {"parent": other}):
            with self.subTest(fields=fields), mock.patch(
                "apps.common.services.async_task"
            ) as task, self.captureOnCommitCallbacks(execute=True):
                services.update_category(self.sub, **fields)
            task.assert_called_once_with(
                "apps.training.tasks.refresh_category_trainings", self.sub.pk, save=False
            )

    def test_deactivating_does_not_queue_a_refresh(self):
        with mock.patch("apps.common.services.async_task") as task, self.captureOnCommitCallbacks(
            execute=True
        ):
            services.update_category(self.sub, is_active=False)
        task.assert_not_called()


class CategoryTreeApiTests(APITestCase):
    def setUp(self):
        cache.delete(CATEGORY_TREE_CACHE_KEY)
        self.top = Category.objects.create(name="Hospitality", icon="ri-cup-line", hue=50)
        Category.objects.create(name="Culinary", parent=self.top)
        retired = Category.objects.create(name="Retired", is_active=False)
        Category.objects.create(name="Orphan", parent=retired)

    def test_public_tree_hides_inactive_categories_and_their_children(self):
        res = self.client.get(TREE_URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual([n["name"] for n in res.data], ["Hospitality"])
        node = res.data[0]
        self.assertEqual((node["icon"], node["hue"]), ("ri-cup-line", 50))
        self.assertEqual([c["name"] for c in node["children"]], ["Culinary"])

    def test_tree_is_cached_and_cleared_by_a_save(self):
        self.client.get(TREE_URL)
        with self.assertNumQueries(0):
            self.client.get(TREE_URL)
        Category.objects.create(name="Healthcare")
        names = [n["name"] for n in self.client.get(TREE_URL).data]
        self.assertIn("Healthcare", names)


class AdminCategoryApiTests(APITestCase):
    def setUp(self):
        self.reviewer = self.admin_with(["manage_categories"], "cat@example.com")

    def admin_with(self, permissions, email):
        admin = user_services.create_admin(
            email=email, password=PASSWORD, full_name="Admin", permissions=permissions
        )
        return User.objects.get(pk=admin.pk)

    def test_access_matrix(self):
        _, staff = make_institute()
        other_admin = self.admin_with(["manage_institutes"], "other@example.com")
        for user, expected in ((None, 401), (staff, 403), (other_admin, 403), (self.reviewer, 200)):
            with self.subTest(user=getattr(user, "email", "anonymous")):
                self.client.force_authenticate(user)
                self.assertEqual(self.client.get(ADMIN_URL).status_code, expected)

    def test_create_rename_move_and_deactivate(self):
        self.client.force_authenticate(self.reviewer)
        top = self.client.post(
            ADMIN_URL, {"name": " Hospitality ", "icon": "ri-cup-line", "hue": 50}, format="json"
        )
        self.assertEqual(top.status_code, 201, top.data)
        self.assertEqual((top.data["name"], top.data["hue"]), ("Hospitality", 50))
        other = self.client.post(ADMIN_URL, {"name": "Healthcare"}, format="json").data
        sub = self.client.post(
            ADMIN_URL, {"name": "Culinary", "parent": top.data["id"]}, format="json"
        ).data
        url = f"{ADMIN_URL}{sub['id']}/"
        res = self.client.patch(url, {"name": "Cooking", "parent": other["id"]}, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["parent_name"], "Healthcare")
        res = self.client.patch(url, {"is_active": False}, format="json")
        self.assertFalse(res.data["is_active"])

    def test_duplicate_name_ignoring_case_is_400(self):
        self.client.force_authenticate(self.reviewer)
        self.client.post(ADMIN_URL, {"name": "Hospitality"}, format="json")
        res = self.client.post(ADMIN_URL, {"name": "hospitality"}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("name", res.data)

    def test_a_sub_category_cannot_be_a_parent(self):
        self.client.force_authenticate(self.reviewer)
        sub = make_category()
        res = self.client.post(ADMIN_URL, {"name": "Deep", "parent": sub.pk}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_a_hue_above_360_is_400_not_a_database_error(self):
        self.client.force_authenticate(self.reviewer)
        res = self.client.post(ADMIN_URL, {"name": "Colourful", "hue": 361}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("hue", res.data)

    def test_there_is_no_delete(self):
        self.client.force_authenticate(self.reviewer)
        category = make_category()
        self.assertEqual(self.client.delete(f"{ADMIN_URL}{category.pk}/").status_code, 405)


class LoadCategoriesTests(TestCase):
    def load(self):
        call_command("load_categories", stdout=StringIO())

    def test_loads_the_ui_list_and_is_safe_to_run_twice(self):
        self.load()
        self.load()
        self.assertEqual(Category.objects.filter(parent=None).count(), 13)
        self.assertEqual(Category.objects.exclude(parent=None).count(), 22)
        it = Category.objects.get(name="IT & Computer")
        self.assertEqual((it.icon, it.hue), ("ri-computer-line", 235))

    def test_never_reactivates_or_overwrites_admin_changes(self):
        self.load()
        Category.objects.filter(name="Hospitality").update(is_active=False, icon="ri-custom")
        self.load()
        hospitality = Category.objects.get(name="Hospitality")
        self.assertFalse(hospitality.is_active)
        self.assertEqual(hospitality.icon, "ri-custom")
