from django.test import TestCase

from apps.enquiries import services
from apps.enquiries.constants import EnquiryStatus, EnquiryType
from apps.enquiries.models import Enquiry
from apps.enquiries.tests.helpers import make_enquiry, next_phone, reset_limits
from apps.notification.constants import EventType
from apps.notification.models import Notification, NotificationDedupe
from apps.notification.tests.helpers import NoQueueMixin, approved_institute
from apps.training.models import Training
from apps.training.tests.helpers import make_training


class EnquiryEventTests(NoQueueMixin, TestCase):
    def setUp(self):
        super().setUp()
        reset_limits()
        self.institute, self.owner, _ = approved_institute()
        self.training = make_training(self.institute)

    def submit(self, **overrides):
        return services.submit_enquiry(
            training=self.training, name="Ram", phone=next_phone(), **overrides
        )

    def count(self, event):
        return Notification.objects.filter(
            type=event
        ).count()  # a fresh query each time

    def test_a_new_enquiry_tells_the_staff(self):
        self.submit()
        row = Notification.objects.get(recipient=self.owner, type=EventType.ENQUIRY_NEW)
        self.assertEqual(row.payload["kind"], "enquiry")
        self.assertEqual(row.payload["name"], "Ram")

    def test_an_interest_is_worded_as_one(self):
        self.submit(type=EnquiryType.INTEREST)
        row = Notification.objects.get(recipient=self.owner, type=EventType.ENQUIRY_NEW)
        self.assertEqual(row.payload["kind"], "interest")

    def test_a_milestone_fires_once_and_only_for_the_highest(self):
        for _ in range(59):
            make_enquiry(self.training)  # written directly: no notifications
        self.submit()  # the 60th
        thresholds = list(
            Notification.objects.filter(type=EventType.MILESTONE_ENQUIRIES).values_list(
                "payload__threshold", flat=True
            )
        )
        self.assertEqual(thresholds, [50])
        keys = NotificationDedupe.objects.filter(key__startswith="milestone:enquiries:")
        self.assertEqual(keys.count(), 3)  # 10 and 25 recorded silently, 50 fired
        self.submit()  # the 61st
        self.assertEqual(self.count(EventType.MILESTONE_ENQUIRIES), 1)

    def test_the_person_who_converts_is_not_told(self):
        enquiry = make_enquiry(self.training)
        services.change_status(enquiry, status=EnquiryStatus.CONVERTED, by=self.owner)
        # the owner is the only member and made the change
        self.assertEqual(self.count(EventType.ENQUIRY_CONVERTED), 0)

    def test_filling_half_the_seats_fires_a_milestone_once(self):
        Training.objects.filter(pk=self.training.pk).update(seats=4)
        for _ in range(3):
            services.change_status(
                make_enquiry(self.training),
                status=EnquiryStatus.CONVERTED,
                by=self.owner,
            )
        rows = Notification.objects.filter(type=EventType.MILESTONE_CONVERTED)
        self.assertEqual(
            [row.payload["percent"] for row in rows], [50]
        )  # 2 of 4 fired it; the 3rd did not repeat it

    def test_a_failed_notification_does_not_lose_the_enquiry(self):
        from unittest import mock

        with mock.patch(
            "apps.notification.services.Notification.objects.bulk_create",
            side_effect=Exception("boom"),
        ):
            # notify() logs the failure and swallows it (captured, so no traceback in the run)
            with self.assertLogs("apps.notification.services", level="ERROR"):
                enquiry = self.submit()
        self.assertTrue(Enquiry.objects.filter(pk=enquiry.pk).exists())
