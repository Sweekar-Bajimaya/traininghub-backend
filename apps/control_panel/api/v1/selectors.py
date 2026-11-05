"""Read-only queries for the control panel that join several apps."""

from apps.institutes.constants import InstituteStatus
from apps.institutes.models import InstituteStatusLog
from apps.training.constants import TrainingStatus
from apps.training.models import Training

_STATUS_LABELS = dict(InstituteStatus.CHOICES)


def _event(type_, title, body, at, *, by=None, **extra):
    return {
        "type": type_,
        "title": title,
        "body": body,
        "at": at,
        "by": by,
        "from_status": None,
        "to_status": None,
        "reason": "",
        "training": None,
        **extra,
    }


def institute_activity(institute):
    """The review page timeline, newest first: when the institute registered, every status change
    (who, why), and each training it submitted. Training approvals and rejections will join once
    trainings keep a status log of their own."""
    documents = institute.documents.count()
    events = [
        _event(
            "REGISTERED",
            "Registered",
            f"Submitted institute details and {documents} document"
            f"{'' if documents == 1 else 's'}",
            institute.created_at,
        )
    ]

    logs = institute.status_logs.select_related("changed_by").order_by("created_at", "pk")
    for log in logs:
        by = None
        if log.changed_by_id:
            by = log.changed_by.full_name or log.changed_by.email
        events.append(
            _event(
                "STATUS_CHANGED",
                f"Status changed to {_STATUS_LABELS.get(log.to_status, log.to_status)}",
                log.reason or (f"By {by}" if by else ""),
                log.created_at,
                by=by,
                from_status=log.from_status,
                to_status=log.to_status,
                reason=log.reason,
            )
        )

    trainings = (
        Training.objects.filter(institute=institute)
        .exclude(status=TrainingStatus.DRAFT)
        .only("slug", "title", "status", "created_at")
    )
    for training in trainings:
        events.append(
            _event(
                "TRAINING_SUBMITTED",
                "Training submitted",
                f"{training.title} \u2014 {training.get_status_display()}",
                training.created_at,
                training={
                    "slug": training.slug,
                    "title": training.title,
                    "status": training.status,
                },
            )
        )

    events.sort(key=lambda event: event["at"], reverse=True)
    return events
