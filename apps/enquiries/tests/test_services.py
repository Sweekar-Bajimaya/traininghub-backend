import threading
from datetime import timedelta
from unittest import mock

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import connections
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from apps.common.exceptions import TooManyRequests
from apps.enquiries import services
from apps.enquiries.constants import (
    MY_ENQUIRIES_DAYS,
    PHONE_DAILY_LIMIT,
    EnquiryStatus,
    EnquiryType,
)
from apps.enquiries.models import Enquiry
from apps.enquiries.tests.helpers import (
    approved_institute,
    make_enquiry,
    make_training,
    new_token,
    next_phone,
    reset_limits,
)
from apps.institutes.constants import InstituteStatus
from apps.institutes.models import Institute
from apps.training import services as training_services
from apps.training.constants import TrainingStatus
from apps.training.models import Training

S = EnquiryStatus


def submit(training, **overrides):
    fields = dict(
        training=training, name="Ram Sharma", phone=next_phone(), device_token=new_token()
    )
    fields.update(overrides)
    return services.submit_enquiry(**fields)


class ServiceTestCase(TestCase):
    def setUp(self):
        reset_limits()
        self.institute, self.owner, _ = approved_institute()
        self.training = make_training(self.institute)


class SubmitTests(ServiceTestCase):
    def test_creates_an_open_enquiry_for_the_trainings_institute(self):
        token = new_token()
        enquiry = submit(self.training, device_token=token, email="a@b.com", message="Hi")
        enquiry.refresh_from_db()
        self.assertEqual(enquiry.institute_id, self.institute.pk)
        self.assertEqual(enquiry.status, S.NEW)
        self.assertEqual(enquiry.type, EnquiryType.ENQUIRY)
        self.assertEqual(str(enquiry.device_token), token)
        self.assertEqual((enquiry.email, enquiry.message), ("a@b.com", "Hi"))

    def test_a_training_that_is_not_published_takes_no_enquiry(self):
        for status in (
            TrainingStatus.DRAFT,
            TrainingStatus.SUBMITTED,
            TrainingStatus.UNPUBLISHED,
            TrainingStatus.CANCELLED,
            TrainingStatus.EXPIRED,
        ):
            for kind in EnquiryType.VALUES:  # an interest does not get round it either
                with self.subTest(status=status, type=kind):
                    training = make_training(self.institute, status=status)
                    with self.assertRaises(ValidationError):
                        submit(training, type=kind)
        self.assertFalse(Enquiry.objects.exists())

    def test_an_institute_that_is_not_approved_takes_no_enquiry(self):
        Institute.objects.filter(pk=self.institute.pk).update(status=InstituteStatus.SUSPENDED)
        training = Training.objects.select_related("institute").get(pk=self.training.pk)
        with self.assertRaises(ValidationError):
            submit(training)

    def test_closed_registration_refuses_an_enquiry_but_not_an_interest(self):
        today = timezone.localdate()
        past_deadline = make_training(
            self.institute,
            registration_deadline=today - timedelta(days=1),
            start_date=today + timedelta(days=10),
        )
        started_no_deadline = make_training(
            self.institute,
            registration_deadline=None,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
        )
        for training in (past_deadline, started_no_deadline):
            with self.subTest(training=training.pk):
                with self.assertRaisesMessage(ValidationError, "closed"):
                    submit(training)
                self.assertEqual(
                    submit(training, type=EnquiryType.INTEREST).type, EnquiryType.INTEREST
                )

    def test_registration_is_open_until_the_deadline_or_the_start_date(self):
        today = timezone.localdate()
        on_deadline = make_training(
            self.institute, registration_deadline=today, start_date=today + timedelta(days=5)
        )
        starts_today = make_training(
            self.institute,
            registration_deadline=None,
            start_date=today,
            end_date=today + timedelta(days=30),
        )
        submit(on_deadline)
        submit(starts_today)

    def test_full_training_refuses_an_enquiry_but_not_an_interest(self):
        training = make_training(self.institute, seats=1)
        make_enquiry(training, status=S.CONVERTED)
        with self.assertRaisesMessage(ValidationError, "full"):
            submit(training)
        submit(training, type=EnquiryType.INTEREST)

    def test_seats_count_only_converted_enquiries(self):
        training = make_training(self.institute, seats=2)
        make_enquiry(training, status=S.CONVERTED)
        for status in (S.NEW, S.CONTACTED, S.INTERESTED, S.NOT_INTERESTED, S.CLOSED):
            make_enquiry(training, status=status)
        submit(training)  # one seat left

    def test_no_seat_count_means_unlimited(self):
        for _ in range(3):
            make_enquiry(self.training, status=S.CONVERTED)
        submit(self.training)

    def test_a_phone_number_has_one_open_enquiry_per_training(self):
        phone = next_phone()
        first = submit(self.training, phone=phone)
        for kind in EnquiryType.VALUES:
            with self.subTest(type=kind), self.assertRaisesMessage(ValidationError, "already"):
                submit(self.training, phone=phone, type=kind)
        Enquiry.objects.filter(pk=first.pk).update(status=S.CLOSED)
        submit(self.training, phone=phone)  # the earlier one is closed
        submit(make_training(self.institute, title="Other"), phone=phone)  # another training

    def test_the_database_decides_when_two_submits_race(self):
        phone = next_phone()

        def rival_gets_in_first(_phone):
            make_enquiry(self.training, phone=phone)

        with mock.patch.object(services, "_claim_phone_slot", side_effect=rival_gets_in_first):
            with self.assertRaisesMessage(ValidationError, "already"):
                submit(self.training, phone=phone)
        self.assertEqual(Enquiry.objects.filter(phone=phone).count(), 1)

    def test_a_phone_number_has_a_daily_allowance(self):
        phone = next_phone()
        trainings = [
            make_training(self.institute, title=f"Course {n}")
            for n in range(PHONE_DAILY_LIMIT + 1)
        ]
        for training in trainings[:PHONE_DAILY_LIMIT]:
            submit(training, phone=phone)
        with self.assertRaises(TooManyRequests) as caught:
            submit(trainings[-1], phone=phone)
        self.assertGreater(caught.exception.wait, 0)
        self.assertFalse(Enquiry.objects.filter(training=trainings[-1]).exists())
        submit(trainings[-1], phone=next_phone())  # another number is not affected

    def test_a_refused_enquiry_does_not_use_the_allowance(self):
        phone = next_phone()
        submit(self.training, phone=phone)
        for _ in range(PHONE_DAILY_LIMIT + 2):  # duplicates are refused before they are counted
            with self.assertRaises(ValidationError):
                submit(self.training, phone=phone)
        self.assertEqual(cache.get(f"enquiry_phone_{phone}"), 1)


