from datetime import time, timedelta
from decimal import Decimal
from io import StringIO
from itertools import product
from unittest import mock

from django.contrib.postgres.search import SearchQuery
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.catalog import services as catalog_services
from apps.institutes import services as institute_services
from apps.institutes.constants import InstituteStatus
from apps.training import services, tasks
from apps.training.api.v1.filters import prefix_query
from apps.training.constants import SEARCH_CONFIG, TrainingStatus
from apps.training.models import Training
from apps.training.tests.helpers import (
    add_location,
    approved_institute,
    make_category,
    make_municipality,
    make_training,
)

S = TrainingStatus
WEEKLY = [{"class_days": ["SUN", "TUE"], "start_time": time(7), "end_time": time(9)}]


def found(text):
    query = SearchQuery(prefix_query(text), config=SEARCH_CONFIG, search_type="raw")
    return list(Training.objects.filter(search_vector=query).values_list("title", flat=True))


class TrainingTestCase(TestCase):
    def setUp(self):
        self.institute, self.owner, self.location = approved_institute()
        self.category = make_category()
        self.today = timezone.localdate()

    def fields(self, **overrides):
        data = dict(
            title="Barista Course",
            category=self.category,
            short_description="Coffee basics",
            mode="ONLINE",
            level="BEGINNER",
            duration_value=6,
            duration_unit="WEEKS",
            fee_npr=Decimal("18500"),
            start_date=self.today + timedelta(days=30),
            end_date=self.today + timedelta(days=72),
        )
        data.update(overrides)
        return data

    def create(self, sessions=WEEKLY, **overrides):
        return services.create_training(self.institute, sessions=sessions, **self.fields(**overrides))

    def status_of(self, training):
        return Training.objects.values_list("status", flat=True).get(pk=training.pk)


class TransitionTableTests(TrainingTestCase):
    def test_every_pair_of_statuses(self):
        for current, target in product(S.TRANSITIONS, S.TRANSITIONS):
            with self.subTest(current=current, target=target):
                training = make_training(self.institute, status=current)
                allowed = target in S.TRANSITIONS[current]
                try:
                    with self.captureOnCommitCallbacks():
                        services._transition(training, target, reason="because")
                except ValidationError:
                    self.assertFalse(allowed)
                else:
                    self.assertTrue(allowed)
                    self.assertEqual(self.status_of(training), target)

    def test_actions_refuse_statuses_outside_their_only_from(self):
        cases = (
            (services.approve, S.UNPUBLISHED, {}),
            (services.approve, S.DRAFT, {}),
            (services.submit, S.APPROVED, {}),
            (services.withdraw, S.APPROVED, {}),
            (services.republish, S.SUBMITTED, {}),
            (services.unpublish, S.SUBMITTED, {}),
            (services.cancel, S.DRAFT, {}),
            (services.reject, S.APPROVED, {"reason": "no"}),
            (services.request_changes, S.UNPUBLISHED, {"reason": "no"}),
        )
        for service, status, kwargs in cases:
            with self.subTest(service=service.__name__, status=status):
                training = make_training(self.institute, status=status)
                with self.assertRaises(ValidationError):
                    service(training, by=self.owner, **kwargs)
                self.assertEqual(self.status_of(training), status)


class ReviewTests(TrainingTestCase):
    def test_reject_and_request_changes_need_a_reason(self):
        for service in (services.reject, services.request_changes):
            with self.subTest(service=service.__name__):
                training = make_training(self.institute, status=S.SUBMITTED)
                with self.assertRaises(ValidationError):
                    service(training, by=self.owner, reason="  ")

    def test_approve_sets_published_at_once_and_clears_feedback(self):
        training = make_training(self.institute, status=S.SUBMITTED, review_feedback="old")
        training = services.approve(training, by=self.owner)
        first = training.published_at
        self.assertIsNotNone(first)
        self.assertEqual(training.review_feedback, "")
        Training.objects.filter(pk=training.pk).update(status=S.SUBMITTED)
        training = services.approve(training, by=self.owner)
        self.assertEqual(training.published_at, first)

    def test_rejecting_stores_the_reason_and_withdrawing_keeps_it(self):
        training = make_training(self.institute, status=S.SUBMITTED)
        services.reject(training, by=self.owner, reason="Fee is unclear")
        services.submit(training, by=self.owner)
        training = services.withdraw(training, by=self.owner)
        self.assertEqual((training.status, training.review_feedback), (S.DRAFT, "Fee is unclear"))


