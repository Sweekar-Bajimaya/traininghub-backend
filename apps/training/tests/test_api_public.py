from datetime import time, timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.institutes.constants import InstituteStatus
from apps.institutes.models import InstituteContact
from apps.training import services
from apps.training.constants import TrainingStatus
from apps.training.models import Training, TrainingSession
from apps.training.tests.helpers import (
    approved_institute,
    count_queries,
    make_category,
    make_training,
)

URL = "/api/v1/trainings/"
S = TrainingStatus


def titles(res):
    return [row["title"] for row in res.data["results"]]


class PublicTrainingTestCase(APITestCase):
    def setUp(self):
        self.institute, _, self.location = approved_institute()
        self.today = timezone.localdate()

    def get(self, **params):
        res = self.client.get(URL, params)
        self.assertEqual(res.status_code, 200, res.data)
        return res


class VisibilityTests(PublicTrainingTestCase):
    def test_only_approved_trainings_of_approved_institutes(self):
        for status in S.TRANSITIONS:
            make_training(self.institute, status=status, title=f"T {status}")
        hidden_institute, _, _ = approved_institute("Beta", "beta@example.com", code=2)
        make_training(hidden_institute, title="Suspended institute")
        hidden_institute.status = InstituteStatus.SUSPENDED
        hidden_institute.save()
        self.assertEqual(titles(self.get()), ["T APPROVED"])

    def test_detail_of_a_hidden_training_is_404(self):
        draft = make_training(self.institute, status=S.DRAFT)
        self.assertEqual(self.client.get(f"{URL}{draft.slug}/").status_code, 404)

    def test_writes_are_not_allowed(self):
        training = make_training(self.institute)
        self.assertEqual(self.client.post(URL, {}).status_code, 405)
        self.assertEqual(self.client.patch(f"{URL}{training.slug}/", {}).status_code, 405)


class FilterTests(PublicTrainingTestCase):
    def setUp(self):
        super().setUp()
        self.coffee = make_category("Coffee", parent="Hospitality")
        self.python = make_category("Python", parent="Technology")
        self.online = make_training(
            self.institute, title="Online", category=self.python, fee_npr=Decimal("5000"),
            level="ADVANCED",
        )
        self.physical = make_training(
            self.institute, title="Physical", category=self.coffee, location=self.location,
            fee_npr=Decimal("20000"), duration_value=3, duration_unit="MONTHS", duration_weeks=13,
            start_date=self.today + timedelta(days=60), end_date=self.today + timedelta(days=150),
            registration_deadline=None,
        )
        self.short = make_training(
            self.institute, title="Short", category=self.coffee.parent, fee_npr=Decimal("1000"),
            duration_value=3, duration_unit="WEEKS", duration_weeks=3,
            registration_deadline=self.today - timedelta(days=1),
        )

    def test_each_filter(self):
        place = self.location.location
        cases = (
            ({"category": self.coffee.parent_id}, ["Physical", "Short"]),
            ({"sub_category": self.coffee.pk}, ["Physical"]),
            ({"mode": "ONLINE"}, ["Online", "Short"]),
            ({"level": "ADVANCED"}, ["Online"]),
            ({"province": place.province_id}, ["Physical"]),
            ({"district": place.district_id}, ["Physical"]),
            ({"municipality": place.pk}, ["Physical"]),
            ({"fee_min": 2000}, ["Online", "Physical"]),
            ({"fee_max": 5000}, ["Online", "Short"]),
            ({"start_from": str(self.today + timedelta(days=45))}, ["Physical"]),
            ({"start_to": str(self.today + timedelta(days=45))}, ["Online", "Short"]),
            ({"duration": "short"}, ["Short"]),
            ({"duration": "mid"}, ["Online"]),
            ({"duration": "long"}, ["Physical"]),
            ({"duration_weeks_min": 8, "duration_weeks_max": 13}, ["Online", "Physical"]),
            ({"institute": self.institute.slug}, ["Online", "Physical", "Short"]),
            ({"registration_open": "true"}, ["Online", "Physical"]),
        )
        for params, expected in cases:
            with self.subTest(params=params):
                self.assertEqual(sorted(titles(self.get(**params))), expected)

    def test_bucket_edges(self):
        for weeks, bucket in ((3, "short"), (4, "mid"), (12, "mid"), (13, "long")):
            with self.subTest(weeks=weeks):
                Training.objects.filter(pk=self.short.pk).update(duration_weeks=weeks)
                self.assertIn("Short", titles(self.get(duration=bucket)))

    def test_ordering(self):
        self.assertEqual(titles(self.get(ordering="-fee_npr")), ["Physical", "Online", "Short"])
        self.assertEqual(titles(self.get(ordering="start_date"))[-1], "Physical")
        self.assertEqual(titles(self.get()), ["Short", "Physical", "Online"])  # newest first


