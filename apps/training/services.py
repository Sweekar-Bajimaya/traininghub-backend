from datetime import timedelta

from django.contrib.postgres.aggregates import ArrayAgg, JSONBAgg
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVector
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import (
    CharField,
    Count,
    Exists,
    F,
    IntegerField,
    JSONField,
    OuterRef,
    Q,
    Subquery,
    Value,
)
from django.db.models.functions import Coalesce, JSONObject
from django.utils import timezone

from apps.common.models.category import Category
from apps.institutes import services as institute_services
from apps.institutes.constants import InstituteStatus
from apps.institutes.models import Institute
from apps.notification import services as notification_services
from apps.notification.constants import EventType
from apps.training.constants import (
    SEARCH_CONFIG,
    DurationUnit,
    StartBucket,
    TrainingMode,
    TrainingShift,
    TrainingStatus,
)
from apps.training.models import (
    LearningOutcome,
    Training,
    TrainingContact,
    TrainingDetail,
    TrainingLocation,
    TrainingModule,
    TrainingSession,
)
from apps.users import services as user_services


# derived values and search
def duration_in_weeks(value, unit):
    if not value or unit not in DurationUnit.WEEKS_PER_UNIT:
        return None
    # half up and at least one week, like the portal's Math.round
    return max(1, int(value * DurationUnit.WEEKS_PER_UNIT[unit] + 0.5))


def _build_search_vector(training):
    category = training.category
    category_names = (
        f"{category.parent.name if category.parent_id else ''} {category.name}"
    )
    venue = getattr(training, "venue", None)  # a draft may not have one yet
    place = venue.location if venue else None
    place_names = f"{place.name} {place.district.name}" if place else ""
    detail = getattr(
        training, "detail", None
    )  # a row made without the services has none
    skills = " ".join(detail.skills) if detail else ""
    overview = detail.overview if detail else ""
    return (
        SearchVector(Value(training.title), weight="A", config=SEARCH_CONFIG)
        + SearchVector(
            Value(f"{training.institute.name} {category_names} {skills}"),
            weight="B",
            config=SEARCH_CONFIG,
        )
        + SearchVector(
            Value(f"{training.short_description} {overview} {place_names}"),
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
        "institute",
        "category__parent",
        "venue__location__district",
        "detail",
    ).get(pk=training.pk)
    Training.objects.filter(pk=training.pk).update(
        search_vector=_build_search_vector(training)
    )


def refresh_search_vectors(queryset):
    for pk in queryset.values_list("pk", flat=True).iterator():
        refresh_search_vector(Training(pk=pk))


def registration_open_q(today=None):
    """A training still takes registrations: its deadline has not passed, or it has no deadline
    and has not started. One definition for the public `registration_open` filter and for
    enquiries (a plain enquiry is refused once this is false)."""
    today = today or timezone.localdate()
    return Q(registration_deadline__gte=today) | Q(
        registration_deadline__isnull=True, start_date__gte=today
    )


# checks
def _require_approved_institute(institute):
    if not Institute.objects.filter(
        pk=institute.pk, status=InstituteStatus.APPROVED
    ).exists():
        raise ValidationError("Only an approved institute can do this.")


def _check_category(category):
    if not category.is_active or (category.parent_id and not category.parent.is_active):
        raise ValidationError({"category": "This category is not available."})


def _check_venue(mode, location, address):
    """`location` is the municipality or None; `address` is the street address, or the plain text
    for an online training."""
    if mode == TrainingMode.ONLINE:
        if location is not None:
            raise ValidationError(
                {
                    "venue": "An online training has no municipality: send only the address text."
                }
            )
    elif location is None:
        raise ValidationError(
            {"venue": "Choose the municipality where the training is held."}
        )
    if not address:
        raise ValidationError({"venue": "Enter the address."})


def _save_venue(training, venue):
    """The one-to-one row holds where it is held. None leaves it alone; a dict replaces it whole."""
    if venue is None:
        return
    training.venue, _ = (
        TrainingLocation.objects.update_or_create(  # keeps the cached row current
            training=training,
            defaults={"location": None, "map_url": "", "contact_phone": "", **venue},
        )
    )


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
            raise ValidationError(
                {"sessions": "Choose at least one class day, each day once."}
            )
        if session["end_time"] <= session["start_time"]:
            raise ValidationError({"sessions": "A session must end after it starts."})


def _clean_shifts(shifts):
    """Each shift once, in Morning, Day, Evening order."""
    return sorted(set(shifts), key=TrainingShift.ORDER.index)


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
            [TrainingModule(training=training, **m) for m in modules]
        )
    if outcomes is not None:
        training.outcomes.all().delete()
        LearningOutcome.objects.bulk_create(
            [LearningOutcome(training=training, **o) for o in outcomes]
        )


