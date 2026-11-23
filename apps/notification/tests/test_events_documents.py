from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.institutes import services as institute_services
from apps.institutes.constants import DocumentStatus
from apps.institutes.models import InstituteDocument
from apps.notification.constants import EventType
from apps.notification.models import Notification
from apps.notification.tests.helpers import NoQueueMixin, approved_institute, make_admin


class DocumentEventTests(NoQueueMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.institute, self.owner, _ = approved_institute()
        self.reviewer = make_admin(
            "reviewer@example.com", permissions=("manage_institutes",)
        )
        self.document = InstituteDocument.objects.create(
            institute=self.institute,
            name="PAN",
            file=SimpleUploadedFile("pan.pdf", b"%PDF-1.4"),
        )

    def test_a_rejection_tells_the_staff_what_to_fix(self):
        institute_services.review_document(
            self.document,
            status=DocumentStatus.REJECTED,
            by=self.reviewer,
            reason="Not legible",
        )
        row = Notification.objects.get(
            recipient=self.owner, type=EventType.DOCUMENT_REJECTED
        )
        self.assertEqual(row.payload["reason"], "Not legible")

    def test_a_rejection_without_a_reason_says_so(self):
        institute_services.review_document(
            self.document, status=DocumentStatus.REJECTED, by=self.reviewer
        )
        row = Notification.objects.get(
            recipient=self.owner, type=EventType.DOCUMENT_REJECTED
        )
        self.assertEqual(row.payload["reason"], "No reason was given.")

    def test_verifying_sends_nothing(self):
        institute_services.review_document(
            self.document, status=DocumentStatus.VERIFIED, by=self.reviewer
        )
        self.assertFalse(Notification.objects.filter(recipient=self.owner).exists())

    def test_a_reupload_tells_the_reviewers(self):
        institute_services.review_document(
            self.document,
            status=DocumentStatus.REJECTED,
            by=self.reviewer,
            reason="Blurry",
        )
        institute_services.reupload_document(
            self.document, file=SimpleUploadedFile("pan2.pdf", b"%PDF-1.4")
        )
        row = Notification.objects.get(
            recipient=self.reviewer, type=EventType.ADMIN_DOCUMENT_REUPLOADED
        )
        self.assertEqual(row.payload["document_name"], "PAN")
