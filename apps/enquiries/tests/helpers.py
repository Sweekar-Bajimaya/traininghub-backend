import uuid

from django.core.cache import cache

from apps.enquiries.models import Enquiry
from apps.training.tests.helpers import (  # noqa: F401  (re-exported for the enquiry tests)
    PASSWORD,
    User,
    approved_institute,
    count_queries,
    make_admin,
    make_category,
    make_training,
    reset_throttles,
)

_phones = iter(range(9800000000, 9899999999))


def next_phone():
    """A fresh valid mobile number each call, so one test never trips another's duplicate rule."""
    return str(next(_phones))


def new_token():
    return str(uuid.uuid4())


def reset_limits():
    """Clear the throttle counters and the per-phone allowances (and nothing else in Redis)."""
    reset_throttles()
    cache.delete_pattern("enquiry_phone_*")


def make_enquiry(training, **overrides):
    """Write the row directly (any status, no rules) with sensible defaults."""
    fields = dict(
        training=training,
        institute=training.institute,
        name="Ram Sharma",
        phone=next_phone(),
        device_token=new_token(),
    )
    fields.update(overrides)
    return Enquiry.objects.create(**fields)


def enquiry_payload(training, /, **overrides):
    """A complete public submit body."""
    data = {"training": training.slug, "name": "Ram Sharma", "phone": next_phone()}
    data.update(overrides)
    return data
