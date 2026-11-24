from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Count, Q

from apps.common.exceptions import TooManyRequests
from apps.enquiries.constants import (
    MILESTONE_COUNTS,
    MILESTONE_SEAT_PERCENTS,
    PHONE_DAILY_LIMIT,
    PHONE_LIMIT_SECONDS,
    EnquiryStatus,
    EnquiryType,
)
from apps.enquiries.models import Enquiry, EnquiryNote
from apps.institutes import services as institute_services
from apps.institutes.constants import InstituteStatus
from apps.notification import services as notification_services
from apps.notification.constants import EventType
from apps.training import services as training_services
from apps.training.constants import TrainingStatus
from apps.training.models import Training

OPEN_CONSTRAINT = "enquiry_one_open_per_phone_training"


def _is_open_duplicate(error):
    """The database rejected a second open enquiry for one phone number and training (and not
    some other constraint)."""
    return OPEN_CONSTRAINT in str(error)


# visitor side
def _require_accepting(training):
    if (
        training.status != TrainingStatus.APPROVED
        or training.institute.status != InstituteStatus.APPROVED
    ):
        raise ValidationError({"training": "This training is not accepting enquiries."})


def _require_open_for_enquiry(training):
    """A plain enquiry asks about this batch, so it needs registration to be open and a free seat.
    Neither check locks the training: one extra enquiry that slips in beside the last seat does no
    harm, because an enquiry does not take a seat (only CONVERTED does, see `change_status`)."""
    open_now = Training.objects.filter(
        training_services.registration_open_q(), pk=training.pk
    )
    if not open_now.exists():
        raise ValidationError(
            "Registration for this training has closed. You can still show interest."
        )
    if training.seats is not None:
        taken = Enquiry.objects.filter(
            training=training, status=EnquiryStatus.CONVERTED
        ).count()
        if taken >= training.seats:
            raise ValidationError("This training is full. You can still show interest.")


def _claim_phone_slot(phone):
    """Count this enquiry against the phone number's daily allowance (Redis, atomic increment)."""
    key = f"enquiry_phone_{phone}"
    cache.add(key, 0, timeout=PHONE_LIMIT_SECONDS)
    try:
        count = cache.incr(key)
    except ValueError:  # the key expired between add and incr
        cache.set(key, 1, timeout=PHONE_LIMIT_SECONDS)
        count = 1
    if count > PHONE_DAILY_LIMIT:
        raise TooManyRequests(
            "Too many enquiries from this phone number today. Please try again tomorrow.",
            wait=cache.ttl(key) or PHONE_LIMIT_SECONDS,
        )


def _milestone_counts(training):
    return Enquiry.objects.filter(training=training).aggregate(
        enquiries=Count("pk"),
        interest=Count("pk", filter=Q(type=EnquiryType.INTEREST)),
        converted=Count("pk", filter=Q(status=EnquiryStatus.CONVERTED)),
    )


def _fire_highest(event, staff, training, metric, crossed, payload_for):
    """Notify for the highest threshold reached and record the lower ones without sending, so
    data that already passed them does not trigger a burst. `crossed` is ascending. The dedupe
    key lets each threshold fire once per person, even when two requests arrive together."""

    if not crossed:
        return

    def key(label):
        return f"milestone:{metric}:{training.pk}:{label}"

    for label in crossed[:-1]:
        notification_services.mark_seen(staff, key(label))
    top = crossed[-1]
    notification_services.notify(
        event, recipients=staff, payload=payload_for(top), dedupe_key=key(top)
    )


def _check_intake_milestones(training, staff):
    counts = _milestone_counts(training)
    base = {"training_title": training.title, "training_slug": training.slug}
    for metric, event in (
        ("enquiries", EventType.MILESTONE_ENQUIRIES),
        ("interest", EventType.MILESTONE_INTEREST),
    ):
        crossed = [n for n in MILESTONE_COUNTS if counts[metric] >= n]
        _fire_highest(
            event, staff, training, metric, crossed, lambda n: {**base, "threshold": n}
        )


def _check_converted_milestone(training, staff):
    if not training.seats:
        return  # unlimited seats: there is no percentage to reach
    converted = _milestone_counts(training)["converted"]
    crossed = [
        p for p in MILESTONE_SEAT_PERCENTS if converted * 100 >= training.seats * p
    ]
    _fire_highest(
        EventType.MILESTONE_CONVERTED,
        staff,
        training,
        "converted",
        crossed,
        lambda p: {
            "training_title": training.title,
            "training_slug": training.slug,
            "percent": p,
            "converted": converted,
            "seats": training.seats,
        },
    )


def _notify_enquiry_created(enquiry, training):
    staff = list(institute_services.staff_users(enquiry.institute))
    notification_services.notify(
        EventType.ENQUIRY_NEW,
        recipients=staff,
        payload={
            "kind": "interest" if enquiry.type == EnquiryType.INTEREST else "enquiry",
            "name": enquiry.name,  # typed by a visitor: plain text only, never in an email subject
            "enquiry_id": enquiry.pk,
            "training_title": training.title,
            "training_slug": training.slug,
        },
    )
    _check_intake_milestones(training, staff)


