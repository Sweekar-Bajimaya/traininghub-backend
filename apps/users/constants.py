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

SOCIAL_PLATFORM_CHOICES = [
    ("facebook", "Facebook"),
    ("linkedin", "LinkedIn"),
    ("twitter", "X (Twitter)"),
    ("instagram", "Instagram"),
    ("youtube", "YouTube"),
    ("website", "Website"),
    ("other", "Other"),
]
