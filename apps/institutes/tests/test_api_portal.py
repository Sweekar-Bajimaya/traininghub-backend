from datetime import timedelta
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from apps.institutes import services
from apps.institutes.constants import InstituteStatus, InvitationStatus, MemberRole
from apps.institutes.models import (
    Institute,
    InstituteDocument,
    InstituteGalleryImage,
    InstituteInvitation,
    InstituteMember,
)
from apps.institutes.tests.helpers import (
    PASSWORD,
    TempMediaMixin,
    User,
    add_location,
    count_queries,
    make_institute,
    make_municipality,
    pdf,
    png,
    reset_throttles,
)
from apps.users import services as user_services
from apps.users.constants import Role

BASE = "/api/v1/institute/"


def make_staff(institute, email):
    user = User.objects.create_user(email, PASSWORD, role=Role.INSTITUTE_STAFF)
    member = InstituteMember.objects.create(
        user=user, institute=institute, role=MemberRole.STAFF
    )
    return user, member


class PortalTestCase(TempMediaMixin, APITestCase):
    def setUp(self):
        super().setUp()
        reset_throttles()
        self.municipality = make_municipality()
        self.institute, self.owner = make_institute()
        self.staff, self.staff_member = make_staff(self.institute, "staff@example.com")
        self.other, self.other_owner = make_institute(
            name="Other Institute", email="other@example.com"
        )

    def as_(self, user):
        self.client.force_authenticate(user)
        return self.client


class PermissionMatrixTests(PortalTestCase):
    MEMBER_ENDPOINTS = ("profile/", "locations/", "documents/", "gallery/")
    OWNER_ENDPOINTS = ("staff/", "invitations/")

    def test_member_endpoints(self):
        admin = User.objects.create_user("admin@example.com", PASSWORD, role=Role.ADMIN)
        homeless = User.objects.create_user("homeless@example.com", PASSWORD)
        cases = (
            (None, 401),
            (admin, 403),
            (homeless, 403),  # an institute-staff account with no institute
            (self.owner, 200),
            (self.staff, 200),
        )
        for endpoint in self.MEMBER_ENDPOINTS:
            for user, expected in cases:
                with self.subTest(endpoint=endpoint, user=getattr(user, "email", "anonymous")):
                    self.client.force_authenticate(user)
                    self.assertEqual(self.client.get(BASE + endpoint).status_code, expected)

    def test_owner_only_endpoints(self):
        cases = ((None, 401), (self.staff, 403), (self.owner, 200))
        for endpoint in self.OWNER_ENDPOINTS:
            for user, expected in cases:
                with self.subTest(endpoint=endpoint, user=getattr(user, "email", "anonymous")):
                    self.client.force_authenticate(user)
                    self.assertEqual(self.client.get(BASE + endpoint).status_code, expected)


class ProfileTests(PortalTestCase):
    def test_get_returns_only_my_institute(self):
        res = self.as_(self.owner).get(BASE + "profile/")
        self.assertEqual(res.data["name"], "Alpha Institute")

    def test_patch_updates_profile_columns_for_owner_and_staff(self):
        for user in (self.owner, self.staff):
            with self.subTest(user=user.email):
                res = self.as_(user).patch(
                    BASE + "profile/",
                    {"ceo_name": f"CEO {user.email}", "website": "https://example.com"},
                    format="json",
                )
                self.assertEqual(res.status_code, 200, res.data)
        self.institute.refresh_from_db()
        self.assertEqual(self.institute.ceo_name, "CEO staff@example.com")
        self.assertEqual(self.institute.website, "https://example.com")

    def test_status_and_slug_cannot_be_changed(self):
        slug = self.institute.slug
        res = self.as_(self.owner).patch(
            BASE + "profile/", {"status": "APPROVED", "slug": "hacked"}, format="json"
        )
        self.assertEqual(res.status_code, 200)
        self.institute.refresh_from_db()
        self.assertEqual(self.institute.status, InstituteStatus.PENDING)
        self.assertEqual(self.institute.slug, slug)

    def test_another_institute_is_untouched(self):
        self.as_(self.owner).patch(BASE + "profile/", {"ceo_name": "Mine"}, format="json")
        self.other.refresh_from_db()
        self.assertEqual(self.other.ceo_name, "")

    def test_a_logo_with_a_bad_extension_is_refused(self):
        bad = SimpleUploadedFile("logo.exe", b"MZ", content_type="application/octet-stream")
        res = self.as_(self.owner).patch(BASE + "profile/", {"logo": bad}, format="multipart")
        self.assertEqual(res.status_code, 400)

    def test_put_is_not_allowed(self):
        self.assertEqual(self.as_(self.owner).put(BASE + "profile/", {}).status_code, 405)


