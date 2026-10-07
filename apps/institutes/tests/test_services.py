import hashlib
from datetime import timedelta
from unittest import mock

from django.core import mail
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.models.location import Location
from apps.institutes import services, tasks
from apps.institutes.constants import (
    DocumentStatus,
    InstituteStatus,
    InvitationStatus,
    MemberRole,
)
from apps.institutes.models import (
    Institute,
    InstituteGalleryImage,
    InstituteInvitation,
    InstituteLocation,
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
from apps.users.constants import Role


class WorkflowTests(TempMediaMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.institute, self.owner = make_institute()
        self.admin = User.objects.create_user(
            "admin@example.com", PASSWORD, role=Role.ADMIN
        )

    def test_every_pair_of_statuses(self):
        for start, allowed in InstituteStatus.TRANSITIONS.items():
            for target in InstituteStatus.TRANSITIONS:
                with self.subTest(start=start, target=target):
                    Institute.objects.filter(pk=self.institute.pk).update(status=start)
                    if target in allowed:
                        result = services._transition(
                            self.institute, target, reason="because"
                        )
                        self.assertEqual(result.status, target)
                    else:
                        with self.assertRaises(ValidationError):
                            services._transition(
                                self.institute, target, reason="because"
                            )

    def test_reason_is_required_to_reject_request_info_and_suspend(self):
        for service, status in (
            (services.reject, InstituteStatus.PENDING),
            (services.request_info, InstituteStatus.PENDING),
            (services.suspend, InstituteStatus.APPROVED),
        ):
            with self.subTest(service=service.__name__):
                Institute.objects.filter(pk=self.institute.pk).update(status=status)
                with self.assertRaises(ValidationError):
                    service(self.institute, by=self.admin, reason="  ")

    def test_reason_is_stored(self):
        result = services.reject(self.institute, by=self.admin, reason="Unclear scan")
        self.assertEqual(result.status_reason, "Unclear scan")

    def test_approval_needs_a_location_and_a_document(self):
        with self.assertRaises(ValidationError):
            services.approve(self.institute, by=self.admin)
        add_location(self.institute, make_municipality(), is_main=True)
        with self.assertRaises(ValidationError):
            services.approve(self.institute, by=self.admin)
        services.add_document(self.institute, name="License", file=pdf())
        self.assertEqual(
            services.approve(self.institute, by=self.admin).status,
            InstituteStatus.APPROVED,
        )

    def test_a_retired_location_does_not_count_for_approval(self):
        add_location(self.institute, make_municipality(), is_active=False)
        services.add_document(self.institute, name="License", file=pdf())
        with self.assertRaises(ValidationError):
            services.approve(self.institute, by=self.admin)

    def test_rejected_institute_can_re_apply(self):
        services.reject(self.institute, by=self.admin, reason="Unclear documents")
        self.assertEqual(
            services.resubmit(self.institute).status, InstituteStatus.PENDING
        )

    def test_info_request_can_be_answered(self):
        services.request_info(self.institute, by=self.admin, reason="Need the PAN")
        self.assertEqual(
            services.resubmit(self.institute).status, InstituteStatus.PENDING
        )

    def test_an_approved_institute_cannot_resubmit(self):
        Institute.objects.filter(pk=self.institute.pk).update(
            status=InstituteStatus.APPROVED
        )
        with self.assertRaises(ValidationError):
            services.resubmit(self.institute)

    def test_suspend_and_reinstate(self):
        Institute.objects.filter(pk=self.institute.pk).update(
            status=InstituteStatus.APPROVED
        )
        services.suspend(self.institute, by=self.admin, reason="Complaint")
        self.assertEqual(
            services.reinstate(self.institute, by=self.admin).status,
            InstituteStatus.APPROVED,
        )

    def test_suspended_staff_keep_their_accounts(self):
        Institute.objects.filter(pk=self.institute.pk).update(
            status=InstituteStatus.APPROVED
        )
        services.suspend(self.institute, by=self.admin, reason="Complaint")
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.is_active)


class RegistrationTests(TestCase):
    def setUp(self):
        self.municipality = make_municipality()
        self.owner = {
            "email": "new@example.com",
            "password": PASSWORD,
            "full_name": "New Owner",
        }
        self.data = {"name": "New Institute", "type": "COMPANY"}

    def test_creates_everything_with_the_first_location_as_main(self):
        institute = services.register(
            institute_data=self.data,
            owner=self.owner,
            locations=[
                {"location": self.municipality, "address": "A"},
                {"location": self.municipality, "address": "B"},
            ],
        )
        self.assertEqual(institute.status, InstituteStatus.PENDING)
        member = institute.members.get()
        self.assertEqual(member.role, MemberRole.OWNER)
        self.assertEqual(member.user.role, Role.INSTITUTE_STAFF)
        self.assertTrue(member.user.check_password(PASSWORD))
        self.assertEqual(
            list(
                institute.locations.order_by("pk").values_list("is_main", flat=True)
            ),
            [True, False],
        )

    def test_locations_are_optional(self):
        institute = services.register(institute_data=self.data, owner=self.owner)
        self.assertFalse(institute.locations.exists())

    def test_a_failure_leaves_nothing_behind(self):
        with mock.patch.object(
            InstituteLocation.objects, "bulk_create", side_effect=RuntimeError("boom")
        ):
            with self.assertRaises(RuntimeError):
                services.register(
                    institute_data=self.data,
                    owner=self.owner,
                    locations=[{"location": self.municipality, "address": "A"}],
                )
        self.assertFalse(Institute.objects.exists())
        self.assertFalse(User.objects.filter(email="new@example.com").exists())

    def test_a_province_is_not_a_valid_location(self):
        province = Location.objects.get(level="PROVINCE")
        with self.assertRaises(ValidationError):
            services.register(
                institute_data=self.data,
                owner=self.owner,
                locations=[{"location": province, "address": "A"}],
            )
        self.assertFalse(Institute.objects.exists())


class LocationTests(TestCase):
    def setUp(self):
        self.institute, _ = make_institute()
        self.municipality = make_municipality()

    def test_the_first_active_location_becomes_main(self):
        first = services.add_location(
            self.institute, location=self.municipality, address="A"
        )
        second = services.add_location(
            self.institute, location=self.municipality, address="B"
        )
        self.assertTrue(first.is_main)
        self.assertFalse(second.is_main)

    def test_a_district_cannot_be_used(self):
        district = Location.objects.get(level="DISTRICT")
        with self.assertRaises(ValidationError):
            services.add_location(self.institute, location=district, address="A")

    def test_a_retired_municipality_cannot_be_used(self):
        Location.objects.filter(pk=self.municipality.pk).update(is_active=False)
        self.municipality.refresh_from_db()
        with self.assertRaises(ValidationError):
            services.add_location(
                self.institute, location=self.municipality, address="A"
            )

    def test_set_main_moves_the_main_office(self):
        first = services.add_location(
            self.institute, location=self.municipality, address="A"
        )
        second = services.add_location(
            self.institute, location=self.municipality, address="B"
        )
        services.set_main_location(second)
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.is_main)
        self.assertTrue(second.is_main)
        self.assertEqual(self.institute.locations.filter(is_main=True).count(), 1)

    def test_an_inactive_location_cannot_become_main(self):
        add_location(self.institute, self.municipality, is_main=True)
        inactive = add_location(self.institute, self.municipality, is_active=False)
        with self.assertRaises(ValidationError):
            services.set_main_location(inactive)

    def test_the_main_office_cannot_be_deactivated(self):
        main = services.add_location(
            self.institute, location=self.municipality, address="A"
        )
        with self.assertRaises(ValidationError):
            services.deactivate_location(main)

    def test_a_branch_can_be_deactivated(self):
        services.add_location(self.institute, location=self.municipality, address="A")
        branch = services.add_location(
            self.institute, location=self.municipality, address="B"
        )
        self.assertFalse(services.deactivate_location(branch).is_active)

    def test_update_changes_the_address(self):
        location = services.add_location(
            self.institute, location=self.municipality, address="Old"
        )
        updated = services.update_location(location, address="New")
        self.assertEqual(updated.address, "New")