class CreateTests(TrainingTestCase):
    def test_creates_a_draft_with_children_and_derived_weeks(self):
        training = services.create_training(
            self.institute,
            sessions=WEEKLY,
            modules=[{"title": "Espresso"}, {"title": "Milk"}],
            outcomes=[{"text": "Pull a shot"}],
            **self.fields(),
        )
        self.assertEqual(training.status, S.DRAFT)
        self.assertEqual(training.duration_weeks, 6)
        self.assertEqual(
            list(training.modules.values_list("title", "position")),
            [("Espresso", 0), ("Milk", 1)],
        )
        self.assertEqual(training.sessions.get().class_days, ["SUN", "TUE"])

    def test_duration_in_weeks(self):
        cases = ((6, "WEEKS", 6), (2, "MONTHS", 9), (3, "MONTHS", 13), (1, "MONTHS", 4),
                 (10, "DAYS", 1), (3, "DAYS", 1), (None, "", None))
        for value, unit, weeks in cases:
            with self.subTest(value=value, unit=unit):
                self.assertEqual(services.duration_in_weeks(value, unit), weeks)

    def test_a_top_level_category_is_accepted(self):
        training = self.create(category=self.category.parent)
        self.assertEqual(training.category, self.category.parent)

    def test_refused(self):
        other_institute, _, other_location = approved_institute(
            name="Beta", email="beta@example.com", code=2
        )
        retired = make_category("Retired", parent="Old")
        retired.is_active = False
        retired.save()
        orphan = make_category("Orphan", parent="Gone")
        orphan.parent.is_active = False
        orphan.parent.save()
        inactive_location = add_location(self.institute, make_municipality(3, "M3"), is_active=False)
        cases = {
            "inactive category": dict(category=retired),
            "sub-category of an inactive parent": dict(category=orphan),
            "another institute's location": dict(mode="PHYSICAL", institute_location=other_location),
            "inactive location": dict(mode="PHYSICAL", institute_location=inactive_location),
            "online with a location": dict(institute_location=self.location),
            "end before start": dict(end_date=self.today),
            "deadline after start": dict(registration_deadline=self.today + timedelta(days=31)),
        }
        for label, overrides in cases.items():
            with self.subTest(label):
                with self.assertRaises(ValidationError):
                    self.create(**overrides)
        self.assertFalse(Training.objects.filter(institute=self.institute).exists())
        self.assertFalse(other_institute.trainings.exists())

    def test_refused_for_an_institute_that_is_not_approved(self):
        for status in (InstituteStatus.PENDING, InstituteStatus.SUSPENDED):
            with self.subTest(status=status):
                self.institute.status = status
                self.institute.save()
                with self.assertRaises(ValidationError):
                    self.create()

    def test_bad_sessions_are_refused(self):
        for sessions in (
            [{"class_days": [], "start_time": time(7), "end_time": time(9)}],
            [{"class_days": ["SUN", "SUN"], "start_time": time(7), "end_time": time(9)}],
            [{"class_days": ["SUN"], "start_time": time(9), "end_time": time(9)}],
        ):
            with self.subTest(sessions=sessions):
                with self.assertRaises(ValidationError):
                    self.create(sessions=sessions)