class ChangeStatusTests(ServiceTestCase):
    def change(self, enquiry, status):
        return services.change_status(enquiry, status=status, by=self.owner)

    def test_any_status_moves_to_any_other(self):
        enquiry = make_enquiry(self.training)
        for target in S.VALUES:
            for start in S.VALUES:
                with self.subTest(start=start, target=target):
                    Enquiry.objects.filter(pk=enquiry.pk).update(status=start)
                    self.assertEqual(self.change(enquiry, target).status, target)
                    enquiry.refresh_from_db()
                    self.assertEqual(enquiry.status, target)

    def test_an_unknown_status_is_refused(self):
        enquiry = make_enquiry(self.training)
        with self.assertRaises(ValidationError):
            self.change(enquiry, "WON")

    def test_the_same_status_changes_nothing(self):
        training = make_training(self.institute, seats=1)
        enquiry = make_enquiry(training, status=S.CONVERTED)
        before = Enquiry.objects.get(pk=enquiry.pk).modified_at
        self.change(enquiry, S.CONVERTED)  # fine even though the seats are all taken
        self.assertEqual(Enquiry.objects.get(pk=enquiry.pk).modified_at, before)

    def test_a_change_updates_modified_at(self):
        enquiry = make_enquiry(self.training)
        before = enquiry.modified_at
        self.change(enquiry, S.CONTACTED)
        self.assertGreater(Enquiry.objects.get(pk=enquiry.pk).modified_at, before)

    def test_converted_stops_at_the_seats(self):
        training = make_training(self.institute, seats=2)
        first, second, third = (make_enquiry(training) for _ in range(3))
        self.change(first, S.CONVERTED)
        self.change(second, S.CONVERTED)
        with self.assertRaisesMessage(ValidationError, "seats"):
            self.change(third, S.CONVERTED)
        third.refresh_from_db()
        self.assertEqual(third.status, S.NEW)

    def test_leaving_converted_frees_the_seat(self):
        training = make_training(self.institute, seats=1)
        first, second = make_enquiry(training), make_enquiry(training)
        self.change(first, S.CONVERTED)
        with self.assertRaises(ValidationError):
            self.change(second, S.CONVERTED)
        self.change(first, S.CLOSED)
        self.change(second, S.CONVERTED)

    def test_no_seat_count_means_any_number_can_convert(self):
        for _ in range(4):
            self.change(make_enquiry(self.training), S.CONVERTED)

    def test_other_trainings_do_not_use_up_the_seats(self):
        training = make_training(self.institute, seats=1)
        make_enquiry(self.training, status=S.CONVERTED)
        self.change(make_enquiry(training), S.CONVERTED)

    def test_reopening_next_to_another_open_enquiry_is_refused(self):
        phone = next_phone()
        closed = make_enquiry(self.training, phone=phone, status=S.CLOSED)
        make_enquiry(self.training, phone=phone)  # the open one
        with self.assertRaisesMessage(ValidationError, "open enquiry"):
            self.change(closed, S.FOLLOW_UP)
        closed.refresh_from_db()
        self.assertEqual(closed.status, S.CLOSED)
        self.change(closed, S.NOT_INTERESTED)  # a closed status is still fine


