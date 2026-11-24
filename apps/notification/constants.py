class Channel:
    IN_APP = "in_app"
    EMAIL = "email"


class EventType:
    # to the institute's staff
    INSTITUTE_APPROVED = "institute.approved"
    INSTITUTE_REJECTED = "institute.rejected"
    INSTITUTE_INFO_REQUESTED = "institute.info_requested"
    INSTITUTE_SUSPENDED = "institute.suspended"
    INSTITUTE_REINSTATED = "institute.reinstated"
    DOCUMENT_REJECTED = "document.rejected"
    TRAINING_SUBMITTED = "training.submitted"
    TRAINING_APPROVED = "training.approved"
    TRAINING_REJECTED = "training.rejected"
    TRAINING_CHANGES_REQUESTED = "training.changes_requested"
    ENQUIRY_NEW = "enquiry.new"
    ENQUIRY_CONVERTED = "enquiry.converted"
    MILESTONE_ENQUIRIES = "milestone.enquiries"
    MILESTONE_INTEREST = "milestone.interest"
    MILESTONE_CONVERTED = "milestone.converted"
    # to admins
    ADMIN_INSTITUTE_VERIFICATION = "admin.institute_verification"
    ADMIN_TRAINING_REVIEW = "admin.training_review"
    ADMIN_DOCUMENT_REUPLOADED = "admin.document_reuploaded"
    ADMIN_ACCOUNT_CREATED = "admin.account_created"


# how long the inbox keeps a notification (see services.purge_old)
RETENTION_READ_DAYS = 90
RETENTION_ANY_DAYS = 180
