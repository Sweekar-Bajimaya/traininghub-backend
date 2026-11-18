from rest_framework.test import APITestCase

from apps.notification.tests.helpers import (
    approved_institute,
    make_row,
    reset_throttles,
)

URL = "/api/v1/notifications/"


class NotificationApiTests(APITestCase):
    def setUp(self):
        reset_throttles()
        self.institute, self.owner, _ = approved_institute()
        _, self.other_owner, _ = approved_institute(
            name="Beta Institute", email="beta@example.com", code=2
        )

    def test_login_is_required(self):
        self.assertEqual(self.client.get(URL).status_code, 401)

    def test_the_list_shows_only_my_rows_newest_first(self):
        older = make_row(self.owner, created_days_ago=2)
        newer = make_row(self.owner)
        make_row(self.other_owner)
        self.client.force_authenticate(self.owner)
        with self.assertNumQueries(2):  # the page count and the rows
            response = self.client.get(URL)
        self.assertEqual(
            [row["id"] for row in response.data["results"]], [newer.pk, older.pk]
        )

    def test_the_unread_filter_and_count(self):
        make_row(self.owner)
        make_row(self.owner, read_days_ago=0)
        self.client.force_authenticate(self.owner)
        self.assertEqual(
            len(self.client.get(URL, {"unread": "true"}).data["results"]), 1
        )
        self.assertEqual(self.client.get(URL + "unread-count/").data, {"count": 1})

    def test_marking_one_read(self):
        row = make_row(self.owner)
        self.client.force_authenticate(self.owner)
        response = self.client.post(f"{URL}{row.pk}/read/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_read"])

    def test_another_users_row_is_a_404(self):
        row = make_row(self.other_owner)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.post(f"{URL}{row.pk}/read/").status_code, 404)

    def test_mark_all_read_only_touches_my_rows(self):
        mine = make_row(self.owner)
        theirs = make_row(self.other_owner)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.post(URL + "read-all/").data, {"updated": 1})
        mine.refresh_from_db()
        theirs.refresh_from_db()
        self.assertIsNotNone(mine.read_at)
        self.assertIsNone(theirs.read_at)

    def test_mark_all_read_is_not_a_get(self):
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.get(URL + "read-all/").status_code, 405)