class SearchTests(PublicTrainingTestCase):
    def setUp(self):
        super().setUp()
        self.python = make_training(
            self.institute, title="Python Bootcamp", skills=["Django"],
            short_description="Backend from zero", location=self.location,
        )
        self.python.modules.create(title="Decorators")
        services.refresh_search_vector(self.python)
        self.coffee = make_training(
            self.institute, title="Barista Course", category=make_category("Coffee", "Hospitality"),
            short_description="Espresso basics with Python-free fun", skills=["Latte art"],
        )

    def search(self, text, **params):
        return titles(self.get(search=text, **params))

    def test_matches(self):
        cases = (
            ("pyth boot", ["Python Bootcamp"]),
            ("decor", ["Python Bootcamp"]),
            ("django", ["Python Bootcamp"]),
            ("latte", ["Barista Course"]),
            ("alpha", None),
            ("hospitality", ["Barista Course"]),
            ("coffee", ["Barista Course"]),
            ("municipality", ["Python Bootcamp"]),
            ("backend", ["Python Bootcamp"]),
            ("nothing", []),
            ("'; DROP TABLE x; --", []),
            ("&|!():*", None),
        )
        for text, expected in cases:
            with self.subTest(text=text):
                result = self.search(text)
                if expected is None:
                    self.assertEqual(sorted(result), ["Barista Course", "Python Bootcamp"])
                else:
                    self.assertEqual(result, expected)

    def test_best_match_first(self):
        # "python" is in one title (weight A) and in the other's short description (weight C)
        for text in ("python", "pyth"):
            with self.subTest(text=text):
                self.assertEqual(self.search(text), ["Python Bootcamp", "Barista Course"])

    def test_an_explicit_ordering_replaces_the_rank(self):
        Training.objects.filter(pk=self.coffee.pk).update(fee_npr=1)
        self.assertEqual(self.search("python", ordering="fee_npr"), ["Barista Course", "Python Bootcamp"])


class DetailTests(PublicTrainingTestCase):
    def test_detail_shape(self):
        InstituteContact.objects.create(
            institute=self.institute,
            contact_person="Front desk",
            contact_phone="9800000000",
            contact_email="info@alpha.example",
        )
        self.location.map_url = "https://maps.example/alpha"
        self.location.save()
        training = make_training(self.institute, location=self.location, contact_person="Ram")
        TrainingSession.objects.create(
            training=training, class_days=["SAT"], start_time=time(6), end_time=time(7)
        )
        TrainingSession.objects.filter(training=training, start_time=time(7)).update(
            class_days=["SUN", "MON", "TUE", "WED", "THU", "FRI"]
        )
        training.modules.create(title="Advanced", position=1)
        training.modules.create(title="Basics", position=0)
        training.outcomes.create(text="Two", position=1)
        training.outcomes.create(text="One", position=0)
        data = self.client.get(f"{URL}{training.slug}/").data
        self.assertEqual(
            [(s["class_days_text"], str(s["start_time"])) for s in data["schedule"]],
            [("Sat", "06:00:00"), ("Sun – Fri", "07:00:00")],
        )
        self.assertEqual([m["title"] for m in data["modules"]], ["Basics", "Advanced"])
        self.assertEqual(data["outcomes"], ["One", "Two"])
        self.assertEqual(data["institute"]["name"], "Alpha Institute")
        self.assertEqual(data["location"]["map_url"], "https://maps.example/alpha")
        self.assertEqual(data["location"]["district"], "District")
        self.assertEqual(data["duration"]["text"], "8 weeks")
        self.assertEqual(
            data["contact"],
            {"person": "Ram", "phone": "9800000000", "email": "info@alpha.example"},
        )


class QueryCountTests(PublicTrainingTestCase):
    def test_list_and_detail_cost_a_constant_number_of_queries(self):
        first = make_training(self.institute, location=self.location)
        one = count_queries(lambda: self.client.get(URL))
        detail_one = count_queries(lambda: self.client.get(f"{URL}{first.slug}/"))
        for i in range(14):
            make_training(self.institute, title=f"T{i}", location=self.location)
        self.assertEqual(count_queries(lambda: self.client.get(URL)), one)
        last = Training.objects.latest("pk")
        self.assertEqual(count_queries(lambda: self.client.get(f"{URL}{last.slug}/")), detail_one)
