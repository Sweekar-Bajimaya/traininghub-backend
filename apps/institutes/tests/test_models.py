from importlib import import_module

from django.apps import apps as django_apps
from django.db import IntegrityError, connection, transaction
from django.test import TestCase
from django.utils import timezone

from apps.institutes.constants import DocumentStatus, InvitationStatus, MemberRole
from apps.institutes.models import (
    InstituteDocument,
    InstituteInvitation,
    InstituteMember,
)
from apps.institutes.tests.helpers import (
    PASSWORD,
    TempMediaMixin,
    User,
    add_location,
    make_institute,
    make_municipality,
    pdf,
)


class InstituteConstraintTests(TestCase):
    def setUp(self):
        self.institute, self.owner = make_institute()
        self.municipality = make_municipality()

    def test_second_owner_rejected(self):
        other = User.objects.create_user("other@example.com", PASSWORD)
        with self.assertRaises(IntegrityError), transaction.atomic():
            InstituteMember.objects.create(
                user=other, institute=self.institute, role=MemberRole.OWNER
            )

    def test_user_cannot_belong_to_two_institutes(self):
        other_institute, _ = make_institute(name="Beta", email="beta@example.com")
        with self.assertRaises(IntegrityError), transaction.atomic():
            InstituteMember.objects.create(
                user=self.owner, institute=other_institute, role=MemberRole.STAFF
            )

    def test_duplicate_pan_vat_number_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_institute(
                name="Beta",
                email="beta@example.com",
                pan_vat_number=self.institute.pan_vat_number,
            )

    def test_two_active_main_locations_rejected(self):
        add_location(self.institute, self.municipality, is_main=True)
        with self.assertRaises(IntegrityError), transaction.atomic():
            add_location(self.institute, self.municipality, is_main=True)

    def test_inactive_main_location_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            add_location(
                self.institute, self.municipality, is_main=True, is_active=False
            )

    def test_duplicate_pending_invitation_rejected_case_insensitively(self):
        make = lambda email, status: InstituteInvitation.objects.create(
            institute=self.institute,
            email=email,
            status=status,
            token_hash=email,
            expires_at=timezone.now(),
        )
        make("a@example.com", InvitationStatus.PENDING)
        with self.assertRaises(IntegrityError), transaction.atomic():
            make("A@Example.com", InvitationStatus.PENDING)
        make("b@example.com", InvitationStatus.REVOKED)  # revoked ones do not block
        make("B@example.com", InvitationStatus.PENDING)

    def test_duplicate_document_name_rejected_case_insensitively(self):
        self.institute.documents.create(name="PAN/VAT", file="a.pdf")
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.institute.documents.create(name="pan/vat", file="b.pdf")
        other, _ = make_institute(name="Beta", email="beta@example.com")
        other.documents.create(name="PAN/VAT", file="c.pdf")  # another institute may reuse it


class CollapseDuplicateDocumentsTests(TempMediaMixin, TestCase):
    """The data step of migration 0004, run on the rows an institute got before the constraint
    existed: a rejected document and the upload that followed it."""

    def setUp(self):
        super().setUp()
        self.institute, _ = make_institute()
        collapse = import_module(
            "apps.institutes.migrations.0004_document_one_row_per_name"
        ).collapse_duplicate_documents
        constraint = InstituteDocument._meta.constraints[0]
        with connection.schema_editor() as editor:  # rolled back with the test (Postgres DDL)
            editor.remove_constraint(InstituteDocument, constraint)
            self.collapse = lambda: collapse(django_apps, editor)

    def make(self, name, status):
        return InstituteDocument.objects.create(
            institute=self.institute, name=name, status=status, file=pdf()
        )

    def test_the_newest_row_is_kept_and_marked_re_uploaded(self):
        self.make("PAN/VAT", DocumentStatus.REJECTED)
        newest = self.make("pan/vat", DocumentStatus.PENDING)
        self.make("License", DocumentStatus.VERIFIED)
        with self.captureOnCommitCallbacks(execute=True):
            self.collapse()
        rows = InstituteDocument.objects.order_by("name")
        self.assertEqual(
            [(r.pk, r.status) for r in rows if r.name.lower() == "pan/vat"],
            [(newest.pk, DocumentStatus.RE_UPLOADED)],
        )
        self.assertEqual(rows.count(), 2)  # the License is untouched
        self.assertEqual(rows.get(name="License").status, DocumentStatus.VERIFIED)

    def test_a_newer_row_that_is_already_reviewed_keeps_its_status(self):
        self.make("PAN/VAT", DocumentStatus.REJECTED)
        newest = self.make("PAN/VAT", DocumentStatus.VERIFIED)
        self.collapse()
        self.assertEqual(
            list(InstituteDocument.objects.values_list("pk", "status")),
            [(newest.pk, DocumentStatus.VERIFIED)],
        )
