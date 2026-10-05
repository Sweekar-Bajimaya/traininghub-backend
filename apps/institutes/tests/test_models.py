from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from apps.institutes.constants import InvitationStatus, MemberRole
from apps.institutes.models import InstituteInvitation, InstituteMember
from apps.institutes.tests.helpers import (
    PASSWORD,
    User,
    add_location,
    make_institute,
    make_municipality,
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
