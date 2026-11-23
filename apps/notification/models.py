from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class Notification(BaseModel):
    """One inbox per row recipient per event. Create it only through `apps.notification.services.notify`."""

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    body = models.CharField(max_length=500, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["recipient", "read_at"], name="notif_recipient_unread_idx"
            ),
            models.Index(
                fields=["recipient", "-created_at"], name="notif_recipient_recent_idx"
            ),
            models.Index(fields=["created_at"], name="notif_created_idx"),  # the purge
        ]

    def __str__(self):
        return f"{self.type} for {self.recipient_id}"


class NotificationDedupe(BaseModel):
    """Remembers that a once-only notification went to a recipient. Kept apart from the inbox
    so the purge never deletes it (a purged milestone would otherwise fire again)."""

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    key = models.CharField(max_length=120)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipient", "key"], name="notif_dedupe_unique"
            )
        ]
