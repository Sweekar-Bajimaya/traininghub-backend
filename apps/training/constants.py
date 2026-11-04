class TrainingMode:
    PHYSICAL, ONLINE = "PHYSICAL", "ONLINE"
    CHOICES = ((PHYSICAL, "Physical"), (ONLINE, "Online"))


class TrainingLevel:
    """Exactly the three levels the UI offers."""

    BEGINNER, INTERMEDIATE, ADVANCED = "BEGINNER", "INTERMEDIATE", "ADVANCED"
    CHOICES = (
        (BEGINNER, "Beginner"),
        (INTERMEDIATE, "Intermediate"),
        (ADVANCED, "Advanced"),
    )


class DurationUnit:
    DAYS, WEEKS, MONTHS = "DAYS", "WEEKS", "MONTHS"
    CHOICES = ((DAYS, "Days"), (WEEKS, "Weeks"), (MONTHS, "Months"))
    # the portal's own conversion (a month is 4.3 weeks); the duration filter uses the result
    WEEKS_PER_UNIT = {DAYS: 1 / 7, WEEKS: 1, MONTHS: 4.3}


class WeekDay:
    """Nepal's week starts on Sunday, like the UI's day picker."""

    SUN, MON, TUE, WED, THU, FRI, SAT = "SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"
    ORDER = (SUN, MON, TUE, WED, THU, FRI, SAT)
    CHOICES = (
        (SUN, "Sun"),
        (MON, "Mon"),
        (TUE, "Tue"),
        (WED, "Wed"),
        (THU, "Thu"),
        (FRI, "Fri"),
        (SAT, "Sat"),
    )


class TrainingStatus:
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"  # "Pending Review" in the UI
    APPROVED = "APPROVED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    REJECTED = "REJECTED"
    UNPUBLISHED = "UNPUBLISHED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"  # set by a daily job once end_date has passed

    CHOICES = (
        (DRAFT, "Draft"),
        (SUBMITTED, "Pending review"),
        (APPROVED, "Approved"),
        (CHANGES_REQUESTED, "Changes requested"),
        (REJECTED, "Rejected"),
        (UNPUBLISHED, "Unpublished"),
        (CANCELLED, "Cancelled"),
        (EXPIRED, "Expired"),
    )
    TRANSITIONS = {
        DRAFT: {SUBMITTED},
        SUBMITTED: {APPROVED, CHANGES_REQUESTED, REJECTED, DRAFT},
        CHANGES_REQUESTED: {SUBMITTED},
        REJECTED: {SUBMITTED},
        APPROVED: {UNPUBLISHED, CANCELLED, EXPIRED, SUBMITTED},
        UNPUBLISHED: {APPROVED, CANCELLED, EXPIRED, SUBMITTED},
        CANCELLED: set(),
        EXPIRED: set(),
    }
    EDITABLE = {
        DRAFT,
        CHANGES_REQUESTED,
        REJECTED,
    }  # saved as is; the institute submits when ready
    REVIEWED_EDIT = {APPROVED, UNPUBLISHED}  # an edit goes straight back to review
    LIVE = {APPROVED, UNPUBLISHED}  # can be cancelled, and expires after end_date
    REASON_REQUIRED = {CHANGES_REQUESTED, REJECTED}
    FINISHED = {CANCELLED, EXPIRED}


SEARCH_CONFIG = "simple"  # no stemming: safe for English and romanised Nepali words


class TrainingShift:
    MORNING, DAY, EVENING = "Morning", "Day", "Evening"
    ORDER = (MORNING, DAY, EVENING)
    CHOICES = ((MORNING, "Morning"), (DAY, "Day"), (EVENING, "Evening"))


class DurationBucket:
    """The public duration filter. `WEEKS` is an inclusive (min, max) on `duration_weeks`;
    None is open-ended. A month is 4.3 weeks (see DurationUnit), so 1 month = 4 weeks and
    3 months = 13: "Under 1 month" is 3 weeks or less, "1 to 3 months" runs from 1 month to
    just under 3, and "3 months or more" starts at exactly 3."""

    UNDER_1_MONTH = "under-1-month"
    ONE_TO_THREE_MONTHS = "1-3-months"
    THREE_MONTHS_PLUS = "3-months-plus"
    CHOICES = (
        (UNDER_1_MONTH, "Under 1 month"),
        (ONE_TO_THREE_MONTHS, "1 to 3 months"),
        (THREE_MONTHS_PLUS, "3 months or more"),
    )
    WEEKS = {
        UNDER_1_MONTH: (None, 3),
        ONE_TO_THREE_MONTHS: (4, 12),
        THREE_MONTHS_PLUS: (13, None),
    }


class StartBucket:
    """The public start-date filter: rolling windows counted from today, each one including the
    shorter ones ("within 30 days" covers "within 2 weeks"). `DAYS` is the last day of each
    window; `LATER` starts the day after the longest. The dates are worked out when the filter
    runs (`services.start_date_range`), so this list never goes stale."""

    WITHIN_2_WEEKS, WITHIN_30_DAYS = "within-2-weeks", "within-30-days"
    WITHIN_60_DAYS, LATER = "within-60-days", "later"
    CHOICES = (
        (WITHIN_2_WEEKS, "Within 2 weeks"),
        (WITHIN_30_DAYS, "Within 30 days"),
        (WITHIN_60_DAYS, "Within 60 days"),
        (LATER, "Later"),
    )
    DAYS = {WITHIN_2_WEEKS: 14, WITHIN_30_DAYS: 30, WITHIN_60_DAYS: 60}