def _save_extras(training, detail, contact):
    """The one-to-one rows hold the long text, skills and contact. None leaves a row alone; a dict
    changes only the fields in it (and creates the row if the training was made without one)."""
    for name, model, values in (
        ("detail", TrainingDetail, detail),
        ("contact", TrainingContact, contact),
    ):
        if values is None:
            continue
        row = getattr(training, name, None) or model(training=training)
        for field, value in values.items():
            setattr(row, field, value)
        row.save()


def _ready_for_submission(training):
    errors = {}
    required = {
        "short_description": training.short_description,
        "level": training.level,
        "shifts": training.shifts,
        "duration_value": training.duration_value,
        "duration_unit": training.duration_unit,
        "fee_npr": training.fee_npr,
        "start_date": training.start_date,
        "end_date": training.end_date,
    }
    for name, value in required.items():
        if value in (None, "", []):
            errors[name] = "This is required before submitting."
    venue = getattr(training, "venue", None)
    detail = getattr(training, "detail", None)
    if detail is None or not detail.target_audience:
        errors["target_audience"] = "This is required before submitting."
    if venue is None or not venue.address:
        errors["venue"] = "Add where the training is held."
    elif training.mode == TrainingMode.PHYSICAL:
        if venue.location_id is None:
            errors["venue"] = "Choose where the training is held."
        elif not venue.location.is_active:
            errors["venue"] = "The selected location is no longer active."
    if not training.sessions.exists():
        errors["sessions"] = "Add at least one class day and time."
    if training.start_date and training.start_date < timezone.localdate():
        errors["start_date"] = "The start date is in the past."
    if errors:
        raise ValidationError(errors)


# workflow
def _transition(training, to, *, only_from=None, reason="", check=None):
    """Caller must be inside transaction.atomic()."""
    training = (
        Training.objects.select_for_update(of=("self",))
        .select_related("institute", "venue__location")
        .get(pk=training.pk)
    )
    # The table alone is not enough: UNPUBLISHED -> APPROVED is a republish, not an admin approval.
    if only_from is not None and training.status not in only_from:
        raise ValidationError(
            f"A {training.get_status_display().lower()} training cannot do this."
        )
    if to not in TrainingStatus.TRANSITIONS[training.status]:
        raise ValidationError(f"Cannot move from {training.status} to {to}.")
    if to in TrainingStatus.REASON_REQUIRED and not reason.strip():
        raise ValidationError({"reason": "A reason is required."})
    previous = training.status
    if check:
        check(training)
    training.status = to
    if to in TrainingStatus.REASON_REQUIRED:
        training.review_feedback = reason
    elif to == TrainingStatus.APPROVED:
        training.review_feedback = ""
    if previous == TrainingStatus.APPROVED and to != TrainingStatus.APPROVED:
        training.is_featured = False  # no longer live, so no longer featured
    training.save(
        update_fields=["status", "review_feedback", "is_featured", "modified_at"]
    )
    return training


def _notify_review_requested(training, *, action):
    institute = training.institute
    notification_services.notify(
        EventType.TRAINING_SUBMITTED,
        recipients=institute_services.staff_users(institute),
        payload={
            "training_title": training.title,
            "training_slug": training.slug,
            "action": action,
        },
    )
    notification_services.notify(
        EventType.ADMIN_TRAINING_REVIEW,
        recipients=user_services.admins_with_permission("manage_trainings"),
        payload={
            "institute_name": institute.name,
            "institute_slug": institute.slug,
            "training_title": training.title,
            "training_slug": training.slug,
            "action": action,
        },
    )


def _notify_outcome(training, event, **extra):
    notification_services.notify(
        event,
        recipients=institute_services.staff_users(training.institute),
        payload={
            "training_title": training.title,
            "training_slug": training.slug,
            **extra,
        },
    )


# institute actions
@transaction.atomic
def submit(training, *, by):
    _require_approved_institute(training.institute)
    resubmitted = (
        training.status != TrainingStatus.DRAFT
    )  # changes were requested, or it was rejected
    training = _transition(
        training,
        TrainingStatus.SUBMITTED,
        check=_ready_for_submission,
        only_from=TrainingStatus.EDITABLE,
    )
    _notify_review_requested(
        training, action="resubmitted" if resubmitted else "submitted"
    )
    return training


