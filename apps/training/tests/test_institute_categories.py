from rest_framework.test import APITestCase

from apps.common.models.category import Category
from apps.training.constants import TrainingStatus
from apps.training.tests.helpers import (
    approved_institute,
    count_queries,
    make_category,
    make_training,
)

URL = "/api/v1/institutes/"
S = TrainingStatus


def top_level(name):
    return Category.objects.get_or_create(name=name, parent=None)[0]


def entry(category):
    return {"id": category.pk, "slug": category.slug, "name": category.name}


class InstituteCategoriesTests(APITestCase):
    """`categories` on the public institute detail: the top-level categories of the institute's
    approved trainings."""

    def setUp(self):
        self.institute, _, _ = approved_institute()

    def categories(self, institute=None):
        institute = institute or self.institute
        res = self.client.get(f"{URL}{institute.slug}/")
        self.assertEqual(res.status_code, 200, res.data)
        return res.data["categories"]

    def test_a_training_in_a_sub_category_shows_its_top_level_parent(self):
        sub = make_category("Python", "Technology")
        make_training(self.institute, category=sub)
        self.assertEqual(self.categories(), [entry(sub.parent)])

    def test_a_training_in_a_top_level_category_shows_that_category(self):
        design = top_level("Design")
        make_training(self.institute, category=design)
        self.assertEqual(self.categories(), [entry(design)])

    def test_a_category_is_listed_once_however_many_trainings_use_it(self):
        python = make_category("Python", "Technology")
        django_ = make_category("Django", "Technology")
        make_training(self.institute, category=python, title="One")
        make_training(self.institute, category=python, title="Two")
        make_training(self.institute, category=django_, title="Three")
        make_training(self.institute, category=python.parent, title="Four")  # the top level itself
        self.assertEqual(self.categories(), [entry(python.parent)])

    def test_the_categories_are_ordered_by_name(self):
        for name in ("Zoology", "Accounting", "Marketing"):
            make_training(self.institute, category=top_level(name), title=name)
        self.assertEqual(
            [c["name"] for c in self.categories()], ["Accounting", "Marketing", "Zoology"]
        )

    def test_only_approved_trainings_count(self):
        shown = top_level("Shown")
        make_training(self.institute, category=shown, title="Live")
        for status in S.TRANSITIONS:
            if status == S.APPROVED:
                continue
            make_training(
                self.institute,
                category=make_category(f"Sub {status}", f"Top {status}"),
                status=status,
                title=f"T {status}",
            )
        self.assertEqual(self.categories(), [entry(shown)])

    def test_an_institute_without_approved_trainings_has_an_empty_list(self):
        self.assertEqual(self.categories(), [])
        make_training(self.institute, status=S.DRAFT)
        self.assertEqual(self.categories(), [])

    def test_another_institutes_categories_do_not_leak(self):
        other, _, _ = approved_institute("Beta Institute", "beta@example.com", code=2)
        mine, theirs = top_level("Mine"), top_level("Theirs")
        make_training(self.institute, category=mine, title="Mine")
        make_training(other, category=theirs, title="Theirs")
        self.assertEqual(self.categories(), [entry(mine)])
        self.assertEqual(self.categories(other), [entry(theirs)])

    def test_a_retired_top_level_category_is_left_out(self):
        live = top_level("Live")
        retired_parent = make_category("Python", "Technology").parent  # a sub-category's parent
        retired_direct = top_level("Design")  # a training filed straight under it
        make_training(self.institute, category=live, title="Live")
        make_training(self.institute, category=make_category("Django", "Technology"), title="Sub")
        make_training(self.institute, category=retired_direct, title="Direct")
        Category.objects.filter(pk__in=(retired_parent.pk, retired_direct.pk)).update(is_active=False)
        self.assertEqual(self.categories(), [entry(live)])

    def test_a_retired_sub_category_does_not_hide_its_active_parent(self):
        sub = make_category("Python", "Technology")
        make_training(self.institute, category=sub)
        Category.objects.filter(pk=sub.pk).update(is_active=False)
        self.assertEqual(self.categories(), [entry(sub.parent)])  # like the public category tree

    def test_it_agrees_with_the_lists_category_count(self):
        python = make_category("Python", "Technology")
        make_training(self.institute, category=python, title="One")
        make_training(self.institute, category=top_level("Design"), title="Two")
        make_training(self.institute, category=make_category("Java", "Technology"), title="Three")
        retired = top_level("Retired")  # neither the list nor the detail counts it
        make_training(self.institute, category=retired, title="Four")
        make_training(self.institute, category=make_category("Old", "Gone"), title="Five")
        Category.objects.filter(name__in=("Retired", "Gone")).update(is_active=False)
        row = next(
            r
            for r in self.client.get(URL).data["results"]
            if r["slug"] == self.institute.slug
        )
        self.assertEqual(row["category_count"], len(self.categories()))
        self.assertEqual(row["category_count"], 2)

    def test_the_list_does_not_carry_it(self):
        make_training(self.institute)
        self.assertNotIn("categories", self.client.get(URL).data["results"][0])


class InstituteCategoriesQueryTests(APITestCase):
    def test_the_detail_costs_the_same_queries_for_one_or_many_categories(self):
        institute, _, _ = approved_institute()
        make_training(institute, category=top_level("Cat 0"), title="T0")
        detail = f"{URL}{institute.slug}/"
        one = count_queries(lambda: self.client.get(detail))
        for i in range(1, 7):
            make_training(institute, category=top_level(f"Cat {i}"), title=f"T{i}")
        many = count_queries(lambda: self.client.get(detail))
        self.assertEqual(one, many)
        self.assertLessEqual(many, 4)  # the categories come with the institute query
        self.assertEqual(len(self.client.get(detail).data["categories"]), 7)
