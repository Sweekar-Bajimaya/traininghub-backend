from django.conf import settings
from django.test import SimpleTestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from apps.common.pagination import CappedLimitOffsetPagination


def limit_for(query):
    """The limit the paginator would apply to `GET /?<query>`."""
    request = Request(APIRequestFactory().get(f"/?{query}" if query else "/"))
    return CappedLimitOffsetPagination().get_limit(request)


class CappedLimitOffsetPaginationTests(SimpleTestCase):
    def test_it_is_the_project_default(self):
        self.assertEqual(
            settings.REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"],
            "apps.common.pagination.CappedLimitOffsetPagination",
        )

    def test_no_limit_uses_the_page_size(self):
        self.assertEqual(limit_for(""), settings.REST_FRAMEWORK["PAGE_SIZE"])

    def test_a_limit_under_the_cap_is_kept(self):
        self.assertEqual(limit_for("limit=25"), 25)

    def test_the_cap_itself_is_allowed(self):
        self.assertEqual(limit_for("limit=100"), 100)

    def test_a_limit_over_the_cap_is_lowered_to_it(self):
        self.assertEqual(limit_for("limit=101"), 100)
        self.assertEqual(limit_for("limit=100000"), 100)

    def test_zero_negative_and_junk_fall_back_to_the_page_size(self):
        for query in ("limit=0", "limit=-5", "limit=abc"):
            with self.subTest(query=query):
                self.assertEqual(limit_for(query), settings.REST_FRAMEWORK["PAGE_SIZE"])
