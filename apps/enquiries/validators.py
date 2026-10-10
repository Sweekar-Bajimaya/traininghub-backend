import re

# A Nepal mobile number: ten digits starting 96, 97 or 98, with an optional country code. The code
# is only dropped when ten digits remain, so a number that itself starts 977 is kept as typed.
NEPAL_MOBILE_REGEX = re.compile(r"(?:\+?977)?(9[678]\d{8})")
PHONE_DB_REGEX = r"^9[678][0-9]{8}$"  # what is stored; the check constraint uses the same


def normalize_phone(value):
    """'+977 984-1526370' gives '9841526370'; anything that is not a mobile number gives None."""
    match = NEPAL_MOBILE_REGEX.fullmatch(re.sub(r"[\s-]", "", str(value)))
    return match.group(1) if match else None
