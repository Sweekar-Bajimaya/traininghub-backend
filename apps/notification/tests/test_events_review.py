from django.test import TestCase

from apps.institutes import services as institute_services
from apps.institutes.constants import InstituteStatus
from apps.institutes.tests.helpers import make_institute
from apps.notification.constants import EventType
from apps.notification.models import Notification
from apps.notification.tests.helpers import (
    NoQueueMixin,
    approved_institute,
    make_admin,
)
from apps.training import services as training_services
from apps.training.constants import TrainingStatus
from apps.training.tests.helpers import make_training
from apps.users import services as user_services


class InstituteReviewEventTests(NoQueueMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.reviewer = make_admin(
            "reviewer@example.com", permissions=("manage_institutes",)
        )
        self.other_admin = make_admin(
            "other@example.com", permissions=("manage_enquiries",)
        )

    def test_a_rejection_tells_the_owner_why(self):
        institute, owner = make_institute(
            name="Gamma", email="gamma@example.com", status=InstituteStatus.PENDING
        )
        institute_services.reject(institute, by=self.reviewer, reason="Blurry PAN")
        row = Notification.objects.get(
            recipient=owner, type=EventType.INSTITUTE_REJECTED
        )
        self.assertEqual(row.payload["reason"], "Blurry PAN")

    def test_a_reinstatement_is_not_an_approval(self):
        institute, owner, _ = approved_institute()
        institute_services.suspend(
            institute, by=self.reviewer, reason="Late compliance"
        )
        institute_services.reinstate(institute, by=self.reviewer)
        types = set(
            Notification.objects.filter(recipient=owner).values_list("type", flat=True)
        )
        self.assertEqual(
            types, {EventType.INSTITUTE_SUSPENDED, EventType.INSTITUTE_REINSTATED}
        )

    def test_a_resubmit_tells_only_admins_who_can_review_it(self):
        institute, owner = make_institute(
            name="Delta", email="delta@example.com", status=InstituteStatus.REJECTED
        )
        institute_services.resubmit(institute, by=owner)
        verification = Notification.objects.filter(
            type=EventType.ADMIN_INSTITUTE_VERIFICATION
        )
        self.assertTrue(verification.filter(recipient=self.reviewer).exists())
        self.assertFalse(verification.filter(recipient=self.other_admin).exists())
        self.assertFalse(
            Notification.objects.filter(recipient=owner).exists()
        )  # not told about their own action


class TrainingReviewEventTests(NoQueueMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.institute, self.owner, _ = approved_institute()
        self.reviewer = make_admin(
            "reviewer@example.com", permissions=("manage_trainings",)
        )

    def test_submit_tells_the_institute_and_the_reviewers(self):
        training = make_training(self.institute, status=TrainingStatus.DRAFT)
        training_services.submit(training, by=self.owner)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.owner, type=EventType.TRAINING_SUBMITTED
            ).exists()
        )
        row = Notification.objects.get(
            recipient=self.reviewer, type=EventType.ADMIN_TRAINING_REVIEW
        )
        self.assertEqual(row.payload["action"], "submitted")

    def test_an_edit_of_an_approved_training_also_reaches_the_reviewers(self):
        training = make_training(self.institute, status=TrainingStatus.APPROVED)
        training_services.update_training(training, title="New title")
        row = Notification.objects.get(
            recipient=self.reviewer, type=EventType.ADMIN_TRAINING_REVIEW
        )
        self.assertEqual(row.payload["action"], "resubmitted")

    def test_a_rejection_carries_the_reason(self):
        training = make_training(self.institute, status=TrainingStatus.SUBMITTED)
        training_services.reject(training, by=self.reviewer, reason="Duplicate")
        row = Notification.objects.get(
            recipient=self.owner, type=EventType.TRAINING_REJECTED
        )
        self.assertEqual(row.payload["reason"], "Duplicate")


class AdminAccountEventTests(NoQueueMixin, TestCase):
    def test_a_new_admin_gets_a_password_note_and_no_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            admin = user_services.create_admin(
                email="new@example.com",
                password="Str0ng-pass-123",
                full_name="New Admin",
            )
        row = Notification.objects.get(
            recipient=admin, type=EventType.ADMIN_ACCOUNT_CREATED
        )
        self.assertIn("password", row.body)
        self.queued.assert_not_called()  # admin events are in-app only