class EditTests(TrainingTestCase):
    def test_editable_statuses_keep_their_status(self):
        for status in S.EDITABLE:
            with self.subTest(status=status):
                training = make_training(self.institute, status=status)
                training = services.update_training(training, title="New title")
                self.assertEqual((training.status, training.title), (status, "New title"))

    def test_editing_a_published_training_sends_it_back_to_review(self):
        for status in S.REVIEWED_EDIT:
            with self.subTest(status=status):
                training = make_training(self.institute, status=status)
                training = services.update_training(training, fee_npr=Decimal("1000"))
                self.assertEqual(training.status, S.SUBMITTED)

    def test_an_incomplete_edit_of_a_published_training_is_refused_and_rolled_back(self):
        training = make_training(self.institute, status=S.APPROVED)
        with self.assertRaises(ValidationError):
            services.update_training(training, title="Changed", short_description="")
        training.refresh_from_db()
        self.assertEqual((training.status, training.title), (S.APPROVED, "Python Bootcamp"))

    def test_some_statuses_cannot_be_edited(self):
        for status in (S.SUBMITTED, S.CANCELLED, S.EXPIRED):
            with self.subTest(status=status):
                training = make_training(self.institute, status=status)
                with self.assertRaises(ValidationError):
                    services.update_training(training, title="x")

    def test_switching_to_online_clears_the_location(self):
        training = make_training(self.institute, status=S.DRAFT, location=self.location)
        training = services.update_training(training, mode="ONLINE")
        self.assertIsNone(training.institute_location)

    def test_changing_the_unit_recomputes_the_weeks(self):
        training = make_training(self.institute, status=S.DRAFT)
        training = services.update_training(training, duration_unit="MONTHS")
        self.assertEqual(training.duration_weeks, 34)

    def test_children_are_replaced_as_a_set(self):
        training = make_training(self.institute, status=S.DRAFT)
        services.update_training(training, modules=[{"title": "A"}, {"title": "B"}])
        services.update_training(training, title="kept")  # None keeps them
        self.assertEqual(training.modules.count(), 2)
        services.update_training(training, modules=[])
        self.assertEqual(training.modules.count(), 0)
        self.assertEqual(training.sessions.count(), 1)

    def test_only_a_draft_can_be_deleted(self):
        submitted = make_training(self.institute, status=S.SUBMITTED)
        with self.assertRaises(ValidationError):
            services.delete_training(submitted)
        draft = make_training(self.institute, status=S.DRAFT)
        services.delete_training(draft)
        self.assertFalse(Training.objects.filter(pk=draft.pk).exists())


class SubmitTests(TrainingTestCase):
    def test_every_missing_field_is_reported_at_once(self):
        training = services.create_training(
            self.institute, title="Empty", category=self.category, mode="PHYSICAL"
        )
        with self.assertRaises(ValidationError) as caught:
            services.submit(training, by=self.owner)
        self.assertEqual(
            set(caught.exception.message_dict),
            {"short_description", "level", "duration_value", "duration_unit", "fee_npr",
             "start_date", "end_date", "institute_location", "sessions"},
        )

    def test_a_start_date_in_the_past_is_refused(self):
        training = self.create(
            start_date=self.today - timedelta(days=1), end_date=self.today + timedelta(days=5)
        )
        with self.assertRaises(ValidationError):
            services.submit(training, by=self.owner)

    def test_a_free_training_can_be_submitted(self):
        training = services.submit(self.create(fee_npr=Decimal("0")), by=self.owner)
        self.assertEqual(training.status, S.SUBMITTED)

    def test_a_suspended_institute_cannot_submit_or_republish(self):
        draft = self.create()
        unpublished = make_training(self.institute, status=S.UNPUBLISHED)
        self.institute.status = InstituteStatus.SUSPENDED
        self.institute.save()
        for service, training in ((services.submit, draft), (services.republish, unpublished)):
            with self.subTest(service=service.__name__):
                with self.assertRaises(ValidationError):
                    service(training, by=self.owner)

    def test_unpublish_and_republish_need_no_review_and_cancel_is_final(self):
        training = make_training(self.institute, status=S.APPROVED)
        self.assertEqual(services.unpublish(training, by=self.owner).status, S.UNPUBLISHED)
        self.assertEqual(services.republish(training, by=self.owner).status, S.APPROVED)
        self.assertEqual(services.cancel(training, by=self.owner).status, S.CANCELLED)
        self.assertEqual(S.TRANSITIONS[S.CANCELLED], set())


