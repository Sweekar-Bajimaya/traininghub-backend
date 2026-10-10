from rest_framework.test import APITestCase

from apps.enquiries.constants import EnquiryStatus
from apps.enquiries.models import Enquiry, EnquiryNote
from apps.enquiries.tests.helpers import (
    PASSWORD,
    User,
    approved_institute,
    count_queries,
    make_admin,
    make_enquiry,
    make_training,
)
from apps.institutes.constants import MemberRole
from apps.institutes.models import InstituteMember
from apps.users.constants import Role

PORTAL = "/api/v1/institute/enquiries/"
S = EnquiryStatus

LIST_FIELDS = {
    "id", "name", "phone", "email", "type", "status", "training", "training_title", "created_at",
}
DETAIL_FIELDS = {
    "id", "name", "phone", "email", "message", "type", "preferred_time", "status", "training",
    "training_title", "notes", "created_at", "modified_at",
}


class PortalTestCase(APITestCase):
    def setUp(self):
        self.institute, self.owner, _ = approved_institute()
        self.staff = User.objects.create_user(
            "staff@example.com", PASSWORD, full_name="Sujata M.", role=Role.INSTITUTE_STAFF
        )
        InstituteMember.objects.create(
            user=self.staff, institute=self.institute, role=MemberRole.STAFF
        )
        self.training = make_training(self.institute)
        self.other_institute, self.other_owner, _ = approved_institute(
            "Beta Institute", "beta@example.com", code=2
        )
        self.other_training = make_training(self.other_institute, title="Beta course")
        self.client.force_authenticate(self.staff)

    def url(self, enquiry, suffix=""):
        return f"{PORTAL}{enquiry.pk}/{suffix}"


class AccessTests(PortalTestCase):
    def test_access_matrix(self):
        mine = make_enquiry(self.training)
        admin = make_admin("admin@example.com", permissions=("manage_enquiries",))
        endpoints = (
            ("get", PORTAL),
            ("get", f"{PORTAL}summary/"),
            ("get", self.url(mine)),
            ("patch", self.url(mine)),
            ("get", self.url(mine, "notes/")),
            ("post", self.url(mine, "notes/")),
        )
        # staff and owner may do everything; an admin and an anonymous caller may not
        for user, expected in ((None, 401), (admin, 403), (self.staff, "ok"), (self.owner, "ok")):
            self.client.force_authenticate(user)
            for method, url in endpoints:
                with self.subTest(user=getattr(user, "email", "anonymous"), method=method, url=url):
                    res = getattr(self.client, method)(url, {"text": "x"}, format="json")
                    if expected == "ok":
                        self.assertLess(res.status_code, 300, res.data)
                    else:
                        self.assertEqual(res.status_code, expected)

    def test_another_institutes_enquiry_is_a_404_not_a_403(self):
        theirs = make_enquiry(self.other_training)
        for method, suffix in (("get", ""), ("patch", ""), ("get", "notes/"), ("post", "notes/")):
            with self.subTest(method=method, suffix=suffix):
                res = getattr(self.client, method)(
                    self.url(theirs, suffix), {"status": S.CLOSED, "text": "x"}, format="json"
                )
                self.assertEqual(res.status_code, 404)
        theirs.refresh_from_db()
        self.assertEqual(theirs.status, S.NEW)
        self.assertFalse(EnquiryNote.objects.exists())

    def test_an_unknown_enquiry_is_a_404(self):
        for method, suffix in (("get", "999999/"), ("patch", "999999/"), ("get", "999999/notes/")):
            with self.subTest(method=method, suffix=suffix):
                res = getattr(self.client, method)(f"{PORTAL}{suffix}", {}, format="json")
                self.assertEqual(res.status_code, 404)

    def test_only_reading_and_patching_are_allowed(self):
        enquiry = make_enquiry(self.training)
        self.assertEqual(self.client.post(PORTAL, {}, format="json").status_code, 405)
        self.assertEqual(self.client.put(self.url(enquiry), {}, format="json").status_code, 405)
        self.assertEqual(self.client.delete(self.url(enquiry)).status_code, 405)
        self.assertTrue(Enquiry.objects.filter(pk=enquiry.pk).exists())