class SeatRaceTests(TransactionTestCase):
    """Real transactions on separate connections: the last seat goes to one member of staff."""

    def test_only_one_of_two_simultaneous_conversions_takes_the_last_seat(self):
        institute, owner, _ = approved_institute()
        training = make_training(institute, seats=1)
        enquiries = [make_enquiry(training) for _ in range(2)]
        barrier = threading.Barrier(2)
        outcomes = []

        def convert(enquiry):
            try:
                barrier.wait(timeout=10)
                services.change_status(enquiry, status=S.CONVERTED, by=owner)
                outcomes.append("converted")
            except ValidationError:
                outcomes.append("refused")
            finally:
                connections.close_all()

        threads = [threading.Thread(target=convert, args=(e,)) for e in enquiries]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)
        self.assertCountEqual(outcomes, ["converted", "refused"])
        self.assertEqual(Enquiry.objects.filter(status=S.CONVERTED).count(), 1)


class NoteTests(ServiceTestCase):
    def test_a_note_is_saved_trimmed_with_its_author(self):
        enquiry = make_enquiry(self.training)
        note = services.add_note(enquiry=enquiry, author=self.owner, text="  Called at 2 PM  ")
        note.refresh_from_db()
        self.assertEqual((note.text, note.author, note.enquiry), ("Called at 2 PM", self.owner, enquiry))


class SummaryTests(ServiceTestCase):
    def test_counts_every_status_even_when_zero(self):
        make_enquiry(self.training, phone="9841111111")
        make_enquiry(self.training, phone="9841111111", status=S.CLOSED)  # same person twice
        make_enquiry(self.training, status=S.CONVERTED)
        counts = services.summary(Enquiry.objects.all())
        self.assertEqual((counts["total"], counts["new"], counts["unique_phones"]), (3, 1, 2))
        self.assertEqual(list(counts["by_status"]), list(S.VALUES))
        self.assertEqual(counts["by_status"][S.NEW], 1)
        self.assertEqual(counts["by_status"][S.CLOSED], 1)
        self.assertEqual(counts["by_status"][S.CONVERTED], 1)
        self.assertEqual(counts["by_status"][S.CONTACTED], 0)

    def test_an_empty_queryset_is_all_zeros(self):
        counts = services.summary(Enquiry.objects.none())
        self.assertEqual((counts["total"], counts["new"], counts["unique_phones"]), (0, 0, 0))
        self.assertEqual(set(counts["by_status"].values()), {0})


class DeviceEnquiriesTests(ServiceTestCase):
    def test_a_device_sees_only_its_own_from_the_last_90_days_newest_first(self):
        token = new_token()
        old = make_enquiry(self.training, device_token=token)
        recent = make_enquiry(self.training, device_token=token)
        newest = make_enquiry(self.training, device_token=token)
        edge = make_enquiry(self.training, device_token=token)
        make_enquiry(self.training)  # someone else's
        now = timezone.now()
        for enquiry, days in ((old, MY_ENQUIRIES_DAYS + 1), (recent, 30), (newest, 1), (edge, MY_ENQUIRIES_DAYS - 1)):
            Enquiry.objects.filter(pk=enquiry.pk).update(created_at=now - timedelta(days=days))
        found = list(services.device_enquiries(token))
        self.assertEqual([e.pk for e in found], [newest.pk, recent.pk, edge.pk])


class DeleteTrainingTests(ServiceTestCase):
    def test_a_draft_with_enquiries_cannot_be_deleted(self):
        make_enquiry(self.training)  # it was live, took an enquiry, then went back to a draft
        Training.objects.filter(pk=self.training.pk).update(status=TrainingStatus.DRAFT)
        training = Training.objects.get(pk=self.training.pk)
        with self.assertRaisesMessage(ValidationError, "enquiries"):
            training_services.delete_training(training)
        self.assertTrue(Training.objects.filter(pk=training.pk).exists())

    def test_a_draft_without_enquiries_still_deletes(self):
        draft = make_training(self.institute, status=TrainingStatus.DRAFT)
        training_services.delete_training(draft)
        self.assertFalse(Training.objects.filter(pk=draft.pk).exists())
