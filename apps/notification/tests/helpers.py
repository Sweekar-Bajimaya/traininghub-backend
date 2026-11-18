from datetime import timedelta
from unittest import mock

from django.utils import timezone

from apps.notification.constants import EventType
from apps.notification.models import Notification
from apps.training.tests.helpers import (  # noqa: F401  (re-exported for these tests)
    approved_institute,
    make_admin,
    reset_throttles,
)


class NoQueueMixin:
    """Put this first in the bases of a TestCase."""

    def setUp(self):
        super().setUp()
        patcher = mock.patch("apps.notification.services.async_task")
        self.queued = patcher.start()
        self.addCleanup(patcher.stop)


def make_row(
    user, *, created_days_ago=0, read_days_ago=None, type=EventType.INSTITUTE_APPROVED
):
    """Write an inbox row directly, with the dates moved back (created_at is auto_now_add)."""
    now = timezone.now()
    row = Notification.objects.create(recipient=user, type=type, title="Title")
    Notification.objects.filter(pk=row.pk).update(
        created_at=now - timedelta(days=created_days_ago),
        read_at=None if read_days_ago is None else now - timedelta(days=read_days_ago),
    )
    return row