@transaction.atomic
def withdraw(training, *, by):
    """Take a submitted training back to DRAFT while it waits for review."""
    return _transition(
        training, TrainingStatus.DRAFT, only_from={TrainingStatus.SUBMITTED}
    )


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
    return _transition(
        training, TrainingStatus.CANCELLED, only_from=TrainingStatus.LIVE
    )


# admin actions (a training that waits for review)
@transaction.atomic
def approve(training, *, by):
    training = _transition(
        training, TrainingStatus.APPROVED, only_from={TrainingStatus.SUBMITTED}
    )
    if training.published_at is None:
        training.published_at = timezone.now()
        training.save(update_fields=["published_at", "modified_at"])
    _notify_outcome(training, EventType.TRAINING_APPROVED)
    return training


@transaction.atomic
def request_changes(training, *, by, reason):
    training = _transition(
        training,
        TrainingStatus.CHANGES_REQUESTED,
        reason=reason,
        only_from={TrainingStatus.SUBMITTED},
    )
    _notify_outcome(training, EventType.TRAINING_CHANGES_REQUESTED, reason=reason)
    return training


@transaction.atomic
def set_featured(training, *, featured, by):
    """Feature or un-feature a training on the front page. Only an approved training of an
    approved institute can be featured; un-featuring is always allowed."""
    training = (
        Training.objects.select_for_update(of=("self",))
        .select_related("institute")
        .get(pk=training.pk)
    )
    if featured:
        if training.status != TrainingStatus.APPROVED:
            raise ValidationError("Only an approved training can be featured.")
        _require_approved_institute(training.institute)
    if training.is_featured != featured:
        training.is_featured = featured
        training.save(update_fields=["is_featured", "modified_at"])
    return training


@transaction.atomic
def reject(training, *, by, reason):
    training = _transition(
        training,
        TrainingStatus.REJECTED,
        reason=reason,
        only_from={TrainingStatus.SUBMITTED},
    )
    _notify_outcome(training, EventType.TRAINING_REJECTED, reason=reason)
    return training


# the system
def expire_trainings(today=None):
    """Set EXPIRED on every live training whose end date has passed. One statement, safe to run often."""
    today = today or timezone.localdate()
    return Training.objects.filter(
        status__in=TrainingStatus.LIVE, end_date__lt=today
    ).update(status=TrainingStatus.EXPIRED, is_featured=False)


# content
@transaction.atomic
def create_training(
    institute,
    *,
    sessions=None,
    modules=None,
    outcomes=None,
    detail=None,
    contact=None,
    venue=None,
    **fields,
):
    Institute.objects.select_for_update().get(
        pk=institute.pk
    )  # an admin may be suspending it right now
    _require_approved_institute(institute)
    _check_category(fields["category"])
    venue = venue or {}
    _check_venue(fields["mode"], venue.get("location"), venue.get("address"))
    _check_dates(
        fields.get("start_date"),
        fields.get("end_date"),
        fields.get("registration_deadline"),
    )
    if "shifts" in fields:
        fields["shifts"] = _clean_shifts(fields["shifts"])
    if sessions is not None:
        _check_sessions(sessions)
    fields["duration_weeks"] = duration_in_weeks(
        fields.get("duration_value"), fields.get("duration_unit")
    )
    training = Training.objects.create(institute=institute, **fields)
    _save_extras(training, detail or {}, contact or {})  # every training has both rows
    _save_venue(training, venue)  # create requires one, so this is never skipped
    _replace_children(training, sessions, modules, outcomes)
    refresh_search_vector(training)
    return training