class ListTests(PortalTestCase):
    def test_lists_only_this_institutes_enquiries_newest_first(self):
        first, second, third = (make_enquiry(self.training) for _ in range(3))
        make_enquiry(self.other_training)
        res = self.client.get(PORTAL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 3)
        self.assertEqual([r["id"] for r in res.data["results"]], [third.pk, second.pk, first.pk])
        row = res.data["results"][0]
        self.assertEqual(set(row), LIST_FIELDS)  # no message and no notes in a table row
        self.assertEqual((row["training"], row["training_title"]), (self.training.pk, self.training.title))
        self.assertEqual(row["status"], S.NEW)

    def test_a_page_is_as_long_as_limit_says(self):
        for _ in range(5):
            make_enquiry(self.training)
        res = self.client.get(PORTAL, {"limit": 2, "offset": 2})
        self.assertEqual((res.data["count"], len(res.data["results"])), (5, 2))

    def test_filter_by_status(self):
        new = make_enquiry(self.training)
        converted = make_enquiry(self.training, status=S.CONVERTED)
        res = self.client.get(PORTAL, {"status": S.CONVERTED})
        self.assertEqual([r["id"] for r in res.data["results"]], [converted.pk])
        res = self.client.get(PORTAL, {"status": S.NEW})
        self.assertEqual([r["id"] for r in res.data["results"]], [new.pk])
        self.assertEqual(self.client.get(PORTAL, {"status": "WON"}).status_code, 400)

    def test_filter_by_training(self):
        other = make_training(self.institute, title="Second course")
        mine = make_enquiry(self.training)
        make_enquiry(other)
        res = self.client.get(PORTAL, {"training": self.training.pk})
        self.assertEqual([r["id"] for r in res.data["results"]], [mine.pk])
        # another institute's training id finds nothing here
        self.assertEqual(self.client.get(PORTAL, {"training": self.other_training.pk}).data["count"], 0)

    def test_search_name_phone_and_email_anywhere_in_the_text(self):
        ram = make_enquiry(self.training, name="Ram Sharma", phone="9841526370", email="ram.s@example.com")
        sita = make_enquiry(self.training, name="Sita Thapa", phone="9803217745", email="")
        for query, expected in (
            ("ram", [ram]),
            ("SHARMA", [ram]),  # not case-sensitive
            ("1526", [ram]),
            ("9803", [sita]),
            ("ram.s@", [ram]),
            ("example.com", [ram]),
            ("  thapa  ", [sita]),
            ("nobody", []),
            ("", [sita, ram]),
        ):
            with self.subTest(q=query):
                res = self.client.get(PORTAL, {"q": query})
                self.assertEqual([r["id"] for r in res.data["results"]], [e.pk for e in expected])

    def test_filters_combine(self):
        other = make_training(self.institute, title="Second course")
        keep = make_enquiry(self.training, name="Ram", status=S.CONTACTED)
        make_enquiry(self.training, name="Ram", status=S.NEW)
        make_enquiry(other, name="Ram", status=S.CONTACTED)
        make_enquiry(self.training, name="Sita", status=S.CONTACTED)
        res = self.client.get(PORTAL, {"q": "ram", "status": S.CONTACTED, "training": self.training.pk})
        self.assertEqual([r["id"] for r in res.data["results"]], [keep.pk])

    def test_the_query_count_does_not_grow_with_the_list(self):
        make_enquiry(self.training)
        few = count_queries(lambda: self.client.get(PORTAL, {"limit": 50}))
        for _ in range(12):
            make_enquiry(make_training(self.institute, title="More"))
        self.assertEqual(count_queries(lambda: self.client.get(PORTAL, {"limit": 50})), few)


class DetailTests(PortalTestCase):
    def test_the_detail_has_the_message_the_preferred_time_and_the_notes(self):
        enquiry = make_enquiry(
            self.training,
            message="Is the morning batch open?",
            preferred_time="MORNING",
            email="ram@example.com",
            type="INTEREST",
        )
        nameless = User.objects.create_user("nameless@example.com", PASSWORD, role=Role.INSTITUTE_STAFF)
        EnquiryNote.objects.create(enquiry=enquiry, author=self.staff, text="Called at 2 PM")
        EnquiryNote.objects.create(enquiry=enquiry, author=self.owner, text="Visiting Thursday")
        EnquiryNote.objects.create(enquiry=enquiry, author=nameless, text="Sent the fee sheet")
        res = self.client.get(self.url(enquiry))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(set(res.data), DETAIL_FIELDS)
        self.assertEqual(res.data["message"], "Is the morning batch open?")
        self.assertEqual((res.data["preferred_time"], res.data["type"]), ("MORNING", "INTEREST"))
        self.assertEqual(res.data["training_title"], self.training.title)
        # newest first; a name when the author has one, else the email
        self.assertEqual(
            [(n["text"], n["author"]) for n in res.data["notes"]],
            [
                ("Sent the fee sheet", "nameless@example.com"),
                ("Visiting Thursday", "Owner"),
                ("Called at 2 PM", "Sujata M."),
            ],
        )

    def test_a_note_whose_author_left_has_no_name(self):
        enquiry = make_enquiry(self.training)
        EnquiryNote.objects.create(enquiry=enquiry, author=None, text="Old note")
        self.assertIsNone(self.client.get(self.url(enquiry)).data["notes"][0]["author"])

    def test_the_query_count_does_not_grow_with_the_notes(self):
        enquiry = make_enquiry(self.training)
        EnquiryNote.objects.create(enquiry=enquiry, author=self.staff, text="one")
        few = count_queries(lambda: self.client.get(self.url(enquiry)))
        for n in range(8):
            EnquiryNote.objects.create(enquiry=enquiry, author=self.owner, text=f"note {n}")
        self.assertEqual(count_queries(lambda: self.client.get(self.url(enquiry))), few)


