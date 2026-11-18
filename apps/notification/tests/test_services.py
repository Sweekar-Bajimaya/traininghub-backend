from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.notification import services
from apps.notification.constants import EventType
from apps.notification.models import Notification
from apps.notification.registry import EVENTS, IN_APP, Event
from apps.notification.tests.helpers import NoQueueMixin, approved_institute, make_admin

User = get_user_model()
PAYLOAD = {"institute_name": "Alpha", "institute_slug": "alpha", "reason": ""}


class NotifyTests(NoQueueMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.institute, self.owner, _ = approved_institute()
        self.admin = make_admin("a@example.com")

    def test_one_row_per_recipient(self):
        rows = services.notify(
            EventType.INSTITUTE_APPROVED, recipients=[self.owner, self.admin], payload=PAYLOAD
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(Notification.objects.filter(type=EventType.INSTITUTE_APPROVED).count(), 2)

    def test_email_is_queued_after_commit_and_only_for_email_events(self):
        with self.captureOnCommitCallbacks(execute=True):
            services.notify(EventType.INSTITUTE_APPROVED, recipients=[self.owner], payload=PAYLOAD)
            services.notify(
                EventType.ADMIN_ACCOUNT_CREATED, recipients=[self.admin], payload={"full_name": "A"}
            )
        self.queued.assert_called_once()  # the admin event is in-app only

    def test_a_dedupe_key_sends_once(self):
        payload = {"training_title": "T", "training_slug": "t", "threshold": 10}
        for _ in range(2):
            services.notify(
                EventType.MILESTONE_ENQUIRIES,
                recipients=[self.owner],
                payload=payload,
                dedupe_key="milestone:enquiries:1:10",
            )
        self.assertEqual(Notification.objects.filter(type=EventType.MILESTONE_ENQUIRIES).count(), 1)

    def test_a_failed_insert_leaves_the_callers_transaction_usable(self):
        bad_type = "x" * 60  # longer than the column, so the database refuses the row
        with mock.patch.dict(EVENTS, {bad_type: Event(IN_APP, "Title")}):
            self.assertEqual(services.notify(bad_type, recipients=[self.owner], payload={}), [])
        self.assertTrue(User.objects.exists())  # raises if the transaction were broken

    def test_an_unknown_event_type_raises(self):
        with self.assertRaises(KeyError):
            services.notify("nope", recipients=[self.owner], payload={})