@transaction.atomic
def update_training(
    training,
    *,
    sessions=None,
    modules=None,
    outcomes=None,
    detail=None,
    contact=None,
    venue=None,
    **fields,
):
    """DRAFT, CHANGES_REQUESTED and REJECTED are saved as they are. APPROVED and UNPUBLISHED go
    straight back to review (hidden until approved), and the edit is refused if the result is not
    ready to submit; the whole edit then rolls back."""
    training = (
        Training.objects.select_for_update(of=("self",))
        .select_related("institute", "category__parent", "venue", "detail", "contact")
        .get(pk=training.pk)
    )
    back_to_review = training.status in TrainingStatus.REVIEWED_EDIT
    if training.status not in TrainingStatus.EDITABLE and not back_to_review:
        raise ValidationError(
            f"A {training.get_status_display().lower()} training cannot be edited."
        )
    mode = fields.get("mode", training.mode)
    if venue is None and mode != training.mode:
        raise ValidationError({"venue": "Send the venue when you change the mode."})
    if (
        venue is not None or "mode" in fields
    ):  # a title-only edit of an old draft stays allowed
        current = getattr(training, "venue", None)
        if venue is not None:
            location, address = venue.get("location"), venue["address"]
        elif current is not None:
            location, address = current.location, current.address
        else:
            location, address = None, ""
        _check_venue(mode, location, address)
    _check_category(fields.get("category", training.category))
    _check_dates(
        fields.get("start_date", training.start_date),
        fields.get("end_date", training.end_date),
        fields.get("registration_deadline", training.registration_deadline),
    )
    if "shifts" in fields:
        fields["shifts"] = _clean_shifts(fields["shifts"])

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
    _save_extras(training, detail, contact)
    _save_venue(training, venue)
    _replace_children(training, sessions, modules, outcomes)
    refresh_search_vector(training)
    if back_to_review:
        _require_approved_institute(training.institute)
        training = _transition(
            training, TrainingStatus.SUBMITTED, check=_ready_for_submission
        )
        _notify_review_requested(training, action="resubmitted")
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
        raise ValidationError(
            "Only a draft can be deleted. Cancel the training instead."
        )
    # a training that was live and went back to a draft may hold enquiries, which the institute keeps
    if training.enquiries.exists():
        raise ValidationError(
            "This training has enquiries, so it cannot be deleted. Cancel it instead."
        )
    training.delete()


def institute_counts(trainings):
    return trainings.aggregate(
        total=Count("pk"),
        active=Count("pk", filter=Q(status=TrainingStatus.APPROVED)),
        pending_review=Count("pk", filter=Q(status=TrainingStatus.SUBMITTED)),
    )


def admin_counts(trainings):
    """The admin dashboard's cards, in one query. `total` leaves out drafts (an institute's private
    work: the admin never reviews one), so it means "submitted at some point"; `pending_review` is
    `SUBMITTED` and `rejected` is `REJECTED` only (not `CHANGES_REQUESTED`)."""
    return trainings.aggregate(
        total=Count("pk", filter=~Q(status=TrainingStatus.DRAFT)),
        pending_review=Count("pk", filter=Q(status=TrainingStatus.SUBMITTED)),
        approved=Count("pk", filter=Q(status=TrainingStatus.APPROVED)),
        rejected=Count("pk", filter=Q(status=TrainingStatus.REJECTED)),
    )


def annotate_category_training_count(categories):
    """Annotate categories with `training_count`: the trainings the public can see (`APPROVED`,
    of an `APPROVED` institute) in the category itself and, for a top-level one, in its
    sub-categories. The same rule as the public `category` filter. One query, however many rows."""
    visible = (
        Training.objects.filter(
            status=TrainingStatus.APPROVED, institute__status=InstituteStatus.APPROVED
        )
        .filter(Q(category=OuterRef("pk")) | Q(category__parent=OuterRef("pk")))
        .order_by()  # no ordering inside the subquery
        .values(group=Value(1))  # one group, so the subquery answers a single row
        .annotate(n=Count("pk"))
        .values("n")
    )
    return categories.annotate(
        training_count=Coalesce(Subquery(visible, output_field=IntegerField()), 0)
    )


def annotate_institute_training_count(trainings):
    """Annotate trainings with `institute_training_count`: the `APPROVED` trainings of the same
    institute. One query, however many rows. The detail view only serves approved institutes, so
    this is the public count."""
    approved = (
        Training.objects.filter(
            institute=OuterRef("institute_id"), status=TrainingStatus.APPROVED
        )
        .order_by()
        .values(group=Value(1))
        .annotate(n=Count("pk"))
        .values("n")
    )
    return trainings.annotate(
        institute_training_count=Coalesce(
            Subquery(approved, output_field=IntegerField()), 0
        )
    )


def annotate_institute_public_counts(institutes):
    """Annotate institutes with `training_count` (their `APPROVED` trainings) and `category_count`
    (the distinct active top-level categories those trainings fall in; a sub-category counts as
    its parent, and a retired top-level category is not counted). One query, however many rows.
    Pass approved institutes only (the public list)."""
    approved = Training.objects.filter(
        institute=OuterRef("pk"), status=TrainingStatus.APPROVED
    ).order_by()

    def scalar(aggregate):
        return Coalesce(
            Subquery(
                approved.values(group=Value(1)).annotate(n=aggregate).values("n"),
                output_field=IntegerField(),
            ),
            0,
        )

    top_level = Coalesce(
        "category__parent_id", "category_id", output_field=IntegerField()
    )
    # the top-level category is the parent when there is one, else the category itself
    top_level_is_active = Q(category__parent__is_active=True) | Q(
        category__parent__isnull=True, category__is_active=True
    )
    return institutes.annotate(
        training_count=scalar(Count("pk")),
        category_count=scalar(
            Count(top_level, distinct=True, filter=top_level_is_active)
        ),
    )