class StatusChangeTests(PortalTestCase):
    def patch(self, enquiry, data):
        return self.client.patch(self.url(enquiry), data, format="json")

    def test_staff_and_owner_can_move_the_status_to_any_other(self):
        enquiry = make_enquiry(self.training)
        for user in (self.staff, self.owner):
            self.client.force_authenticate(user)
            for status in (S.CONTACTED, S.CONVERTED, S.NEW, S.CLOSED, S.FOLLOW_UP):
                with self.subTest(user=user.email, status=status):
                    res = self.patch(enquiry, {"status": status})
                    self.assertEqual(res.status_code, 200, res.data)
                    self.assertEqual(res.data["status"], status)
                    enquiry.refresh_from_db()
                    self.assertEqual(enquiry.status, status)

    def test_the_answer_is_the_full_detail_with_the_notes(self):
        enquiry = make_enquiry(self.training)
        EnquiryNote.objects.create(enquiry=enquiry, author=self.staff, text="Called")
        res = self.patch(enquiry, {"status": S.CONTACTED})
        self.assertEqual(set(res.data), DETAIL_FIELDS)
        self.assertEqual(len(res.data["notes"]), 1)

    def test_only_the_status_can_be_written(self):
        enquiry = make_enquiry(self.training, name="Ram Sharma", phone="9841526370", message="Hi")
        other = make_training(self.institute, title="Other")
        res = self.patch(
            enquiry,
            {
                "status": S.CONTACTED,
                "name": "Someone Else",
                "phone": "9801111111",
                "message": "Changed",
                "type": "INTEREST",
                "training": other.pk,
                "institute": self.other_institute.pk,
            },
        )
        self.assertEqual(res.status_code, 200)
        enquiry.refresh_from_db()
        self.assertEqual(
            (enquiry.name, enquiry.phone, enquiry.message, enquiry.type, enquiry.training_id, enquiry.institute_id),
            ("Ram Sharma", "9841526370", "Hi", "ENQUIRY", self.training.pk, self.institute.pk),
        )
        self.assertEqual(enquiry.status, S.CONTACTED)

    def test_an_empty_patch_changes_nothing(self):
        enquiry = make_enquiry(self.training, status=S.INTERESTED)
        self.assertEqual(self.patch(enquiry, {}).status_code, 200)
        enquiry.refresh_from_db()
        self.assertEqual(enquiry.status, S.INTERESTED)

    def test_an_unknown_status_is_a_400(self):
        enquiry = make_enquiry(self.training)
        for value in ("WON", "", "new", None):
            with self.subTest(value=value):
                res = self.patch(enquiry, {"status": value})
                self.assertEqual(res.status_code, 400)
                self.assertIn("status", res.data)

    def test_converted_stops_at_the_seats(self):
        training = make_training(self.institute, seats=1, title="One seat")
        first, second = make_enquiry(training), make_enquiry(training)
        self.assertEqual(self.patch(first, {"status": S.CONVERTED}).status_code, 200)
        res = self.patch(second, {"status": S.CONVERTED})
        self.assertEqual(res.status_code, 400)
        self.assertIn("seats", res.data["status"][0])
        self.assertEqual(self.patch(first, {"status": S.CLOSED}).status_code, 200)
        self.assertEqual(self.patch(second, {"status": S.CONVERTED}).status_code, 200)

    def test_reopening_next_to_another_open_enquiry_is_a_400(self):
        closed = make_enquiry(self.training, phone="9841526370", status=S.CLOSED)
        make_enquiry(self.training, phone="9841526370")
        res = self.patch(closed, {"status": S.NEW})
        self.assertEqual(res.status_code, 400)
        self.assertIn("open enquiry", res.data["status"][0])


