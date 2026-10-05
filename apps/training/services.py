from django.contrib.postgres.search import SearchVector
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Value
from django.utils import timezone

from apps.institutes.constants import InstituteStatus
from apps.institutes.models import Institute
from apps.training.constants import (
    SEARCH_CONFIG,
    DurationUnit,
    TrainingMode,
    TrainingStatus,
)
from apps.training.models import (
    LearningOutcome,
    Training,
    TrainingModule,
    TrainingSession,
)

# ---------------------------------------------------------------- derived values and search


def duration_in_weeks(value, unit):
    if not value or unit not in DurationUnit.WEEKS_PER_UNIT:
        return None
    # half up and at least one week, like the portal's Math.round
    return max(1, int(value * DurationUnit.WEEKS_PER_UNIT[unit] + 0.5))


def _build_search_vector(training):
    category = training.category
    category_names = f"{category.parent.name if category.parent_id else ''} {category.name}"
    place = training.institute_location
    place_names = f"{place.location.name} {place.location.district.name}" if place else ""
    return (
        SearchVector(Value(training.title), weight="A", config=SEARCH_CONFIG)
        + SearchVector(
            Value(f"{training.institute.name} {category_names} {' '.join(training.skills)}"),
            weight="B",
            config=SEARCH_CONFIG,
        )
        + SearchVector(
            Value(f"{training.short_description} {training.overview} {place_names}"),
            weight="C",
            config=SEARCH_CONFIG,
        )
        + SearchVector(
            Value(" ".join(training.modules.values_list("title", flat=True))),
            weight="D",
            config=SEARCH_CONFIG,
        )
    )


def refresh_search_vector(training):
    """The vector is built from Python values, so one UPDATE and no joins in the database."""
    training = Training.objects.select_related(
        "institute", "category__parent", "institute_location__location__district"
    ).get(pk=training.pk)
    Training.objects.filter(pk=training.pk).update(
        search_vector=_build_search_vector(training)
    )


def refresh_search_vectors(queryset):
    for pk in queryset.values_list("pk", flat=True).iterator():
        refresh_search_vector(Training(pk=pk))


# ---------------------------------------------------------------- checks


def _require_approved_institute(institute):
    if not Institute.objects.filter(pk=institute.pk, status=InstituteStatus.APPROVED).exists():
        raise ValidationError("Only an approved institute can do this.")


def _check_category(category):
    if not category.is_active or (category.parent_id and not category.parent.is_active):
        raise ValidationError({"category": "This category is not available."})


def _check_location(institute, mode, location):
    if mode == TrainingMode.ONLINE:
        if location is not None:
            raise ValidationError({"institute_location": "An online training has no location."})
        return
    if location is not None and (
        location.institute_id != institute.pk or not location.is_active
    ):
        raise ValidationError({"institute_location": "Choose one of your active locations."})


def _check_dates(start, end, deadline):
    errors = {}
    if start and end and end < start:
        errors["end_date"] = "The end date cannot be before the start date."
    if deadline and start and deadline > start:
        errors["registration_deadline"] = (
            "The registration deadline cannot be after the start date."
        )
    if errors:
        raise ValidationError(errors)


def _check_sessions(sessions):
    for session in sessions:
        days = session["class_days"]
        if not days or len(set(days)) != len(days):
            raise ValidationError({"sessions": "Choose at least one class day, each day once."})
        if session["end_time"] <= session["start_time"]:
            raise ValidationError({"sessions": "A session must end after it starts."})


def _replace_children(training, sessions, modules, outcomes):
    """None leaves a list alone; a list (even an empty one) replaces it."""
    if sessions is not None:
        training.sessions.all().delete()
        TrainingSession.objects.bulk_create(
            [TrainingSession(training=training, **s) for s in sessions]
        )
    if modules is not None:
        training.modules.all().delete()
        TrainingModule.objects.bulk_create(
            [TrainingModule(training=training, position=i, **m) for i, m in enumerate(modules)]
        )
    if outcomes is not None:
        training.outcomes.all().delete()
        LearningOutcome.objects.bulk_create(
            [LearningOutcome(training=training, position=i, **o) for i, o in enumerate(outcomes)]
        )