def annotate_institute_public_categories(institutes):
    """Annotate institutes with `categories`: a list of `{id, slug, name}`, the active top-level
    categories their `APPROVED` trainings fall in (a training in a sub-category counts for its
    parent; a retired top-level category is left out, like in the public category tree), ordered
    by name. The same rule as `category_count`, so the two always agree. It is computed inside
    the institute query (no extra query), so use it on the detail only: the list does not show
    it. Pass approved institutes only (the public detail)."""
    # inner OuterRef is the category, outer OuterRef is the institute
    uses_category = Exists(
        Training.objects.filter(
            institute=OuterRef(OuterRef("pk")), status=TrainingStatus.APPROVED
        )
        .filter(Q(category=OuterRef("pk")) | Q(category__parent=OuterRef("pk")))
        .order_by()
    )
    used = (
        Category.objects.filter(parent__isnull=True, is_active=True)
        .filter(uses_category)
        .order_by()  # the order is set inside the aggregate
        .values(group=Value(1))  # one group, so the subquery answers a single row
        .annotate(
            items=JSONBAgg(
                JSONObject(id="id", slug="slug", name="name"), order_by=("name", "pk")
            )
        )
        .values("items")
    )
    return institutes.annotate(
        categories=Coalesce(
            Subquery(used, output_field=JSONField()),
            Value([], output_field=JSONField()),  # no approved training: an empty list
        )
    )


def annotate_institute_public_training_modes(institutes):
    """Annotate institutes with `training_modes`: the distinct modes (`ONLINE`, `PHYSICAL`) of
    their `APPROVED` trainings, in alphabetical order, so a list of zero, one or two values. The
    same trainings as `training_count`. It is computed inside the institute query (no extra
    query), so use it on the detail only: the list does not show it. Pass approved institutes
    only (the public detail)."""
    modes_field = ArrayField(CharField(max_length=10))
    used = (
        Training.objects.filter(
            institute=OuterRef("pk"), status=TrainingStatus.APPROVED
        )
        .order_by()
        .values(group=Value(1))  # one group, so the subquery answers a single row
        .annotate(items=ArrayAgg("mode", distinct=True, order_by="mode"))
        .values("items")
    )
    return institutes.annotate(
        training_modes=Coalesce(
            Subquery(used, output_field=modes_field),
            Value([], output_field=modes_field),  # no approved training: an empty list
        )
    )


def training_counts_by_location():
    """Public trainings per district (the same rule as the public list: APPROVED trainings of
    APPROVED institutes), biggest first, then one "Online" entry last. Online trainings have no
    municipality, so they are counted on their own, by mode, which is what `?mode=ONLINE` filters
    on: that entry has `id` None, and the other entries link to `?district=<id>`. Districts and
    Online are left out when they have no training. Two queries."""

    public = Training.objects.filter(
        status=TrainingStatus.APPROVED, institute__status=InstituteStatus.APPROVED
    )
    rows = (
        public.filter(venue__location__district__is_active=True)
        .values(
            district_id=F("venue__location__district_id"),
            district_name=F("venue__location__district__name"),
        )
        .annotate(training_count=Count("pk"))
        .order_by("-training_count", "district_name")
    )
    # an alias called `id` would clash with Training.id, so rename here
    counts = [
        {
            "id": r["district_id"],
            "name": r["district_name"],
            "training_count": r["training_count"],
        }
        for r in rows
    ]
    online = public.filter(mode=TrainingMode.ONLINE).count()
    if online:
        counts.append({"id": None, "name": "Online", "training_count": online})
    return counts


def start_date_range(bucket, today=None):
    """(first day, last day) a StartBucket covers; the last day is None when it has no end.
    The windows are rolling and cumulative, counted from today. A training that has already
    started is in no bucket."""
    today = today or timezone.localdate()
    if bucket == StartBucket.LATER:
        return today + timedelta(days=max(StartBucket.DAYS.values()) + 1), None
    return today, today + timedelta(days=StartBucket.DAYS[bucket])
