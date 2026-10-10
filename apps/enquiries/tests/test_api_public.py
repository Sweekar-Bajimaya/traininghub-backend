import uuid
from datetime import timedelta

from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.enquiries.constants import MY_ENQUIRIES_DAYS, PHONE_DAILY_LIMIT, EnquiryStatus
from apps.enquiries.models import Enquiry
from apps.enquiries.tests.helpers import (
    approved_institute,
    count_queries,
    enquiry_payload,
    make_enquiry,
    make_training,
    new_token,
    next_phone,
    reset_limits,
    reset_throttles,
)
from apps.institutes.constants import InstituteStatus
from apps.institutes.models import Institute
from apps.training.constants import TrainingStatus

URL = "/api/v1/enquiries/"
MY = "/api/v1/enquiries/my/"
S = EnquiryStatus

VISITOR_FIELDS = {"id", "type", "training", "institute_name", "status_label", "created_at"}


class PublicTestCase(APITestCase):
    def setUp(self):
        reset_limits()
        self.institute, self.owner, _ = approved_institute()
        self.training = make_training(self.institute)
        self.token = new_token()

    def post(self, payload=None, token="default"):
        """Submit as a visitor. Throttles are cleared first, so a test can send many requests."""
        reset_throttles()
        headers = {} if token is None else {"HTTP_X_DEVICE_TOKEN": self.token if token == "default" else token}
        payload = enquiry_payload(self.training) if payload is None else payload
        return self.client.post(URL, payload, format="json", **headers)

    def get_my(self, token="default"):
        headers = {} if token is None else {"HTTP_X_DEVICE_TOKEN": self.token if token == "default" else token}
        return self.client.get(MY, **headers)