def _ready_for_submission(training):
    errors = {}
    required = {
        "short_description": training.short_description,
        "level": training.level,
        "duration_value": training.duration_value,
        "duration_unit": training.duration_unit,
        "fee_npr": training.fee_npr,
        "start_date": training.start_date,
        "end_date": training.end_date,
    }
    for name, value in required.items():
        if value in (None, ""):
            errors[name] = "This is required before submitting."
    if training.mode != TrainingMode.ONLINE:
        if training.institute_location_id is None:
            errors["institute_location"] = "Choose where the training is held."
        elif not training.institute_location.is_active:
            errors["institute_location"] = "The selected location is no longer active."
    if not training.sessions.exists():
        errors["sessions"] = "Add at least one class day and time."
    if training.start_date and training.start_date < timezone.localdate():
        errors["start_date"] = "The start date is in the past."
    if errors:
        raise ValidationError(errors)


# ---------------------------------------------------------------- workflow


def _transition(training, to, *, only_from=None, reason="", check=None):
    """Caller must be inside transaction.atomic()."""
    training = (
        Training.objects.select_for_update(of=("self",))
        .select_related("institute", "institute_location")
        .get(pk=training.pk)
    )
    # The table alone is not enough: UNPUBLISHED -> APPROVED is a republish, not an admin approval.
    if only_from is not None and training.status not in only_from:
        raise ValidationError(f"A {training.get_status_display().lower()} training cannot do this.")
    if to not in TrainingStatus.TRANSITIONS[training.status]:
        raise ValidationError(f"Cannot move from {training.status} to {to}.")
    if to in TrainingStatus.REASON_REQUIRED and not reason.strip():
        raise ValidationError({"reason": "A reason is required."})
    if check:
        check(training)
    training.status = to
    if to in TrainingStatus.REASON_REQUIRED:
        training.review_feedback = reason
    elif to == TrainingStatus.APPROVED:
        training.review_feedback = ""
    training.save(update_fields=["status", "review_feedback", "modified_at"])
    return training


# institute actions


@transaction.atomic
def submit(training, *, by):
    _require_approved_institute(training.institute)
    # TODO(notify): admins with manage_trainings
    return _transition(
        training,
        TrainingStatus.SUBMITTED,
        check=_ready_for_submission,
        only_from=TrainingStatus.EDITABLE,
    )


@transaction.atomic
def withdraw(training, *, by):
    """Take a submitted training back to DRAFT while it waits for review."""
    return _transition(training, TrainingStatus.DRAFT, only_from={TrainingStatus.SUBMITTED})


@transaction.atomic
def unpublish(training, *, by):
    return _transition(
        training, TrainingStatus.UNPUBLISHED, only_from={TrainingStatus.APPROVED}
    )


@transaction.atomic
def republish(training, *, by):
    _require_approved_institute(training.institute)
    return _transition(
        training, TrainingStatus.APPROVED, only_from={TrainingStatus.UNPUBLISHED}
    )


@transaction.atomic
def cancel(training, *, by):
    # TODO(notify): people who sent an enquiry (once enquiries exist)
    return _transition(training, TrainingStatus.CANCELLED, only_from=TrainingStatus.LIVE)


# admin actions (a training that waits for review)


@transaction.atomic
def approve(training, *, by):
    training = _transition(
        training, TrainingStatus.APPROVED, only_from={TrainingStatus.SUBMITTED}
    )
    if training.published_at is None:
        training.published_at = timezone.now()
        training.save(update_fields=["published_at", "modified_at"])
    # TODO(audit) + TODO(notify): the institute
    return training


@transaction.atomic
def request_changes(training, *, by, reason):
    return _transition(
        training,
        TrainingStatus.CHANGES_REQUESTED,
        reason=reason,
        only_from={TrainingStatus.SUBMITTED},
    )


