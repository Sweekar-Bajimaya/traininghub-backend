MALE, FEMALE, OTHER = "Male", "Female", "Other"

GENDER_CHOICES = (
    (MALE, "Male"),
    (FEMALE, "Female"),
    (OTHER, "Other"),
)


class Role:
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    INSTITUTE_STAFF = "INSTITUTE_STAFF"

    CHOICES = (
        (SUPER_ADMIN, "Super admin"),
        (ADMIN, "Admin"),
        (INSTITUTE_STAFF, "Institute staff"),
    )


GRANTABLE_PERMISSIONS = (
    "manage_enquiries",
    "manage_account_status",
    "manage_institutes",
    "manage_trainings",
    "manage_categories",
)


class SocialPlatform:
    FACEBOOK, LINKEDIN, TWITTER, INSTAGRAM = (
        "facebook",
        "linkedin",
        "twitter",
        "instagram",
    )
    YOUTUBE, WEBSITE, OTHER = "youtube", "website", "other"
    CHOICES = (
        (FACEBOOK, "Facebook"),
        (LINKEDIN, "LinkedIn"),
        (TWITTER, "X (Twitter)"),
        (INSTAGRAM, "Instagram"),
        (YOUTUBE, "YouTube"),
        (WEBSITE, "Website"),
        (OTHER, "Other"),
    )


class OTPPurpose:
    """What a one-time code is for. Each purpose has its own cache keys, so a code issued for one
    flow can never be used in another."""

    PASSWORD_RESET = "password_reset"
    INSTITUTE_REGISTRATION = "institute_registration"


OTP_LENGTH = 6
OTP_TTL_SECONDS = 300  # a code is valid for 5 minutes (the email says so)
OTP_COOLDOWN_SECONDS = 60  # one code per address per minute
OTP_MAX_ATTEMPTS = 5  # wrong guesses allowed per code
