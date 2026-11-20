from django.test import TestCase

from apps.notification import services
from apps.notification.models import Notification, NotificationDedupe
from apps.notification.tests.helpers import approved_institute, make_row


class PurgeTests(TestCase):
    def setUp(self):
        _, self.owner, _ = approved_institute()

    def test_old_read_rows_and_very_old_rows_go(self):
        old_read = make_row(self.owner, created_days_ago=100, read_days_ago=91)
        very_old = make_row(self.owner, created_days_ago=181)
        self.assertEqual(services.purge_old(), 2)
        self.assertFalse(
            Notification.objects.filter(pk__in=[old_read.pk, very_old.pk]).exists()
        )

    def test_recent_rows_and_unread_rows_stay(self):
        recent = make_row(self.owner)
        recent_read = make_row(self.owner, created_days_ago=10, read_days_ago=5)
        unread_old = make_row(
            self.owner, created_days_ago=100
        )  # unread: kept until 180 days
        self.assertEqual(services.purge_old(), 0)
        self.assertEqual(
            Notification.objects.filter(
                pk__in=[recent.pk, recent_read.pk, unread_old.pk]
            ).count(),
            3,
        )

    def test_the_dedupe_records_are_never_purged(self):
        NotificationDedupe.objects.create(
            recipient=self.owner, key="milestone:enquiries:1:10"
        )
        make_row(self.owner, created_days_ago=400)
        services.purge_old()
        self.assertEqual(NotificationDedupe.objects.count(), 1)