class DocumentAndGalleryTests(TempMediaMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.institute, _ = make_institute()
        self.admin = User.objects.create_user(
            "admin@example.com", PASSWORD, role=Role.ADMIN
        )

    def png(self, name="a.png"):
        return SimpleUploadedFile(name, b"not-really-a-png", content_type="image/png")

    def test_document_review(self):
        document = services.add_document(self.institute, name="License", file=pdf())
        self.assertEqual(document.status, DocumentStatus.PENDING)
        reviewed = services.review_document(
            document, status=DocumentStatus.VERIFIED, by=self.admin
        )
        self.assertEqual(reviewed.status, DocumentStatus.VERIFIED)

    def test_document_review_refuses_other_statuses(self):
        document = services.add_document(self.institute, name="License", file=pdf())
        with self.assertRaises(ValidationError):
            services.review_document(
                document, status=DocumentStatus.PENDING, by=self.admin
            )

    def test_gallery_images_are_appended_in_order(self):
        positions = [
            services.add_gallery_image(self.institute, image=self.png(f"{i}.png")).position
            for i in range(3)
        ]
        self.assertEqual(positions, [0, 1, 2])

    def test_gallery_reorder(self):
        a, b, c = [
            services.add_gallery_image(self.institute, image=self.png(f"{i}.png"))
            for i in range(3)
        ]
        services.reorder_gallery(self.institute, [c.pk, a.pk, b.pk])
        ordered = list(
            InstituteGalleryImage.objects.filter(institute=self.institute)
            .order_by("position")
            .values_list("pk", flat=True)
        )
        self.assertEqual(ordered, [c.pk, a.pk, b.pk])

    def test_gallery_reorder_needs_every_id_exactly_once(self):
        a, b = [
            services.add_gallery_image(self.institute, image=self.png(f"{i}.png"))
            for i in range(2)
        ]
        for ids in ([a.pk], [a.pk, a.pk], [a.pk, b.pk, 999999]):
            with self.subTest(ids=ids):
                with self.assertRaises(ValidationError):
                    services.reorder_gallery(self.institute, ids)

    def test_gallery_reorder_ignores_other_institutes_images(self):
        other, _ = make_institute(name="Other", email="other@example.com")
        foreign = services.add_gallery_image(other, image=self.png("x.png"))
        mine = services.add_gallery_image(self.institute, image=self.png("y.png"))
        with self.assertRaises(ValidationError):
            services.reorder_gallery(self.institute, [mine.pk, foreign.pk])


class InvitationTests(TestCase):
    def setUp(self):
        self.institute, self.owner = make_institute()

    def invite(self, email="new@example.com"):
        with mock.patch("apps.institutes.services.async_task") as queued, \
                self.captureOnCommitCallbacks(execute=True):
            invitation = services.invite(
                institute=self.institute, email=email, by=self.owner
            )
        return invitation, queued

    def test_only_a_hash_is_stored_and_the_task_is_not_saved(self):
        invitation, queued = self.invite()
        token = queued.call_args.args[2]
        self.assertEqual(
            invitation.token_hash, hashlib.sha256(token.encode()).hexdigest()
        )
        self.assertNotIn(token, invitation.token_hash)
        self.assertIs(queued.call_args.kwargs["save"], False)

    def test_the_email_is_queued_only_after_the_commit(self):
        with mock.patch("apps.institutes.services.async_task") as queued, \
                self.captureOnCommitCallbacks(execute=False) as callbacks:
            services.invite(
                institute=self.institute, email="new@example.com", by=self.owner
            )
        queued.assert_not_called()
        self.assertEqual(len(callbacks), 1)

    def test_invitations_are_always_for_staff_and_expire(self):
        invitation, _ = self.invite()
        self.assertEqual(invitation.role, MemberRole.STAFF)
        self.assertGreater(invitation.expires_at, timezone.now())

    def test_accept_works_once(self):
        invitation, queued = self.invite()
        token = queued.call_args.args[2]
        user = services.accept_invitation(
            token=token, full_name="New Staff", password=PASSWORD
        )
        self.assertEqual(user.membership.institute, self.institute)
        self.assertEqual(user.role, Role.INSTITUTE_STAFF)
        self.assertEqual(user.membership.role, MemberRole.STAFF)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, InvitationStatus.ACCEPTED)
        with self.assertRaises(ValidationError):
            services.accept_invitation(token=token, full_name="Again", password=PASSWORD)

    def test_an_unknown_token_is_refused(self):
        with self.assertRaises(ValidationError):
            services.accept_invitation(
                token="nonsense", full_name="X", password=PASSWORD
            )

    def test_expired_invitation_is_refused(self):
        invitation, queued = self.invite()
        InstituteInvitation.objects.filter(pk=invitation.pk).update(
            expires_at=timezone.now()
        )
        with self.assertRaises(ValidationError):
            services.accept_invitation(
                token=queued.call_args.args[2], full_name="X", password=PASSWORD
            )

    def test_existing_account_cannot_be_invited(self):
        with self.assertRaises(ValidationError):
            self.invite(email=self.owner.email.upper())

    def test_a_second_pending_invitation_is_refused_with_a_clear_error(self):
        self.invite()
        with self.assertRaises(ValidationError):
            self.invite(email="NEW@example.com")

    def test_an_expired_invitation_does_not_block_a_new_one(self):
        old, _ = self.invite()
        InstituteInvitation.objects.filter(pk=old.pk).update(
            expires_at=timezone.now() - timedelta(days=1)
        )
        new, _ = self.invite()
        old.refresh_from_db()
        self.assertEqual(old.status, InvitationStatus.REVOKED)
        self.assertEqual(new.status, InvitationStatus.PENDING)

    def test_a_revoked_invitation_cannot_be_accepted(self):
        invitation, queued = self.invite()
        services.revoke_invitation(invitation, by=self.owner)
        with self.assertRaises(ValidationError):
            services.accept_invitation(
                token=queued.call_args.args[2], full_name="X", password=PASSWORD
            )

    def test_only_a_pending_invitation_can_be_revoked(self):
        invitation, queued = self.invite()
        services.accept_invitation(
            token=queued.call_args.args[2], full_name="X", password=PASSWORD
        )
        with self.assertRaises(ValidationError):
            services.revoke_invitation(invitation, by=self.owner)

    def test_the_email_task_sends_the_link(self):
        invitation, queued = self.invite()
        token = queued.call_args.args[2]
        tasks.send_invitation_email(invitation.pk, token)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["new@example.com"])
        self.assertIn(f"/accept-invitation?token={token}", mail.outbox[0].body)

    def test_the_email_task_skips_a_revoked_invitation(self):
        invitation, queued = self.invite()
        services.revoke_invitation(invitation, by=self.owner)
        tasks.send_invitation_email(invitation.pk, queued.call_args.args[2])
        self.assertEqual(len(mail.outbox), 0)


class RemoveStaffTests(TestCase):
    def setUp(self):
        self.institute, self.owner = make_institute()
        self.staff = User.objects.create_user(
            "staff@example.com", PASSWORD, role=Role.INSTITUTE_STAFF
        )
        self.member = InstituteMember.objects.create(
            user=self.staff, institute=self.institute, role=MemberRole.STAFF
        )

    def test_removing_staff_deactivates_the_account_and_revokes_tokens(self):
        refresh = RefreshToken.for_user(self.staff)
        services.remove_staff(self.member, by=self.owner)
        self.staff.refresh_from_db()
        self.assertFalse(self.staff.is_active)
        self.assertFalse(InstituteMember.objects.filter(pk=self.member.pk).exists())
        self.assertTrue(
            BlacklistedToken.objects.filter(token__jti=refresh["jti"]).exists()
        )

    def test_the_owner_cannot_be_removed(self):
        owner_member = self.owner.membership
        with self.assertRaises(ValidationError):
            services.remove_staff(owner_member, by=self.owner)
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.is_active)