class LocationTests(PortalTestCase):
    def create(self, user=None, **extra):
        data = {"location": self.municipality.pk, "address": "Road", **extra}
        return (self.as_(user or self.owner)).post(BASE + "locations/", data, format="json")

    def test_the_first_location_becomes_main_and_the_second_does_not(self):
        first, second = self.create(), self.create(address="Branch")
        self.assertEqual((first.status_code, second.status_code), (201, 201))
        self.assertTrue(first.data["is_main"])
        self.assertFalse(second.data["is_main"])
        self.assertEqual(first.data["district_name"], "District")
        self.assertEqual(first.data["province_name"], "Province")

    def test_staff_can_add_locations_too(self):
        self.assertEqual(self.create(user=self.staff).status_code, 201)

    def test_a_province_or_unknown_id_is_refused(self):
        for pk in (self.municipality.province_id, self.municipality.district_id, 999999):
            with self.subTest(pk=pk):
                res = self.as_(self.owner).post(
                    BASE + "locations/", {"location": pk, "address": "Road"}, format="json"
                )
                self.assertEqual(res.status_code, 400)

    def test_set_main_moves_the_main_office(self):
        first, second = self.create(), self.create(address="Branch")
        res = self.as_(self.owner).post(f"{BASE}locations/{second.data['id']}/set-main/")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data["is_main"])
        listing = self.client.get(BASE + "locations/").data["results"]
        self.assertEqual([r["is_main"] for r in listing], [True, False])
        self.assertEqual(listing[0]["id"], second.data["id"])

    def test_the_main_office_cannot_be_deactivated_but_a_branch_can(self):
        main, branch = self.create(), self.create(address="Branch")
        self.assertEqual(
            self.client.post(f"{BASE}locations/{main.data['id']}/deactivate/").status_code, 400
        )
        res = self.client.post(f"{BASE}locations/{branch.data['id']}/deactivate/")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.data["is_active"])

    def test_patch_changes_the_address_only(self):
        location = self.create()
        res = self.client.patch(
            f"{BASE}locations/{location.data['id']}/", {"address": "New Road"}, format="json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["address"], "New Road")
        self.assertTrue(res.data["is_main"])

    def test_the_list_shows_only_my_locations(self):
        self.create()
        add_location(self.other, self.municipality, is_main=True)
        self.assertEqual(len(self.client.get(BASE + "locations/").data["results"]), 1)

    def test_another_institutes_location_is_a_404(self):
        theirs = add_location(self.other, self.municipality, is_main=True)
        self.as_(self.owner)
        self.assertEqual(self.client.get(f"{BASE}locations/{theirs.pk}/").status_code, 404)
        self.assertEqual(
            self.client.patch(f"{BASE}locations/{theirs.pk}/", {"address": "x"}, format="json").status_code,
            404,
        )
        self.assertEqual(self.client.post(f"{BASE}locations/{theirs.pk}/set-main/").status_code, 404)
        self.assertEqual(self.client.post(f"{BASE}locations/{theirs.pk}/deactivate/").status_code, 404)

    def test_the_list_costs_a_constant_number_of_queries(self):
        self.create()
        self.client.get(BASE + "locations/")  # warm-up: the membership is loaded once
        one = count_queries(lambda: self.client.get(BASE + "locations/"))
        for i in range(6):
            self.create(address=f"Branch {i}")
        many = count_queries(lambda: self.client.get(BASE + "locations/"))
        self.assertEqual(one, many)


class DocumentTests(PortalTestCase):
    def upload(self, user=None, file=None, name="License"):
        return self.as_(user or self.owner).post(
            BASE + "documents/", {"name": name, "file": file or pdf()}, format="multipart"
        )

    def test_upload_never_echoes_the_file(self):
        res = self.upload()
        self.assertEqual(res.status_code, 201, res.data)
        self.assertNotIn("file", res.data)
        self.assertEqual(res.data["status"], "PENDING")
        self.assertEqual(self.institute.documents.count(), 1)

    def test_staff_can_upload_too(self):
        self.assertEqual(self.upload(user=self.staff).status_code, 201)

    def test_bad_extension_and_oversize_files_are_refused(self):
        exe = SimpleUploadedFile("run.exe", b"MZ", content_type="application/octet-stream")
        self.assertEqual(self.upload(file=exe).status_code, 400)
        with override_settings(INSTITUTE_UPLOAD_MAX_BYTES=5):
            self.assertEqual(self.upload().status_code, 400)
        self.assertEqual(self.institute.documents.count(), 0)

    def test_list_shows_my_documents_without_file_paths(self):
        self.upload()
        services.add_document(self.other, name="Theirs", file=pdf())
        res = self.client.get(BASE + "documents/")
        self.assertEqual([r["name"] for r in res.data["results"]], ["License"])
        self.assertNotIn("file", res.data["results"][0])

    def test_download_my_own_document(self):
        document = self.institute.documents.create(name="X", file=pdf())
        res = self.as_(self.owner).get(f"{BASE}documents/{document.pk}/download/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(b"".join(res.streaming_content), b"%PDF-1.4 test")

    def test_download_of_another_institutes_document_is_a_404(self):
        theirs = services.add_document(self.other, name="Theirs", file=pdf())
        res = self.as_(self.owner).get(f"{BASE}documents/{theirs.pk}/download/")
        self.assertEqual(res.status_code, 404)

    def test_no_url_is_ever_generated_for_a_private_file(self):
        document = self.institute.documents.create(name="X", file=pdf())
        with self.assertRaises(ValueError):
            document.file.url


class GalleryTests(PortalTestCase):
    def add(self, caption="Front", user=None):
        return self.as_(user or self.owner).post(
            BASE + "gallery/", {"image": png(), "caption": caption}, format="multipart"
        )

    def test_images_are_appended_in_order(self):
        first, second = self.add("One"), self.add("Two")
        self.assertEqual((first.status_code, second.status_code), (201, 201))
        self.assertEqual((first.data["position"], second.data["position"]), (0, 1))

    def test_reorder(self):
        a, b, c = [self.add(str(i)).data["id"] for i in range(3)]
        res = self.client.post(BASE + "gallery/reorder/", {"ids": [c, a, b]}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual([r["id"] for r in res.data], [c, a, b])

    def test_reorder_needs_every_id_exactly_once(self):
        a, b = [self.add(str(i)).data["id"] for i in range(2)]
        for ids in ([a], [a, a], [a, b, 999999]):
            with self.subTest(ids=ids):
                res = self.client.post(BASE + "gallery/reorder/", {"ids": ids}, format="json")
                self.assertEqual(res.status_code, 400)

    def test_rename_and_delete(self):
        image = self.add("Old").data["id"]
        res = self.client.patch(f"{BASE}gallery/{image}/", {"caption": "New"}, format="json")
        self.assertEqual(res.data["caption"], "New")
        self.assertEqual(self.client.delete(f"{BASE}gallery/{image}/").status_code, 204)
        self.assertFalse(InstituteGalleryImage.objects.filter(pk=image).exists())

    def test_a_non_image_is_refused(self):
        fake = SimpleUploadedFile("a.png", b"not an image", content_type="image/png")
        res = self.as_(self.owner).post(BASE + "gallery/", {"image": fake}, format="multipart")
        self.assertEqual(res.status_code, 400)

    def test_another_institutes_image_is_a_404(self):
        theirs = services.add_gallery_image(self.other, image=png("theirs.png"))
        self.as_(self.owner)
        self.assertEqual(self.client.patch(f"{BASE}gallery/{theirs.pk}/", {"caption": "x"}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(f"{BASE}gallery/{theirs.pk}/").status_code, 404)


class StaffTests(PortalTestCase):
    def test_list_shows_the_owner_and_staff_of_my_institute_only(self):
        make_staff(self.other, "theirs@example.com")
        res = self.as_(self.owner).get(BASE + "staff/")
        self.assertEqual(
            sorted(r["email"] for r in res.data["results"]),
            ["owner@example.com", "staff@example.com"],
        )

    def test_removing_staff_deactivates_the_account_and_revokes_tokens(self):
        refresh = RefreshToken.for_user(self.staff)
        res = self.as_(self.owner).delete(f"{BASE}staff/{self.staff_member.pk}/")
        self.assertEqual(res.status_code, 204)
        self.staff.refresh_from_db()
        self.assertFalse(self.staff.is_active)
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=refresh["jti"]).exists())

    def test_the_owner_cannot_be_removed(self):
        res = self.as_(self.owner).delete(f"{BASE}staff/{self.owner.membership.pk}/")
        self.assertEqual(res.status_code, 400)

    def test_staff_cannot_remove_anyone(self):
        res = self.as_(self.staff).delete(f"{BASE}staff/{self.staff_member.pk}/")
        self.assertEqual(res.status_code, 403)

    def test_another_institutes_member_is_a_404(self):
        res = self.as_(self.owner).delete(f"{BASE}staff/{self.other_owner.membership.pk}/")
        self.assertEqual(res.status_code, 404)

    def test_the_list_costs_a_constant_number_of_queries(self):
        self.as_(self.owner).get(BASE + "staff/")
        one = count_queries(lambda: self.client.get(BASE + "staff/"))
        for i in range(5):
            make_staff(self.institute, f"more{i}@example.com")
        many = count_queries(lambda: self.client.get(BASE + "staff/"))
        self.assertEqual(one, many)


class InvitationTests(PortalTestCase):
    def invite(self, email="new@example.com", user=None):
        with mock.patch("apps.institutes.services.async_task") as queued, \
                self.captureOnCommitCallbacks(execute=True):
            res = self.as_(user or self.owner).post(
                BASE + "invitations/", {"email": email}, format="json"
            )
        return res, queued

    def accept(self, token, **extra):
        payload = {"token": token, "full_name": "New Staff", "password": PASSWORD, **extra}
        return APIClient().post(BASE + "invitations/accept/", payload, format="json")

    def test_create_returns_no_token_and_queues_the_email(self):
        res, queued = self.invite()
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["status"], InvitationStatus.PENDING)
        self.assertEqual(res.data["role"], MemberRole.STAFF)
        self.assertNotIn(queued.call_args.args[2], str(res.data))
        queued.assert_called_once()

    def test_staff_cannot_invite(self):
        res, queued = self.invite(user=self.staff)
        self.assertEqual(res.status_code, 403)
        queued.assert_not_called()

    def test_an_existing_account_and_a_second_pending_invite_are_refused(self):
        self.assertEqual(self.invite(email="owner@example.com")[0].status_code, 400)
        self.assertEqual(self.invite()[0].status_code, 201)
        self.assertEqual(self.invite(email="NEW@example.com")[0].status_code, 400)

    def test_list_and_revoke(self):
        created, _ = self.invite()
        self.assertEqual(len(self.client.get(BASE + "invitations/").data["results"]), 1)
        res = self.client.delete(f"{BASE}invitations/{created.data['id']}/")
        self.assertEqual(res.status_code, 204)
        self.assertEqual(
            InstituteInvitation.objects.get(pk=created.data["id"]).status,
            InvitationStatus.REVOKED,
        )

    def test_another_institutes_invitation_is_a_404(self):
        theirs = InstituteInvitation.objects.create(
            institute=self.other, email="x@example.com", token_hash="h",
            expires_at=timezone.now() + timedelta(days=1),
        )
        res = self.as_(self.owner).delete(f"{BASE}invitations/{theirs.pk}/")
        self.assertEqual(res.status_code, 404)

    def test_accepting_creates_a_staff_account_that_can_log_in(self):
        _, queued = self.invite()
        res = self.accept(queued.call_args.args[2])
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data, {"email": "new@example.com"})
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.membership.institute, self.institute)
        self.assertEqual(user.membership.role, MemberRole.STAFF)
        login = APIClient().post(
            "/api/v1/user/auth/login/", {"email": "new@example.com", "password": PASSWORD}
        )
        self.assertEqual(login.status_code, 200)

    def test_a_token_works_once(self):
        _, queued = self.invite()
        token = queued.call_args.args[2]
        self.assertEqual(self.accept(token).status_code, 201)
        self.assertEqual(self.accept(token).status_code, 400)

    def test_bad_expired_and_weak_requests_are_400(self):
        created, queued = self.invite()
        token = queued.call_args.args[2]
        self.assertEqual(self.accept("nonsense").status_code, 400)
        self.assertEqual(self.accept(token, password="123").status_code, 400)
        InstituteInvitation.objects.filter(pk=created.data["id"]).update(expires_at=timezone.now())
        self.assertEqual(self.accept(token).status_code, 400)

    def test_the_eleventh_attempt_in_an_hour_is_throttled(self):
        for _ in range(10):
            self.assertEqual(self.accept("nonsense").status_code, 400)
        self.assertEqual(self.accept("nonsense").status_code, 429)

    def test_the_list_costs_a_constant_number_of_queries(self):
        make = lambda i: InstituteInvitation.objects.create(
            institute=self.institute, email=f"i{i}@example.com", token_hash=f"h{i}",
            expires_at=timezone.now() + timedelta(days=1),
        )
        make(0)  # an empty page skips the data query, so start from one row
        self.as_(self.owner).get(BASE + "invitations/")
        one = count_queries(lambda: self.client.get(BASE + "invitations/"))
        for i in range(1, 6):
            make(i)
        many = count_queries(lambda: self.client.get(BASE + "invitations/"))
        self.assertEqual(one, many)


