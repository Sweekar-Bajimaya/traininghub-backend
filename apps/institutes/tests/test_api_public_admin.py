from rest_framework.test import APITestCase

from apps.institutes import services
from apps.institutes.constants import InstituteStatus
from apps.institutes.models import Institute, InstituteLocation
from apps.institutes.tests.helpers import (
    PASSWORD,
    TempMediaMixin,
    User,
    add_location,
    count_queries,
    make_institute,
    make_municipality,
    pdf,
    reset_throttles,
)
from apps.users import services as user_services
from apps.users.constants import Role

REGISTER_URL = "/api/v1/institute/register/"
PUBLIC_URL = "/api/v1/institutes/"
ADMIN_URL = "/api/v1/admin/institutes/"


class RegistrationApiTests(APITestCase):
    def setUp(self):
        reset_throttles()
        self.municipality = make_municipality()

    def payload(self, **overrides):
        data = {
            "name": "New Institute",
            "type": "COMPANY",
            "owner": {
                "email": "owner@example.com",
                "full_name": "Owner",
                "password": PASSWORD,
            },
            "locations": [{"location": self.municipality.pk, "address": "Main Road"}],
        }
        data.update(overrides)
        return data

    def post(self, **overrides):
        return self.client.post(REGISTER_URL, self.payload(**overrides), format="json")

    def test_registers_institute_owner_and_location(self):
        res = self.post()
        self.assertEqual(res.status_code, 201, res.data)
        institute = Institute.objects.get(slug=res.data["slug"])
        self.assertEqual(institute.status, InstituteStatus.PENDING)
        self.assertEqual(institute.members.get().user.email, "owner@example.com")
        self.assertTrue(institute.locations.get().is_main)

    def test_the_response_never_echoes_credentials(self):
        res = self.post()
        self.assertNotIn("owner", res.data)
        self.assertNotIn("password", str(res.data))

    def test_status_slug_and_role_in_the_payload_are_ignored(self):
        res = self.post(
            status="APPROVED",
            slug="hacked",
            owner={
                "email": "owner@example.com",
                "full_name": "Owner",
                "password": PASSWORD,
                "role": "SUPER_ADMIN",
                "is_staff": True,
            },
        )
        self.assertEqual(res.status_code, 201, res.data)
        institute = Institute.objects.get(slug=res.data["slug"])
        self.assertEqual(institute.status, InstituteStatus.PENDING)
        self.assertNotEqual(institute.slug, "hacked")
        owner = institute.members.get().user
        self.assertEqual(owner.role, Role.INSTITUTE_STAFF)
        self.assertFalse(owner.is_staff)

    def test_locations_are_required(self):
        payload = self.payload()
        del payload["locations"]
        res = self.client.post(REGISTER_URL, payload, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("locations", res.data)
        self.assertFalse(Institute.objects.exists())

    def test_an_empty_locations_list_is_refused(self):
        res = self.post(locations=[])
        self.assertEqual(res.status_code, 400)
        self.assertIn("locations", res.data)
        self.assertFalse(Institute.objects.exists())

    def test_duplicate_email_is_a_400_in_any_case(self):
        User.objects.create_user("Owner@Example.com", PASSWORD)
        self.assertEqual(self.post().status_code, 400)

    def test_a_province_is_not_a_valid_location(self):
        province_id = self.municipality.province_id
        res = self.post(locations=[{"location": province_id, "address": "Road"}])
        self.assertEqual(res.status_code, 400)
        self.assertFalse(Institute.objects.exists())

    def test_weak_password_unknown_type_and_missing_owner_are_400(self):
        weak = {"email": "o@example.com", "full_name": "O", "password": "123"}
        self.assertEqual(self.post(owner=weak).status_code, 400)
        self.assertEqual(self.post(type="SCHOOL").status_code, 400)
        payload = self.payload()
        del payload["owner"]
        self.assertEqual(
            self.client.post(REGISTER_URL, payload, format="json").status_code, 400
        )

    def test_the_owner_can_log_in_while_the_institute_is_pending(self):
        self.post()
        res = self.client.post(
            "/api/v1/user/auth/login/",
            {"email": "owner@example.com", "password": PASSWORD},
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)

    def test_the_sixth_registration_in_an_hour_is_throttled(self):
        for i in range(5):
            owner = {
                "email": f"owner{i}@example.com",
                "full_name": "Owner",
                "password": PASSWORD,
            }
            self.assertEqual(self.post(name=f"Institute {i}", owner=owner).status_code, 201)
        owner = {"email": "owner9@example.com", "full_name": "Owner", "password": PASSWORD}
        self.assertEqual(self.post(name="One more", owner=owner).status_code, 429)


class PublicInstituteApiTests(TempMediaMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.municipality = make_municipality(name="Kathmandu")

    def approved(self, name, email, **kwargs):
        institute, _ = make_institute(
            name=name, email=email, status=InstituteStatus.APPROVED
        )
        add_location(institute, self.municipality, is_main=True)
        return institute

    def test_only_approved_institutes_are_listed(self):
        shown = self.approved("Shown", "shown@example.com")
        for status in (
            InstituteStatus.PENDING,
            InstituteStatus.REJECTED,
            InstituteStatus.INFO_REQUESTED,
            InstituteStatus.SUSPENDED,
        ):
            make_institute(name=f"Hidden {status}", email=f"{status}@example.com", status=status)
        res = self.client.get(PUBLIC_URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual([r["slug"] for r in res.data["results"]], [shown.slug])

    def test_a_suspended_institute_disappears(self):
        institute = self.approved("Alpha", "alpha@example.com")
        admin = User.objects.create_user("a@example.com", PASSWORD, role=Role.ADMIN)
        services.suspend(institute, by=admin, reason="Complaint")
        self.assertEqual(self.client.get(PUBLIC_URL).data["results"], [])
        self.assertEqual(self.client.get(f"{PUBLIC_URL}{institute.slug}/").status_code, 404)

    def test_the_card_shows_the_main_location_with_district_and_province(self):
        self.approved("Alpha", "alpha@example.com")
        card = self.client.get(PUBLIC_URL).data["results"][0]
        self.assertEqual(
            card["location"],
            {
                "municipality": "Kathmandu",
                "district": "District",
                "province": "Province",
                "address": "Main Road",
                "map_url": "",
            },
        )

    def test_the_map_link_is_saved_and_shown(self):
        institute = self.approved("Alpha", "alpha@example.com")
        InstituteLocation.objects.filter(institute=institute).update(
            map_url="https://maps.example/alpha"
        )
        card = self.client.get(PUBLIC_URL).data["results"][0]
        self.assertEqual(card["location"]["map_url"], "https://maps.example/alpha")
        detail = self.client.get(f"{PUBLIC_URL}{institute.slug}/").data
        self.assertEqual(detail["locations"][0]["map_url"], "https://maps.example/alpha")

    def test_detail_by_slug(self):
        institute = self.approved("Alpha", "alpha@example.com")
        res = self.client.get(f"{PUBLIC_URL}{institute.slug}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["name"], "Alpha")
        self.assertEqual(len(res.data["locations"]), 1)
        self.assertEqual(res.data["gallery"], [])

    def test_a_pending_institute_has_no_public_page(self):
        institute, _ = make_institute()
        self.assertEqual(self.client.get(f"{PUBLIC_URL}{institute.slug}/").status_code, 404)

    def test_retired_locations_are_not_shown(self):
        institute = self.approved("Alpha", "alpha@example.com")
        add_location(institute, self.municipality, is_active=False)
        res = self.client.get(f"{PUBLIC_URL}{institute.slug}/")
        self.assertEqual(len(res.data["locations"]), 1)

    def test_filter_by_type_and_search_by_name(self):
        self.approved("Alpha Academy", "alpha@example.com")
        res = self.client.get(PUBLIC_URL, {"search": "academy"})
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(self.client.get(PUBLIC_URL, {"search": "zzz"}).data["results"], [])
        self.assertEqual(len(self.client.get(PUBLIC_URL, {"type": "COMPANY"}).data["results"]), 1)
        self.assertEqual(self.client.get(PUBLIC_URL, {"type": "GOVERNMENT"}).data["results"], [])

    def test_the_list_costs_the_same_number_of_queries_for_one_or_many_institutes(self):
        self.approved("Institute 0", "i0@example.com")
        one = count_queries(lambda: self.client.get(PUBLIC_URL))
        for i in range(1, 9):
            self.approved(f"Institute {i}", f"i{i}@example.com")
        many = count_queries(lambda: self.client.get(PUBLIC_URL))
        self.assertEqual(one, many)

    def test_the_detail_costs_a_constant_number_of_queries(self):
        first = self.approved("Alpha", "alpha@example.com")
        add_location(first, self.municipality)
        self.assertLessEqual(
            count_queries(lambda: self.client.get(f"{PUBLIC_URL}{first.slug}/")), 4
        )

    def test_writes_are_not_allowed(self):
        self.assertEqual(self.client.post(PUBLIC_URL, {}).status_code, 405)


class AdminApiTests(TempMediaMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.super_admin = User.objects.create_superuser("root@example.com", PASSWORD)
        self.reviewer = self.admin_with(["manage_institutes"], "reviewer@example.com")
        self.municipality = make_municipality()
        self.institute, self.owner = make_institute()

    def admin_with(self, permissions, email):
        admin = user_services.create_admin(
            email=email, password=PASSWORD, full_name="Admin", permissions=permissions
        )
        return User.objects.get(pk=admin.pk)  # fresh instance: permissions are cached per object

    def ready(self):
        """Give the institute what approval needs."""
        add_location(self.institute, self.municipality, is_main=True)
        return services.add_document(self.institute, name="License", file=pdf())

    def url(self, action):
        return f"{ADMIN_URL}{self.institute.pk}/{action}/"

    def test_access_matrix(self):
        staff = self.owner
        other_admin = self.admin_with(["manage_enquiries"], "other@example.com")
        cases = (
            (None, 401),
            (staff, 403),
            (other_admin, 403),
            (self.reviewer, 200),
            (self.super_admin, 200),
        )
        for user, expected in cases:
            with self.subTest(user=getattr(user, "email", "anonymous")):
                self.client.force_authenticate(user)
                self.assertEqual(self.client.get(ADMIN_URL).status_code, expected)
        self.client.force_authenticate(None)

    def test_list_shows_owner_and_documents_but_no_file_path(self):
        document = self.ready()
        self.client.force_authenticate(self.reviewer)
        row = self.client.get(ADMIN_URL).data["results"][0]
        self.assertEqual(row["owner_email"], "owner@example.com")
        self.assertEqual(row["documents"][0]["id"], document.pk)
        self.assertNotIn("file", row["documents"][0])
        self.assertNotIn("private_media", str(row))

    def test_list_filter_by_status(self):
        make_institute(name="Beta", email="beta@example.com", status=InstituteStatus.APPROVED)
        self.client.force_authenticate(self.reviewer)
        res = self.client.get(ADMIN_URL, {"status": "APPROVED"})
        self.assertEqual([r["name"] for r in res.data["results"]], ["Beta"])

    def test_the_list_costs_the_same_number_of_queries_for_one_or_many(self):
        self.client.force_authenticate(self.reviewer)
        self.client.get(ADMIN_URL)  # warm-up: the user's permissions are loaded once, then cached
        one = count_queries(lambda: self.client.get(ADMIN_URL))
        for i in range(8):
            make_institute(name=f"Institute {i}", email=f"i{i}@example.com")
        many = count_queries(lambda: self.client.get(ADMIN_URL))
        self.assertEqual(one, many)

    def test_approve(self):
        self.ready()
        self.client.force_authenticate(self.reviewer)
        res = self.client.post(self.url("approve"))
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["status"], InstituteStatus.APPROVED)
        self.assertEqual(res.data["owner_email"], "owner@example.com")

    def test_approve_without_a_document_is_a_400(self):
        add_location(self.institute, self.municipality, is_main=True)
        self.client.force_authenticate(self.reviewer)
        self.assertEqual(self.client.post(self.url("approve")).status_code, 400)

    def test_decisions_that_need_a_reason(self):
        self.client.force_authenticate(self.reviewer)
        for action in ("reject", "request-info"):
            with self.subTest(action=action):
                self.assertEqual(self.client.post(self.url(action)).status_code, 400)
        res = self.client.post(self.url("reject"), {"reason": "Blurry scan"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], InstituteStatus.REJECTED)
        self.assertEqual(res.data["status_reason"], "Blurry scan")

    def test_request_info_suspend_and_reinstate(self):
        self.client.force_authenticate(self.reviewer)
        res = self.client.post(self.url("request-info"), {"reason": "Need the PAN"})
        self.assertEqual(res.data["status"], InstituteStatus.INFO_REQUESTED)
        Institute.objects.filter(pk=self.institute.pk).update(status=InstituteStatus.APPROVED)
        res = self.client.post(self.url("suspend"), {"reason": "Complaint"})
        self.assertEqual(res.data["status"], InstituteStatus.SUSPENDED)
        res = self.client.post(self.url("reinstate"))
        self.assertEqual(res.data["status"], InstituteStatus.APPROVED)

    def test_an_illegal_move_is_a_400(self):
        self.client.force_authenticate(self.reviewer)
        res = self.client.post(self.url("suspend"), {"reason": "Not approved yet"})
        self.assertEqual(res.status_code, 400)

    def test_staff_cannot_review(self):
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.post(self.url("approve")).status_code, 403)

    def test_document_review(self):
        document = self.ready()
        self.client.force_authenticate(self.reviewer)
        url = f"{ADMIN_URL}{self.institute.pk}/documents/{document.pk}/"
        res = self.client.patch(url, {"status": "VERIFIED"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], "VERIFIED")
        self.assertEqual(self.client.patch(url, {"status": "PENDING"}).status_code, 400)

    def test_document_download_streams_the_file(self):
        document = self.ready()
        self.client.force_authenticate(self.reviewer)
        res = self.client.get(f"{ADMIN_URL}{self.institute.pk}/documents/{document.pk}/download/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(b"".join(res.streaming_content), b"%PDF-1.4 test")
        self.assertIn("attachment", res["Content-Disposition"])

    def test_document_of_another_institute_is_a_404(self):
        document = self.ready()
        other, _ = make_institute(name="Other", email="other@example.com")
        self.client.force_authenticate(self.reviewer)
        url = f"{ADMIN_URL}{other.pk}/documents/{document.pk}/download/"
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_staff_cannot_download_through_the_admin_api(self):
        document = self.ready()
        self.client.force_authenticate(self.owner)
        url = f"{ADMIN_URL}{self.institute.pk}/documents/{document.pk}/download/"
        self.assertEqual(self.client.get(url).status_code, 403)
