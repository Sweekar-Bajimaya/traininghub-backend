import logging

from apps.notification import emails, services
from apps.notification.models import Notification

logger = logging.getLogger(__name__)


def send_notification_email(notification_id):
    try:
        notification = Notification.objects.select_related("recipient").get(
            pk=notification_id
        )
    except Notification.DoesNotExist:
        return  # purged, or its transaction rolled back
    try:
        emails.send(notification)
    except Exception:
        logger.exception("Failed to email notification %s", notification_id)


def purge_notifications():
    """Schedule daily (Django admin > Django Q > Scheduled tasks)."""
    return services.purge_old()
