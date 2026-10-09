from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import CASCADE

from apps.common.models.base import BaseModel, SlugModel
from apps.common.models.category import Category
from apps.common.utils.helpers import get_upload_path
from apps.common.validators import validate_phone_number
from apps.institutes.models import Institute, InstituteLocation
from apps.institutes.validators import validate_image_file
from apps.training.constants import (
    DurationUnit,
    TrainingLevel,
    TrainingMode,
    TrainingStatus,
    WeekDay,
)


class Training(BaseModel, SlugModel):
    """Write through apps.training.services only: they keep the search vector and duration_weeks."""

    institute = models.ForeignKey(
        Institute, on_delete=models.PROTECT, related_name="trainings"
    )
    # a top-level category or a sub-category
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="trainings"
    )
    institute_location = models.ForeignKey(
        InstituteLocation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="trainings",
    )
    title = models.CharField(max_length=255)
    short_description = models.CharField(
        max_length=160, blank=True
    )  # on the cards; needed to submit
    cover_image = models.ImageField(
        upload_to=get_upload_path, blank=True, validators=[validate_image_file]
    )
    mode = models.CharField(max_length=10, choices=TrainingMode.CHOICES)
    level = models.CharField(max_length=15, choices=TrainingLevel.CHOICES, blank=True)
    duration_value = models.PositiveSmallIntegerField(null=True, blank=True)
    duration_unit = models.CharField(
        max_length=10, choices=DurationUnit.CHOICES, blank=True
    )
    # derived from value and unit by the services; the duration filter uses it
    duration_weeks = models.PositiveSmallIntegerField(
        null=True, blank=True, editable=False
    )
    fee_npr = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )  # 0 means free
    seats = models.PositiveIntegerField(null=True, blank=True)  # empty = unlimited
    start_date = models.DateField(null=True, blank=True)  # Nepal time
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=TrainingStatus.CHOICES, default=TrainingStatus.DRAFT
    )
    registration_deadline = models.DateField(null=True, blank=True)
    review_feedback = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)  # first approval
    search_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        constraints = [
            # drafts may be incomplete, so only "online has no location" is a database rule;
            # "physical and hybrid need a location" is checked when submitting
            models.CheckConstraint(
                condition=~models.Q(
                    mode=TrainingMode.ONLINE, institute_location__isnull=False
                ),
                name="training_online_has_no_location",
            ),
            models.CheckConstraint(
                condition=models.Q(start_date__isnull=True)
                | models.Q(end_date__isnull=True)
                | models.Q(end_date__gte=models.F("start_date")),
                name="training_dates_ordered",
            ),
            models.CheckConstraint(
                condition=models.Q(registration_deadline__isnull=True)
                | models.Q(start_date__isnull=True)
                | models.Q(registration_deadline__lte=models.F("start_date")),
                name="training_deadline_before_start",
            ),
            models.CheckConstraint(
                condition=models.Q(fee_npr__isnull=True) | models.Q(fee_npr__gte=0),
                name="training_fee_not_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(seats__isnull=True) | models.Q(seats__gt=0),
                name="training_seats_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(duration_value__isnull=True)
                | models.Q(duration_value__gt=0),
                name="training_duration_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(duration_value__isnull=True)
                | ~models.Q(duration_unit=""),
                name="training_duration_has_unit",
            ),
        ]
        indexes = [
            models.Index(
                fields=["start_date"],
                condition=models.Q(status=TrainingStatus.APPROVED),
                name="training_start_pub_idx",
            ),
            models.Index(
                fields=["-published_at"],
                condition=models.Q(status=TrainingStatus.APPROVED),
                name="training_published_idx",
            ),
            models.Index(
                fields=["institute", "status"], name="training_inst_status_idx"
            ),
            models.Index(fields=["category", "status"], name="training_cat_status_idx"),
            # the daily expiry job
            models.Index(fields=["status", "end_date"], name="training_status_end_idx"),
            GinIndex(fields=["search_vector"], name="training_search_gin"),
        ]

    def __str__(self):
        return self.title


class TrainingDetail(BaseModel):
    training = models.OneToOneField(Training, on_delete=CASCADE, related_name="detail")
    overview = models.TextField(blank=True)
    eligibility = models.TextField(blank=True)
    certification = models.CharField(max_length=255, blank=True)
    skills = ArrayField(models.CharField(max_length=60), blank=True, default=list)


class TrainingContact(BaseModel):
    training = models.OneToOneField(
        Training, on_delete=models.CASCADE, related_name="contact"
    )
    contact_person = models.CharField(max_length=150, blank=True)
    contact_phone = models.CharField(
        max_length=25, blank=True, validators=[validate_phone_number]
    )
    contact_email = models.EmailField(blank=True)


class TrainingSession(BaseModel):
    """A weekly class slot: the days it runs on and the time of day (Nepal time, online included).
    A training may have several, for example a morning and an evening batch."""

    training = models.ForeignKey(
        Training, on_delete=models.CASCADE, related_name="sessions"
    )
    class_days = ArrayField(
        models.CharField(max_length=3, choices=WeekDay.CHOICES), size=7
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ("start_time", "pk")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="training_session_ends_after_start",
            ),
        ]


class TrainingModule(BaseModel):
    """One entry of the curriculum."""

    training = models.ForeignKey(
        Training, on_delete=models.CASCADE, related_name="modules"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("pk",)  # entered order: the services insert the list in order


class LearningOutcome(BaseModel):
    training = models.ForeignKey(
        Training, on_delete=models.CASCADE, related_name="outcomes"
    )
    text = models.CharField(max_length=300)

    class Meta:
        ordering = ("pk",)
