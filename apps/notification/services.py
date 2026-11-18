import logging
from datetime import timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django_q.tasks import async_task

from apps.notification.constants import RETENTION_ANY_DAYS, RETENTION_READ_DAYS, Channel
from apps.notification.models import Notification, NotificationDedupe
from apps.notification.registry import EVENTS

logger = logging.getLogger(__name__)


def claim(recipient, key):
    """True the first time a recipient claims `key` False Afterwards.
    The unique so that two requests at once cannot be true."""
    _, created = NotificationDedupe.objects.get_or_create(recipient=recipient, key=key)
    return created


def mark_seen(recipients, key):
    """Record `key` for each recipient without sending anything (the lower milestones)."""
    for user in recipients:
        claim(user, key)


def notify(event, *, recipients, payload, dedupe_key=""):
    """Create one in-app row per recipient and queue the email if the event has that channel.

    Call it from a service, after the state change. A database failure is logged and swallowed:
    the rows are written in a savepoint, so the caller's transaction stays usable. The email is
    queued after the outer transaction commits. With `dedupe_key`, a recipient who already
    claimed the key is skipped."""

    spec = EVENTS[event]
    title, body = spec.render(payload)
    recipients = list(recipients)
    try:
        with transaction.atomic():
            rows = [
                Notification(
                    recipient=user, type=event, title=title, body=body, payload=payload
                )
                for user in recipients
                if not dedupe_key or claim(user, dedupe_key)
            ]
            created = Notification.objects.bulk_create(rows)
    except Exception:
        logger.exception("Could not create %s notifications", event)
        return []

    if Channel.EMAIL in spec.channels and created:
        ids = [row.pk for row in created]

        def queue_emails():
            for pk in ids:
                async_task(
                    "apps.notification.tasks.send_notification_email", pk, save=False
                )

        transaction.on_commit(queue_emails)
    return created


def unread_count(user):
    return Notification.objects.filter(recipient=user, read_at__is_null=True).count()


def mark_read(notification):
    now = timezone.now()
    Notification.objects.filter(pk=notification.pk, read_at__isnull=True).update(
        read_at=now, modified_at=now
    )


def mark_all_read(user):
    now = timezone.now()
    return Notification.objects.filter(recipient=user, read_at__isnull=True).update(
        read_at=now, modified_at=now
    )


def purge_old(*, now=None):
    """Delete read rows older than RETENTION_READ_DAYS and any row older than RETENTION_ANY_DAYS.
    The dedupe records are kept on purpose."""
    now = now or timezone.now()
    deleted, _ = Notification.objects.filter(
        Q(read_at__lt=now - timedelta(days=RETENTION_READ_DAYS))
        | Q(created_at__lt=now - timedelta(days=RETENTION_ANY_DAYS))
    ).delete()
    return deleted
