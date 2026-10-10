class EnquiryStatus:
    """The seven statuses of the portal's Enquiries screen. Any status can move to any other (staff
    correct mistakes with the same dropdown), so there is no transitions table; the one guard is
    seats, see `services.change_status`."""

    NEW = "NEW"
    CONTACTED = "CONTACTED"
    FOLLOW_UP = "FOLLOW_UP"
    INTERESTED = "INTERESTED"
    CONVERTED = "CONVERTED"
    NOT_INTERESTED = "NOT_INTERESTED"
    CLOSED = "CLOSED"

    CHOICES = (
        (NEW, "New"),
        (CONTACTED, "Contacted"),
        (FOLLOW_UP, "Follow-up"),
        (INTERESTED, "Interested"),
        (CONVERTED, "Converted"),
        (NOT_INTERESTED, "Not interested"),
        (CLOSED, "Closed"),
    )
    VALUES = tuple(value for value, _ in CHOICES)
    # still being worked: one phone number has at most one such enquiry per training
    OPEN = (NEW, CONTACTED, FOLLOW_UP, INTERESTED)
    # what a visitor sees under "My enquiries" (the prototype's wording; the internal status stays
    # with the institute, so "Not interested" reads as "Closed")
    VISITOR_LABELS = {
        NEW: "Sent to institute",
        CONTACTED: "Institute contacted you",
        FOLLOW_UP: "Institute will follow up",
        INTERESTED: "Marked interested",
        CONVERTED: "Enrolled",
        NOT_INTERESTED: "Closed",
        CLOSED: "Closed",
    }


class EnquiryType:
    """An ENQUIRY asks about this batch. An INTEREST asks to hear about the next one, so it is
    still accepted when registration has closed or the seats are full."""

    ENQUIRY, INTEREST = "ENQUIRY", "INTEREST"
    CHOICES = ((ENQUIRY, "Enquiry"), (INTEREST, "Interest"))
    VALUES = tuple(value for value, _ in CHOICES)


class PreferredTime:
    MORNING, DAY, EVENING, WEEKEND = "MORNING", "DAY", "EVENING", "WEEKEND"
    CHOICES = (
        (MORNING, "Morning"),
        (DAY, "Day"),
        (EVENING, "Evening"),
        (WEEKEND, "Weekend"),
    )
    VALUES = tuple(value for value, _ in CHOICES)


MY_ENQUIRIES_DAYS = 90  # a device sees its enquiries for this long; the institute keeps them
PHONE_DAILY_LIMIT = 3  # enquiries accepted per phone number
PHONE_LIMIT_SECONDS = 24 * 60 * 60  # ... in this window (the IP limit is the `enquiry` throttle scope)
DEVICE_TOKEN_HEADER = "X-Device-Token"  # a UUID4 the browser makes and keeps (also in CORS_ALLOW_HEADERS)
MESSAGE_MAX_LENGTH = 2000