class ExpiryTests(TrainingTestCase):
    def test_expires_live_trainings_after_their_end_date(self):
        yesterday = self.today - timedelta(days=1)
        past = dict(start_date=self.today - timedelta(days=30), end_date=yesterday,
                    registration_deadline=None)
        approved = make_training(self.institute, status=S.APPROVED, **past)
        unpublished = make_training(self.institute, status=S.UNPUBLISHED, **past)
        draft = make_training(self.institute, status=S.DRAFT, **past)
        cancelled = make_training(self.institute, status=S.CANCELLED, **past)
        ends_today = make_training(self.institute, status=S.APPROVED, end_date=self.today,
                                   start_date=self.today - timedelta(days=3), registration_deadline=None)
        self.assertEqual(services.expire_trainings(), 2)
        self.assertEqual(
            [self.status_of(t) for t in (approved, unpublished, draft, cancelled, ends_today)],
            [S.EXPIRED, S.EXPIRED, S.DRAFT, S.CANCELLED, S.APPROVED],
        )
        self.assertEqual(services.expire_trainings(), 0)

    def test_the_command_prints_the_count(self):
        out = StringIO()
        call_command("expire_trainings", stdout=out)
        self.assertIn("Expired 0 training(s)", out.getvalue())


class SearchVectorTests(TrainingTestCase):
    def test_found_by_each_part(self):
        training = make_training(
            self.institute,
            status=S.DRAFT,
            location=self.location,
            title="Barista Bootcamp",
            short_description="Espresso and latte art",
            skills=["Steaming"],
        )
        services.update_training(training, modules=[{"title": "Grinding"}])
        for text in ("bari", "barista boot", "steam", "latte", "Municipality", "District",
                     "Alpha", "Technology", "Python", "grind"):
            with self.subTest(text=text):
                self.assertEqual(found(text), ["Barista Bootcamp"])
        self.assertEqual(found("nothing-like-this"), [])

    def test_follows_an_institute_rename(self):
        make_training(self.institute)
        with mock.patch("apps.institutes.services.async_task") as task, self.captureOnCommitCallbacks(
            execute=True
        ):
            institute_services.update_profile(self.institute, name="Zenith Academy")
        task.assert_called_once_with(
            "apps.training.tasks.refresh_institute_trainings", self.institute.pk, save=False
        )
        tasks.refresh_institute_trainings(self.institute.pk)
        self.assertEqual(found("zenith"), ["Python Bootcamp"])

    def test_follows_a_category_rename_or_move(self):
        make_training(self.institute, category=self.category)
        with mock.patch("apps.catalog.services.async_task"):
            catalog_services.update_category(self.category.parent, name="Computing")
        tasks.refresh_category_trainings(self.category.parent_id)
        self.assertEqual(found("computing"), ["Python Bootcamp"])

    def test_follows_a_location_change(self):
        make_training(self.institute, location=self.location)
        other = make_municipality(5, "Pokhara")
        with mock.patch("apps.institutes.services.async_task") as task, self.captureOnCommitCallbacks(
            execute=True
        ):
            institute_services.update_location(self.location, location=other)
        task.assert_called_once()
        tasks.refresh_location_trainings(self.location.pk)
        self.assertEqual(found("pokhara"), ["Python Bootcamp"])


class DeactivateLocationTests(TrainingTestCase):
    def test_refused_while_a_live_training_uses_it(self):
        branch = add_location(self.institute, make_municipality(4, "Branch"))
        training = make_training(self.institute, status=S.APPROVED, location=branch)
        with self.assertRaises(ValidationError):
            institute_services.deactivate_location(branch)
        services.cancel(training, by=self.owner)
        location = institute_services.deactivate_location(branch)
        self.assertFalse(location.is_active)
