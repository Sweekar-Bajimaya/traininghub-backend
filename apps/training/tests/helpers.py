from datetime import time, timedelta
from decimal import Decimal

from django.utils import timezone

from apps.catalog.tests.helpers import make_category  # noqa: F401  (re-exported)
from apps.institutes.constants import InstituteStatus
from apps.institutes.tests.helpers import (  # noqa: F401  (re-exported for the training tests)
    PASSWORD,
    TempMediaMixin,
    User,
    add_location,
    count_queries,
    make_institute,
    make_municipality,
    png,
    reset_throttles,
)
from apps.training import services
from apps.training.constants import TrainingStatus
from apps.training.models import Training, TrainingSession
from apps.users import services as user_services


def approved_institute(name="Alpha Institute", email="owner@example.com", code=1):
    institute, owner = make_institute(name=name, email=email, status=InstituteStatus.APPROVED)
    location = add_location(
        institute, make_municipality(code=code, name=f"Municipality {code}"), is_main=True
    )
    return institute, owner, location


def make_admin(email, permissions=("manage_trainings",)):
    admin = user_services.create_admin(
        email=email, password=PASSWORD, full_name="Admin", permissions=permissions
    )
    return User.objects.get(pk=admin.pk)  # fresh instance: permissions are cached per object


def make_training(
    institute, *, category=None, location=None, status=TrainingStatus.APPROVED, **overrides
):
    """Writes the row directly (any status, no checks) and then builds its search vector."""
    today = timezone.localdate()
    fields = dict(
        title="Python Bootcamp",
        short_description="Learn Python from scratch",
        overview="A detailed description",
        mode="ONLINE",
        level="BEGINNER",
        duration_value=8,
        duration_unit="WEEKS",
        duration_weeks=8,
        fee_npr=Decimal("5000"),
        skills=["Python", "Git"],
        start_date=today + timedelta(days=30),
        end_date=today + timedelta(days=90),
        registration_deadline=today + timedelta(days=20),
        status=status,
        published_at=timezone.now() if status == TrainingStatus.APPROVED else None,
    )
    if location is not None:
        fields["mode"] = "PHYSICAL"  # a located training is physical unless the test says otherwise
    fields.update(overrides)
    training = Training.objects.create(
        institute=institute,
        category=category or make_category(),
        institute_location=location,
        **fields,
    )
    TrainingSession.objects.create(
        training=training,
        class_days=["SUN", "MON", "TUE"],
        start_time=time(7, 0),
        end_time=time(9, 0),
    )
    services.refresh_search_vector(training)
    training.refresh_from_db()
    return training


def training_payload(category, **overrides):
    """A complete portal create body (online, so no location needed)."""
    today = timezone.localdate()
    data = {
        "title": "Barista Course",
        "category": category.pk,
        "short_description": "Coffee basics",
        "overview": "Espresso, milk and latte art",
        "mode": "ONLINE",
        "level": "BEGINNER",
        "duration_value": 6,
        "duration_unit": "WEEKS",
        "fee_npr": "18500.00",
        "start_date": str(today + timedelta(days=30)),
        "end_date": str(today + timedelta(days=72)),
        "skills": ["Espresso", "Latte art"],
        "sessions": [
            {"class_days": ["SUN", "MON", "TUE", "WED", "THU", "FRI"], "start_time": "07:00", "end_time": "09:00"}
        ],
        "modules": [{"title": "Espresso"}, {"title": "Milk", "description": "Steaming"}],
        "outcomes": [{"text": "Pull a shot"}],
    }
    data.update(overrides)
    return data
