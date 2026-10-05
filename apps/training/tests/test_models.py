from datetime import time, timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from apps.training.models import Training, TrainingSession
from apps.training.tests.helpers import approved_institute, make_category


class TrainingConstraintTests(TestCase):
    def setUp(self):
        self.institute, _, self.location = approved_institute()
        self.category = make_category()
        self.today = timezone.localdate()

    def create(self, **fields):
        data = dict(institute=self.institute, category=self.category, title="T", mode="ONLINE")
        data.update(fields)
        return Training.objects.create(**data)

    def assertRejected(self, **fields):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.create(**fields)

    def test_a_draft_with_only_the_required_fields_saves(self):
        training = self.create()
        self.assertEqual(training.status, "DRAFT")
        self.assertEqual(training.skills, [])

    def test_online_training_cannot_have_a_location(self):
        self.assertRejected(institute_location=self.location)

    def test_end_before_start_is_rejected(self):
        self.assertRejected(start_date=self.today, end_date=self.today - timedelta(days=1))

    def test_deadline_after_start_is_rejected(self):
        self.assertRejected(
            start_date=self.today, registration_deadline=self.today + timedelta(days=1)
        )

    def test_negative_fee_is_rejected(self):
        self.assertRejected(fee_npr=-1)

    def test_zero_seats_is_rejected(self):
        self.assertRejected(seats=0)

    def test_zero_duration_is_rejected(self):
        self.assertRejected(duration_value=0, duration_unit="WEEKS")

    def test_a_duration_needs_a_unit(self):
        self.assertRejected(duration_value=4)


class TrainingSessionConstraintTests(TestCase):
    def setUp(self):
        institute, _, _ = approved_institute()
        self.training = Training.objects.create(
            institute=institute, category=make_category(), title="T", mode="ONLINE"
        )

    def test_a_session_must_end_after_it_starts(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            TrainingSession.objects.create(
                training=self.training, class_days=["SUN"], start_time=time(9), end_time=time(8)
            )