class SubmitTests(PublicTestCase):
    def test_anyone_can_submit_and_gets_the_visitors_view_back(self):
        res = self.post(
            enquiry_payload(
                self.training,
                phone="+977 984-1526370",
                email="Ram@Example.com",
                message="Is the morning batch open?",
                type="INTEREST",
                preferred_time="MORNING",
            )
        )
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(set(res.data), VISITOR_FIELDS)  # no phone, email or message echoed
        self.assertEqual(res.data["type"], "INTEREST")
        self.assertEqual(res.data["status_label"], "Sent to institute")
        self.assertEqual(res.data["institute_name"], self.institute.name)
        self.assertEqual(
            res.data["training"],
            {"id": self.training.pk, "slug": self.training.slug, "title": self.training.title},
        )
        enquiry = Enquiry.objects.get()
        self.assertEqual(enquiry.phone, "9841526370")  # normalised
        self.assertEqual(enquiry.email, "ram@example.com")
        self.assertEqual(enquiry.status, S.NEW)
        self.assertEqual(enquiry.institute_id, self.institute.pk)
        self.assertEqual(str(enquiry.device_token), self.token)
        self.assertEqual((enquiry.message, enquiry.preferred_time), ("Is the morning batch open?", "MORNING"))

    def test_only_name_phone_and_training_are_required(self):
        res = self.post({"training": self.training.slug, "name": "Sita", "phone": next_phone()})
        self.assertEqual(res.status_code, 201, res.data)
        enquiry = Enquiry.objects.get()
        self.assertEqual((enquiry.type, enquiry.email, enquiry.message, enquiry.preferred_time), ("ENQUIRY", "", "", ""))

    def test_a_logged_in_users_token_is_ignored(self):
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.post().status_code, 201)

    def test_phone_numbers_are_normalised_or_refused(self):
        accepted = {
            "9841526370": "9841526370",
            "+977 9851526370": "9851526370",
            "977-9861526370": "9861526370",
            "9771234567": "9771234567",  # a 977 number is not a country code when ten digits remain
        }
        for typed, stored in accepted.items():
            with self.subTest(typed=typed):
                res = self.post(enquiry_payload(self.training, phone=typed))
                self.assertEqual(res.status_code, 201, res.data)
                self.assertTrue(Enquiry.objects.filter(phone=stored).exists())
        for typed in ("984152637", "9541526370", "abc", "+977 12345", ""):
            with self.subTest(typed=typed):
                res = self.post(enquiry_payload(self.training, phone=typed))
                self.assertEqual(res.status_code, 400)
                self.assertIn("phone", res.data)

    def test_invalid_input_is_a_400(self):
        base = enquiry_payload(self.training)
        cases = {
            "name": ("name", "A"),
            "blank name": ("name", ""),
            "email": ("email", "not-an-email"),
            "type": ("type", "QUESTION"),
            "preferred_time": ("preferred_time", "NIGHT"),
            "message": ("message", "x" * 2001),
        }
        for label, (field, value) in cases.items():
            with self.subTest(label):
                res = self.post({**base, field: value})
                self.assertEqual(res.status_code, 400)
                self.assertIn(field, res.data)
        for field in ("training", "name", "phone"):
            with self.subTest(missing=field):
                res = self.post({k: v for k, v in base.items() if k != field})
                self.assertEqual(res.status_code, 400)
                self.assertIn(field, res.data)
        self.assertFalse(Enquiry.objects.exists())

    def test_the_status_cannot_be_chosen_by_the_visitor(self):
        res = self.post(enquiry_payload(self.training, status="CONVERTED", institute=999))
        self.assertEqual(res.status_code, 201)
        enquiry = Enquiry.objects.get()
        self.assertEqual((enquiry.status, enquiry.institute_id), (S.NEW, self.institute.pk))

    def test_only_a_published_training_of_an_approved_institute_is_found(self):
        draft = make_training(self.institute, status=TrainingStatus.DRAFT)
        unpublished = make_training(self.institute, status=TrainingStatus.UNPUBLISHED)
        for slug in ("no-such-training", draft.slug, unpublished.slug):
            with self.subTest(slug=slug):
                res = self.post(enquiry_payload(self.training, training=slug))
                self.assertEqual(res.status_code, 400)
                self.assertEqual(res.data["training"], ["This training is not accepting enquiries."])
        Institute.objects.filter(pk=self.institute.pk).update(status=InstituteStatus.SUSPENDED)
        self.assertEqual(self.post().status_code, 400)
        self.assertFalse(Enquiry.objects.exists())

    def test_closed_registration_and_full_seats_refuse_an_enquiry_but_not_an_interest(self):
        today = timezone.localdate()
        closed = make_training(
            self.institute,
            registration_deadline=today - timedelta(days=1),
            start_date=today + timedelta(days=10),
        )
        full = make_training(self.institute, seats=1)
        make_enquiry(full, status=S.CONVERTED)
        for training, word in ((closed, "closed"), (full, "full")):
            with self.subTest(training=word):
                refused = self.post(enquiry_payload(training))
                self.assertEqual(refused.status_code, 400)
                self.assertIn(word, refused.data["non_field_errors"][0])
                accepted = self.post(enquiry_payload(training, type="INTEREST"))
                self.assertEqual(accepted.status_code, 201, accepted.data)

    def test_a_second_open_enquiry_from_the_same_phone_is_refused(self):
        phone = next_phone()
        self.assertEqual(self.post(enquiry_payload(self.training, phone=phone)).status_code, 201)
        res = self.post(enquiry_payload(self.training, phone=phone))
        self.assertEqual(res.status_code, 400)
        self.assertIn("already", res.data["non_field_errors"][0])
        Enquiry.objects.update(status=S.CLOSED)
        self.assertEqual(self.post(enquiry_payload(self.training, phone=phone)).status_code, 201)


class DeviceTokenTests(PublicTestCase):
    def test_the_token_must_be_a_random_uuid(self):
        bad = {
            "missing": None,
            "empty": "",
            "not a uuid": "hello",
            "all zeros": str(uuid.UUID(int=0)),
            "a time-based uuid": str(uuid.uuid1()),
        }
        for label, token in bad.items():
            with self.subTest(label):
                for res in (self.post(token=token), self.get_my(token=token)):
                    self.assertEqual(res.status_code, 400)
                    self.assertIn("device_token", res.data)
        self.assertFalse(Enquiry.objects.exists())

    def test_a_uuid_without_hyphens_is_accepted_and_stored_in_the_same_form(self):
        token = uuid.uuid4()
        self.assertEqual(self.post(token=token.hex).status_code, 201)
        self.assertEqual(Enquiry.objects.get().device_token, token)
        self.assertEqual(self.get_my(token=str(token)).data["count"], 1)

    @override_settings(CORS_ALLOW_ALL_ORIGINS=True)
    def test_the_header_is_allowed_in_cors_preflights(self):
        res = self.client.options(
            URL,
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="x-device-token,content-type",
        )
        self.assertIn("x-device-token", res.headers.get("Access-Control-Allow-Headers", ""))


