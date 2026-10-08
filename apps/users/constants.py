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
