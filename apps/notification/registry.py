from dataclasses import dataclass

from apps.notification.constants import Channel, EventType

IN_APP = (Channel.IN_APP,)
BOTH = (Channel.IN_APP, Channel.EMAIL)


@dataclass(frozen=True)
class Event:
    channels: tuple
    title: str  # str.format over the payload; plain text
    body: str = ""
    # Blank means "use the title". Set it whenever the title carries text a visitor typed.
    email_subject: str = ""

    def render(self, payload):
        title = self.title.format_map(payload)[:200]
        body = self.body.format_map(payload)[:500]
        return title, body

    def subject(self, payload):
        return (self.email_subject or self.title).format_map(payload)


EVENTS = {
    # --- to the institute's staff: in-app + email ---
    # payload: institute_name, institute_slug, reason
    EventType.INSTITUTE_APPROVED: Event(
        BOTH,
        "Your institute is verified",
        "{institute_name} is approved. You can now add trainings.",
    ),
    EventType.INSTITUTE_REJECTED: Event(
        BOTH, "Your institute was rejected", "Reason: {reason}"
    ),
    EventType.INSTITUTE_INFO_REQUESTED: Event(
        BOTH, "More information requested", "{reason}"
    ),
    EventType.INSTITUTE_SUSPENDED: Event(
        BOTH, "Your institute was suspended", "Reason: {reason}"
    ),
    EventType.INSTITUTE_REINSTATED: Event(
        BOTH,
        "Your institute is active again",
        "{institute_name} is visible on TrainingHub again.",
    ),
    # payload: institute_name, document_name, reason
    EventType.DOCUMENT_REJECTED: Event(
        BOTH, "Document rejected: {document_name}", "{reason}"
    ),
    # payload: training_title, training_slug, action ("submitted" or "resubmitted")
    EventType.TRAINING_SUBMITTED: Event(
        BOTH,
        "Training {action} for review",
        "“{training_title}” is waiting for an admin.",
    ),
    # payload: training_title, training_slug
    EventType.TRAINING_APPROVED: Event(
        BOTH, "Training approved", "“{training_title}” is now live on TrainingHub."
    ),
    # payload: training_title, training_slug, reason
    EventType.TRAINING_REJECTED: Event(
        BOTH, "Training rejected", "“{training_title}” was rejected. Reason: {reason}"
    ),
    EventType.TRAINING_CHANGES_REQUESTED: Event(
        BOTH,
        "Changes requested",
        "Admin asked for changes to “{training_title}”: {reason}",
    ),
    # payload: kind ("enquiry" or "interest"), name, enquiry_id, training_title, training_slug
    EventType.ENQUIRY_NEW: Event(
        BOTH,
        "New {kind} from {name}",
        "About “{training_title}”.",
        email_subject="New {kind} on TrainingHub",  # the visitor's name stays out of the subject
    ),
    # payload: name, enquiry_id, training_title, training_slug, changed_by
    EventType.ENQUIRY_CONVERTED: Event(
        BOTH,
        "Enquiry converted: {name}",
        "“{training_title}”, changed by {changed_by}.",
        email_subject="An enquiry was converted on TrainingHub",
    ),
    # payload: training_title, training_slug, threshold
    EventType.MILESTONE_ENQUIRIES: Event(
        BOTH,
        "{threshold} enquiries on “{training_title}”",
        "Your training has reached {threshold} enquiries.",
    ),
    EventType.MILESTONE_INTEREST: Event(
        BOTH,
        "{threshold} people are interested in “{training_title}”",
        "{threshold} people have shown interest.",
    ),
    # payload: training_title, training_slug, percent, converted, seats
    EventType.MILESTONE_CONVERTED: Event(
        BOTH,
        "“{training_title}” is {percent}% full",
        "{converted} of {seats} seats are taken by converted enquiries.",
    ),
    # --- to admins: in-app only, except admin.account_created (in-app + email).
    # --- to switch email on for another event, use BOTH. -----
    # payload: institute_name, institute_slug, action ("requested verification", "re-applied" or
    # "answered the information request")
    EventType.ADMIN_INSTITUTE_VERIFICATION: Event(
        IN_APP,
        "{institute_name} {action}",
        "Review the registration and its documents.",
    ),
    # payload: institute_name, institute_slug, training_title, training_slug, action
    EventType.ADMIN_TRAINING_REVIEW: Event(
        IN_APP,
        "{institute_name} {action} a training",
        "“{training_title}” is waiting for review.",
    ),
    # payload: institute_name, institute_slug, document_name
    EventType.ADMIN_DOCUMENT_REUPLOADED: Event(
        IN_APP,
        "{institute_name} re-uploaded {document_name}",
        "A rejected document is waiting for review.",
    ),
    # payload: full_name
    EventType.ADMIN_ACCOUNT_CREATED: Event(
        BOTH,
        "Welcome to the admin console",
        "Your account was created by the Super Admin. Change your password after you sign in.",
    ),
}