class ThrottleTests(PublicTestCase):
    def test_the_eleventh_request_from_one_address_in_an_hour_is_throttled(self):
        for n in range(10):
            res = self.client.post(
                URL, enquiry_payload(self.training), format="json", HTTP_X_DEVICE_TOKEN=self.token
            )
            self.assertEqual(res.status_code, 201, f"request {n + 1}")
        res = self.client.post(
            URL, enquiry_payload(self.training), format="json", HTTP_X_DEVICE_TOKEN=self.token
        )
        self.assertEqual(res.status_code, 429)
        self.assertIn("Retry-After", res.headers)
        self.assertEqual(Enquiry.objects.count(), 10)

    def test_a_phone_number_has_a_daily_allowance_whatever_the_address(self):
        phone = next_phone()
        trainings = [
            make_training(self.institute, title=f"Course {n}")
            for n in range(PHONE_DAILY_LIMIT + 1)
        ]
        for training in trainings[:PHONE_DAILY_LIMIT]:
            self.assertEqual(self.post(enquiry_payload(training, phone=phone)).status_code, 201)
        res = self.post(enquiry_payload(trainings[-1], phone=phone))
        self.assertEqual(res.status_code, 429)
        self.assertIn("Retry-After", res.headers)
        self.assertEqual(Enquiry.objects.filter(phone=phone).count(), PHONE_DAILY_LIMIT)
        self.assertEqual(self.post(enquiry_payload(trainings[-1])).status_code, 201)


class MyEnquiriesTests(PublicTestCase):
    def test_a_device_sees_only_its_own_enquiries_newest_first(self):
        mine = [make_enquiry(self.training, device_token=self.token) for _ in range(3)]
        make_enquiry(self.training)  # another browser's
        res = self.get_my()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 3)
        self.assertEqual([row["id"] for row in res.data["results"]], [e.pk for e in reversed(mine)])
        self.assertEqual(self.get_my(token=new_token()).data["count"], 0)

    def test_nothing_private_is_returned(self):
        make_enquiry(self.training, device_token=self.token, email="ram@example.com", message="secret")
        row = self.get_my().data["results"][0]
        self.assertEqual(set(row), VISITOR_FIELDS)
        self.assertEqual(set(row["training"]), {"id", "slug", "title"})
        self.assertNotIn("ram@example.com", str(row))
        self.assertNotIn("secret", str(row))

    def test_each_status_reads_as_the_prototypes_wording(self):
        for status in S.VALUES:
            make_enquiry(self.training, device_token=self.token, status=status)
        labels = {row["status_label"] for row in self.get_my().data["results"]}
        self.assertEqual(
            labels,
            {
                "Sent to institute",
                "Institute contacted you",
                "Institute will follow up",
                "Marked interested",
                "Enrolled",
                "Closed",
            },
        )
        # not interested and closed read the same, so the visitor never sees the institute's verdict
        expected = [S.VISITOR_LABELS[s] for s in S.VALUES]
        self.assertEqual(expected.count("Closed"), 2)

    def test_only_the_last_90_days_are_shown(self):
        old = make_enquiry(self.training, device_token=self.token)
        edge = make_enquiry(self.training, device_token=self.token)
        now = timezone.now()
        Enquiry.objects.filter(pk=old.pk).update(created_at=now - timedelta(days=MY_ENQUIRIES_DAYS + 1))
        Enquiry.objects.filter(pk=edge.pk).update(created_at=now - timedelta(days=MY_ENQUIRIES_DAYS - 1))
        ids = [row["id"] for row in self.get_my().data["results"]]
        self.assertEqual(ids, [edge.pk])
        self.assertTrue(Enquiry.objects.filter(pk=old.pk).exists())  # the institute still has it

    def test_the_visitor_follows_an_enquiry_from_sent_to_closed(self):
        created = self.post()
        self.assertEqual(created.status_code, 201)
        self.assertEqual(self.get_my().data["results"][0]["status_label"], "Sent to institute")
        Enquiry.objects.update(status=S.CONTACTED)
        self.assertEqual(self.get_my().data["results"][0]["status_label"], "Institute contacted you")

    def test_the_query_count_does_not_grow_with_the_list(self):
        make_enquiry(self.training, device_token=self.token)
        few = count_queries(lambda: self.get_my())
        for _ in range(8):
            make_enquiry(self.training, device_token=self.token)
        self.assertEqual(count_queries(lambda: self.get_my()), few)
