from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel
from apps.enquiries.constants import (
    MESSAGE_MAX_LENGTH,
    EnquiryStatus,
    EnquiryType,
    PreferredTime,
)
from apps.enquiries.validators import PHONE_DB_REGEX
from apps.institutes.models import Institute
from apps.training.models import Training


class Enquiry(BaseModel):
    """A visitor's question about a training, sent without an account. Create it through
    `apps.enquiries.services.submit_enquiry` (it checks the training and the limits) and move it
    through `change_status` (it guards the seats)."""

    training = models.ForeignKey(
        Training, on_delete=models.PROTECT, related_name="enquiries"
    )
    # copied from the training, so the portal scopes on it like every other institute table; the
    # service is the only writer, so the two cannot disagree
    institute = models.ForeignKey(
        Institute, on_delete=models.PROTECT, related_name="enquiries"
    )
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=10)  # ten digits, no country code
    email = models.EmailField(blank=True)
    message = models.CharField(max_length=MESSAGE_MAX_LENGTH, blank=True)
    type = models.CharField(
        max_length=10, choices=EnquiryType.CHOICES, default=EnquiryType.ENQUIRY
    )
    preferred_time = models.CharField(
        max_length=10, choices=PreferredTime.CHOICES, blank=True
    )
    status = models.CharField(
        max_length=20, choices=EnquiryStatus.CHOICES, default=EnquiryStatus.NEW
    )
    # a UUID4 the visitor's browser keeps: it is the only link back to "My enquiries"
    device_token = models.UUIDField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=EnquiryStatus.VALUES),
                name="enquiry_status_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(type__in=EnquiryType.VALUES),
                name="enquiry_type_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(preferred_time="")
                | models.Q(preferred_time__in=PreferredTime.VALUES),
                name="enquiry_preferred_time_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(phone__regex=PHONE_DB_REGEX),
                name="enquiry_phone_format",
            ),
            # one open enquiry per phone number and training; also closes the race between two
            # simultaneous submits and between a submit and a status change
            models.UniqueConstraint(
                fields=["training", "phone"],
                condition=models.Q(status__in=EnquiryStatus.OPEN),
                name="enquiry_one_open_per_phone_training",
            ),
        ]
        indexes = [
            # the portal list, its status tabs and the counts
            models.Index(
                fields=["institute", "status", "-created_at"],
                name="enquiry_inst_status_idx",
            ),
            # "My enquiries"
            models.Index(
                fields=["device_token", "-created_at"], name="enquiry_device_idx"
            ),
            # converted enquiries against the seats
            models.Index(fields=["training", "status"], name="enquiry_training_status_idx"),
        ]

    def __str__(self):
        return f"{self.name} - {self.training_id}"


class EnquiryNote(BaseModel):
    """An internal note: only the institute's own team sees it, never the visitor."""

    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    text = models.CharField(max_length=MESSAGE_MAX_LENGTH)

    class Meta:
        ordering = ["-created_at", "-pk"]
        constraints = [
            models.CheckConstraint(condition=~models.Q(text=""), name="enquirynote_text_not_blank"),
        ]