class ResubmitTests(PortalTestCase):
    def test_allowed_from_rejected_and_info_requested(self):
        for status in (InstituteStatus.REJECTED, InstituteStatus.INFO_REQUESTED):
            with self.subTest(status=status):
                Institute.objects.filter(pk=self.institute.pk).update(status=status)
                res = self.as_(self.owner).post(BASE + "resubmit/")
                self.assertEqual(res.status_code, 200, res.data)
                self.assertEqual(res.data["status"], InstituteStatus.PENDING)

    def test_refused_from_pending_and_approved(self):
        for status in (InstituteStatus.PENDING, InstituteStatus.APPROVED):
            with self.subTest(status=status):
                Institute.objects.filter(pk=self.institute.pk).update(status=status)
                self.assertEqual(self.as_(self.owner).post(BASE + "resubmit/").status_code, 400)

    def test_staff_can_resubmit_too(self):
        Institute.objects.filter(pk=self.institute.pk).update(status=InstituteStatus.REJECTED)
        self.assertEqual(self.as_(self.staff).post(BASE + "resubmit/").status_code, 200)


class EndToEndTests(TempMediaMixin, APITestCase):
    """The whole journey, through the API only."""

    def test_register_upload_approve_publish_and_invite(self):
        reset_throttles()
        municipality = make_municipality(name="Pokhara")
        reviewer = user_services.create_admin(
            email="reviewer@example.com", password=PASSWORD, full_name="Reviewer",
            permissions=["manage_institutes"],
        )
        reviewer = User.objects.get(pk=reviewer.pk)

        # 1. register
        owner_client = APIClient()
        res = owner_client.post(
            BASE + "register/",
            {
                "name": "Journey Academy",
                "type": "LANGUAGE_SCHOOL",
                "owner": {"email": "boss@example.com", "full_name": "Boss", "password": PASSWORD},
                "locations": [{"location": municipality.pk, "address": "Lakeside"}],
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        slug = res.data["slug"]
        self.assertEqual(APIClient().get(f"/api/v1/institutes/{slug}/").status_code, 404)  # still pending

        # 2. log in and upload a verification document
        login = owner_client.post(
            "/api/v1/user/auth/login/", {"email": "boss@example.com", "password": PASSWORD}
        )
        owner_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        res = owner_client.post(
            BASE + "documents/", {"name": "Registration", "file": pdf()}, format="multipart"
        )
        self.assertEqual(res.status_code, 201, res.data)
        document_id = res.data["id"]

        # 3. an admin reviews the document and approves the institute
        admin_client = APIClient()
        admin_client.force_authenticate(reviewer)
        institute_id = Institute.objects.get(slug=slug).pk
        res = admin_client.patch(
            f"/api/v1/admin/institutes/{institute_id}/documents/{document_id}/",
            {"status": "VERIFIED"},
        )
        self.assertEqual(res.status_code, 200)
        res = admin_client.post(f"/api/v1/admin/institutes/{institute_id}/approve/")
        self.assertEqual(res.status_code, 200, res.data)

        # 4. it is now public
        public = APIClient().get(f"/api/v1/institutes/{slug}/")
        self.assertEqual(public.status_code, 200)
        self.assertEqual(public.data["locations"][0]["municipality"], "Pokhara")

        # 5. the owner invites a colleague, who accepts and logs in
        with mock.patch("apps.institutes.services.async_task") as queued, \
                self.captureOnCommitCallbacks(execute=True):
            res = owner_client.post(BASE + "invitations/", {"email": "colleague@example.com"}, format="json")
        self.assertEqual(res.status_code, 201, res.data)
        res = APIClient().post(
            BASE + "invitations/accept/",
            {"token": queued.call_args.args[2], "full_name": "Colleague", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        login = APIClient().post(
            "/api/v1/user/auth/login/", {"email": "colleague@example.com", "password": PASSWORD}
        )
        self.assertEqual(login.status_code, 200)
        self.assertEqual(InstituteDocument.objects.get(pk=document_id).status, "VERIFIED")
