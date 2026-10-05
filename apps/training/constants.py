class TrainingMode:
    PHYSICAL, ONLINE, HYBRID = "PHYSICAL", "ONLINE", "HYBRID"
    CHOICES = ((PHYSICAL, "Physical"), (ONLINE, "Online"), (HYBRID, "Hybrid"))


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
    EDITABLE = {DRAFT, CHANGES_REQUESTED, REJECTED}  # saved as is; the institute submits when ready
    REVIEWED_EDIT = {APPROVED, UNPUBLISHED}  # an edit goes straight back to review
    LIVE = {APPROVED, UNPUBLISHED}  # can be cancelled, and expires after end_date
    REASON_REQUIRED = {CHANGES_REQUESTED, REJECTED}
    FINISHED = {CANCELLED, EXPIRED}


SEARCH_CONFIG = "simple"  # no stemming: safe for English and romanised Nepali words