@transaction.atomic
def reject(training, *, by, reason):
    return _transition(
        training, TrainingStatus.REJECTED, reason=reason, only_from={TrainingStatus.SUBMITTED}
    )


# the system


def expire_trainings(today=None):
    """Set EXPIRED on every live training whose end date has passed. One statement, safe to run often."""
    today = today or timezone.localdate()
    return Training.objects.filter(
        status__in=TrainingStatus.LIVE, end_date__lt=today
    ).update(status=TrainingStatus.EXPIRED, modified_at=timezone.now())


# ---------------------------------------------------------------- content


@transaction.atomic
def create_training(institute, *, sessions=None, modules=None, outcomes=None, **fields):
    Institute.objects.select_for_update().get(pk=institute.pk)  # an admin may be suspending it right now
    _require_approved_institute(institute)
    _check_category(fields["category"])
    _check_location(institute, fields["mode"], fields.get("institute_location"))
    _check_dates(
        fields.get("start_date"), fields.get("end_date"), fields.get("registration_deadline")
    )
    if sessions is not None:
        _check_sessions(sessions)
    fields["duration_weeks"] = duration_in_weeks(
        fields.get("duration_value"), fields.get("duration_unit")
    )
    training = Training.objects.create(institute=institute, **fields)
    _replace_children(training, sessions, modules, outcomes)
    refresh_search_vector(training)
    return training


@transaction.atomic
def update_training(training, *, sessions=None, modules=None, outcomes=None, **fields):
    """DRAFT, CHANGES_REQUESTED and REJECTED are saved as they are. APPROVED and UNPUBLISHED go
    straight back to review (hidden until approved), and the edit is refused if the result is not
    ready to submit; the whole edit then rolls back."""
    training = (
        Training.objects.select_for_update(of=("self",))
        .select_related("institute", "category__parent", "institute_location")
        .get(pk=training.pk)
    )
    back_to_review = training.status in TrainingStatus.REVIEWED_EDIT
    if training.status not in TrainingStatus.EDITABLE and not back_to_review:
        raise ValidationError(
            f"A {training.get_status_display().lower()} training cannot be edited."
        )
    mode = fields.get("mode", training.mode)
    if mode == TrainingMode.ONLINE and "institute_location" not in fields:
        fields["institute_location"] = None  # switching to online clears the location
    _check_category(fields.get("category", training.category))
    _check_location(
        training.institute, mode, fields.get("institute_location", training.institute_location)
    )
    _check_dates(
        fields.get("start_date", training.start_date),
        fields.get("end_date", training.end_date),
        fields.get("registration_deadline", training.registration_deadline),
    )
    if sessions is not None:
        _check_sessions(sessions)
    if "duration_value" in fields or "duration_unit" in fields:
        fields["duration_weeks"] = duration_in_weeks(
            fields.get("duration_value", training.duration_value),
            fields.get("duration_unit", training.duration_unit),
        )
    for name, value in fields.items():
        setattr(training, name, value)
    training.save(update_fields=[*fields, "modified_at"])
    _replace_children(training, sessions, modules, outcomes)
    refresh_search_vector(training)
    if back_to_review:
        _require_approved_institute(training.institute)
        training = _transition(
            training, TrainingStatus.SUBMITTED, check=_ready_for_submission
        )
    return training


@transaction.atomic
def set_cover(training, image):
    training = Training.objects.select_for_update().get(pk=training.pk)
    if training.status not in TrainingStatus.EDITABLE:
        raise ValidationError(
            "The cover can only change while the training is a draft or being revised."
        )
    training.cover_image = image
    training.save(update_fields=["cover_image", "modified_at"])
    return training


@transaction.atomic
def delete_training(training):
    training = Training.objects.select_for_update().get(pk=training.pk)
    if training.status != TrainingStatus.DRAFT:
        raise ValidationError("Only a draft can be deleted. Cancel the training instead.")
    training.delete()