def _notify_converted(enquiry, by):
    training = enquiry.training
    everyone = list(institute_services.staff_users(enquiry.institute))
    # the owner and the other staff hear about it; the person who made the change already knows
    others = [user for user in everyone if user.pk != by.pk]
    notification_services.notify(
        EventType.ENQUIRY_CONVERTED,
        recipients=others,
        payload={
            "name": enquiry.name,
            "enquiry_id": enquiry.pk,
            "training_title": training.title,
            "training_slug": training.slug,
            "changed_by": by.full_name or by.email,
        },
    )
    _check_converted_milestone(training, everyone)  # the milestone goes to everyone


def submit_enquiry(
    *,
    training,
    name,
    phone,
    email="",
    message="",
    type=EnquiryType.ENQUIRY,
    preferred_time="",
):
    """Create an enquiry for a published training. `phone` is already normalised and
    `training.institute` should be loaded. Raises ValidationError when the training does not
    accept it, and TooManyRequests when the phone number is over its daily allowance."""
    _require_accepting(training)
    if type == EnquiryType.ENQUIRY:
        _require_open_for_enquiry(training)
    duplicate = ValidationError(
        "You already have an open enquiry for this training from this phone number."
    )
    if Enquiry.objects.filter(
        training=training, phone=phone, status__in=EnquiryStatus.OPEN
    ).exists():
        raise duplicate
    _claim_phone_slot(
        phone
    )  # after the rules, so a refused enquiry does not use the allowance
    try:
        with transaction.atomic():
            enquiry = Enquiry.objects.create(
                training=training,
                institute=training.institute,
                name=name,
                phone=phone,
                email=email,
                message=message,
                type=type,
                preferred_time=preferred_time,
            )
            _notify_enquiry_created(enquiry, training)
        return enquiry
    except IntegrityError as error:  # two submits at once: the unique index decides
        if _is_open_duplicate(error):
            raise duplicate from error
        raise


# institute side
@transaction.atomic
def change_status(enquiry, *, status, by):
    """Move an enquiry to any status. CONVERTED takes a seat, so it is refused once the training's
    converted enquiries reach its seats; the training row is locked first, so two staff members
    cannot both take the last seat. Locks always run enquiry then training, so they cannot
    deadlock."""
    if status not in EnquiryStatus.VALUES:
        raise ValidationError({"status": "Not a valid status."})
    enquiry = Enquiry.objects.select_for_update().get(pk=enquiry.pk)
    if enquiry.status == status:
        return enquiry
    if status == EnquiryStatus.CONVERTED:
        seats = (
            Training.objects.select_for_update()
            .only("seats")
            .get(pk=enquiry.training_id)
            .seats
        )
        if (
            seats is not None
            and Enquiry.objects.filter(
                training_id=enquiry.training_id, status=EnquiryStatus.CONVERTED
            ).count()
            >= seats
        ):
            raise ValidationError(
                {
                    "status": "All seats of this training are already taken by converted enquiries."
                }
            )
    enquiry.status = status
    try:
        with (
            transaction.atomic()
        ):  # a savepoint, so the error does not poison the outer transaction
            enquiry.save(update_fields=["status", "modified_at"])
    except IntegrityError as error:
        if not _is_open_duplicate(error):
            raise
        raise ValidationError(
            {
                "status": "Another open enquiry from this phone number already exists "
                "for this training."
            }
        ) from error
    if status == EnquiryStatus.CONVERTED:
        _notify_converted(enquiry, by)
    # TODO(audit): who changed the status (`by`)
    return enquiry


def add_note(*, enquiry, author, text):
    return EnquiryNote.objects.create(enquiry=enquiry, author=author, text=text.strip())


def summary(enquiries):
    """Counts for the portal's tabs, sidebar badge and cards, in one query. Pass the queryset the
    list shows (without a status filter, or the other tabs read zero)."""
    counts = enquiries.aggregate(
        total=Count("pk"),
        unique_phones=Count("phone", distinct=True),
        **{
            status: Count("pk", filter=Q(status=status))
            for status in EnquiryStatus.VALUES
        },
    )
    return {
        "total": counts["total"],
        "new": counts[EnquiryStatus.NEW],
        "unique_phones": counts["unique_phones"],
        "by_status": {status: counts[status] for status in EnquiryStatus.VALUES},
    }


def counts(enquiries):
    """Total and converted, in one query. The admin monitor's header."""
    return enquiries.aggregate(
        total=Count("pk"),
        converted=Count("pk", filter=Q(status=EnquiryStatus.CONVERTED)),
    )


def admin_counts(enquiries):
    """The admin dashboard's cards, in one query: total, new and converted (the frontend shows
    converted / total as a percentage). Pass an unfiltered queryset."""
    return enquiries.aggregate(
        total=Count("pk"),
        new=Count("pk", filter=Q(status=EnquiryStatus.NEW)),
        converted=Count("pk", filter=Q(status=EnquiryStatus.CONVERTED)),
    )


def institute_dashboard_counts(enquiries):
    """The institute dashboard's cards, in one query: every enquiry, the new ones, and the people
    who asked to hear about the next batch (INTEREST type, one per phone number, because a visitor
    has no account). Pass the institute's own enquiries."""
    return enquiries.aggregate(
        total=Count("pk"),
        new=Count("pk", filter=Q(status=EnquiryStatus.NEW)),
        interested_users=Count(
            "phone", filter=Q(type=EnquiryType.INTEREST), distinct=True
        ),
    )