class NoteTests(PortalTestCase):
    def test_a_note_is_added_with_the_callers_name(self):
        enquiry = make_enquiry(self.training)
        res = self.client.post(self.url(enquiry, "notes/"), {"text": "  Called at 2 PM  "}, format="json")
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual((res.data["text"], res.data["author"]), ("Called at 2 PM", "Sujata M."))
        note = EnquiryNote.objects.get()
        self.assertEqual((note.enquiry, note.author), (enquiry, self.staff))

    def test_the_author_and_enquiry_cannot_be_chosen(self):
        enquiry = make_enquiry(self.training)
        theirs = make_enquiry(self.other_training)
        res = self.client.post(
            self.url(enquiry, "notes/"),
            {"text": "Hi", "author": self.owner.pk, "enquiry": theirs.pk},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        note = EnquiryNote.objects.get()
        self.assertEqual((note.enquiry, note.author), (enquiry, self.staff))

    def test_a_blank_or_oversized_note_is_a_400(self):
        enquiry = make_enquiry(self.training)
        for text in ("", "   ", "x" * 2001):
            with self.subTest(length=len(text)):
                res = self.client.post(self.url(enquiry, "notes/"), {"text": text}, format="json")
                self.assertEqual(res.status_code, 400)
                self.assertIn("text", res.data)
        self.assertEqual(self.client.post(self.url(enquiry, "notes/"), {}, format="json").status_code, 400)
        self.assertFalse(EnquiryNote.objects.exists())

    def test_notes_are_listed_newest_first_and_all_of_them(self):
        enquiry = make_enquiry(self.training)
        for n in range(12):  # more than a page of the default pagination
            EnquiryNote.objects.create(enquiry=enquiry, author=self.staff, text=f"note {n}")
        make_enquiry(self.training)  # another enquiry's notes stay out
        EnquiryNote.objects.create(enquiry=Enquiry.objects.exclude(pk=enquiry.pk).get(), text="elsewhere")
        res = self.client.get(self.url(enquiry, "notes/"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 12)  # a plain list, not a page
        self.assertEqual(res.data[0]["text"], "note 11")

    def test_a_colleagues_note_is_visible_to_the_team(self):
        enquiry = make_enquiry(self.training)
        self.client.post(self.url(enquiry, "notes/"), {"text": "From staff"}, format="json")
        self.client.force_authenticate(self.owner)
        res = self.client.get(self.url(enquiry, "notes/"))
        self.assertEqual([n["text"] for n in res.data], ["From staff"])

    def test_the_query_count_does_not_grow_with_the_notes(self):
        enquiry = make_enquiry(self.training)
        EnquiryNote.objects.create(enquiry=enquiry, author=self.staff, text="one")
        few = count_queries(lambda: self.client.get(self.url(enquiry, "notes/")))
        for n in range(8):
            EnquiryNote.objects.create(enquiry=enquiry, author=self.owner, text=f"note {n}")
        self.assertEqual(count_queries(lambda: self.client.get(self.url(enquiry, "notes/"))), few)


class SummaryTests(PortalTestCase):
    SUMMARY = f"{PORTAL}summary/"

    def test_counts_for_the_tabs_the_badge_and_the_cards(self):
        make_enquiry(self.training, phone="9841111111")
        make_enquiry(self.training, phone="9841111111", status=S.CLOSED)  # the same person again
        make_enquiry(self.training, status=S.CONVERTED)
        make_enquiry(self.other_training)  # another institute's do not count
        res = self.client.get(self.SUMMARY)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(set(res.data), {"total", "new", "unique_phones", "by_status"})
        self.assertEqual((res.data["total"], res.data["new"], res.data["unique_phones"]), (3, 1, 2))
        self.assertEqual(list(res.data["by_status"]), list(S.VALUES))
        self.assertEqual(res.data["by_status"][S.CLOSED], 1)
        self.assertEqual(res.data["by_status"][S.CONTACTED], 0)

    def test_the_search_and_training_filters_apply(self):
        other = make_training(self.institute, title="Second course")
        make_enquiry(self.training, name="Ram Sharma")
        make_enquiry(self.training, name="Sita Thapa", status=S.CONTACTED)
        make_enquiry(other, name="Ram Karki")
        by_training = self.client.get(self.SUMMARY, {"training": self.training.pk}).data
        self.assertEqual((by_training["total"], by_training["by_status"][S.CONTACTED]), (2, 1))
        by_search = self.client.get(self.SUMMARY, {"q": "ram"}).data
        self.assertEqual((by_search["total"], by_search["by_status"][S.CONTACTED]), (2, 0))

    def test_no_enquiries_is_all_zeros(self):
        res = self.client.get(self.SUMMARY)
        self.assertEqual((res.data["total"], res.data["new"], res.data["unique_phones"]), (0, 0, 0))
        self.assertEqual(set(res.data["by_status"].values()), {0})

    def test_the_query_count_does_not_grow_with_the_enquiries(self):
        make_enquiry(self.training)
        few = count_queries(lambda: self.client.get(self.SUMMARY))
        for _ in range(10):
            make_enquiry(self.training)
        self.assertEqual(count_queries(lambda: self.client.get(self.SUMMARY)), few)
