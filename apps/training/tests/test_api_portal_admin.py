from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.institutes.constants import InstituteStatus, MemberRole
from apps.institutes.models import InstituteMember
from apps.training.constants import TrainingStatus
from apps.training.models import Training
from apps.training.tests.helpers import (
    PASSWORD,
    TempMediaMixin,
    User,
    add_location,
    approved_institute,
    count_queries,
    make_admin,
    make_category,
    make_municipality,
    make_training,
    png,
    training_payload,
)
from apps.users.constants import Role

PORTAL = "/api/v1/institute/trainings/"
ADMIN = "/api/v1/admin/trainings/"
PUBLIC = "/api/v1/trainings/"
S = TrainingStatus


class PortalTestCase(APITestCase):
    def setUp(self):
        self.institute, self.owner, self.location = approved_institute()
        self.category = make_category()
        self.staff = User.objects.create_user(
            "staff@example.com", PASSWORD, role=Role.INSTITUTE_STAFF
        )
        InstituteMember.objects.create(
            user=self.staff, institute=self.institute, role=MemberRole.STAFF
        )
        self.client.force_authenticate(self.staff)

    def create(self, **overrides):
        data = training_payload(self.category)
        data.update(overrides)
        return self.client.post(PORTAL, data, format="json")

    def url(self, training, action=""):
        return f"{PORTAL}{training.pk}/{action + '/' if action else ''}"


class PortalPermissionTests(PortalTestCase):
    def test_access_matrix(self):
        training = make_training(self.institute, status=S.DRAFT)
        _, other_owner, _ = approved_institute("Beta", "beta@example.com", code=2)
        admin = make_admin("admin@example.com")
        detail_endpoints = (
            ("get", self.url(training)),
            ("patch", self.url(training)),
            ("post", self.url(training, "submit")),
        )
        # another institute's training is a 404, not a 403
        cases = ((None, 401), (admin, 403), (other_owner, 404), (self.staff, 200))
        for user, expected in cases:
            for method, url in detail_endpoints:
                with self.subTest(user=getattr(user, "email", "anonymous"), method=method, url=url):
                    self.client.force_authenticate(user)
                    status = getattr(self.client, method)(url, {}, format="json").status_code
                    self.assertEqual(status, expected)
        self.client.force_authenticate(other_owner)
        self.assertEqual(self.client.get(PORTAL).data["count"], 0)  # only their own trainings


class PortalCreateTests(PortalTestCase):
    def test_create_with_nested_children(self):
        res = self.create(status="APPROVED", slug="hacked", duration_weeks=99)
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["status"], S.DRAFT)
        self.assertNotEqual(res.data["slug"], "hacked")
        self.assertEqual(res.data["duration_weeks"], 6)
        self.assertEqual([m["title"] for m in res.data["modules"]], ["Espresso", "Milk"])
        self.assertEqual(res.data["sessions"][0]["class_days"][0], "SUN")
        self.assertEqual(res.data["outcomes"], [{"text": "Pull a shot"}])

    def test_a_top_level_category_is_accepted(self):
        res = self.create(category=self.category.parent_id)
        self.assertEqual(res.status_code, 201, res.data)

    def test_physical_training_at_own_location(self):
        res = self.create(mode="PHYSICAL", institute_location=self.location.pk)
        self.assertEqual(res.status_code, 201, res.data)

    def test_refused(self):
        _, _, other_location = approved_institute("Beta", "beta@example.com", code=2)
        inactive = add_location(self.institute, make_municipality(3, "M3"), is_active=False)
        retired = make_category("Retired", "Old")
        retired.is_active = False
        retired.save()
        cases = {
            "another institute's location": dict(mode="PHYSICAL", institute_location=other_location.pk),
            "inactive location": dict(mode="PHYSICAL", institute_location=inactive.pk),
            "inactive category": dict(category=retired.pk),
            "unknown day": dict(sessions=[{"class_days": ["XYZ"], "start_time": "07:00", "end_time": "08:00"}]),
            "repeated day": dict(sessions=[{"class_days": ["SUN", "SUN"], "start_time": "07:00", "end_time": "08:00"}]),
            "unknown level": dict(level="ALL_LEVELS"),
            "hours": dict(duration_unit="HOURS"),
        }
        for label, overrides in cases.items():
            with self.subTest(label):
                self.assertEqual(self.create(**overrides).status_code, 400)

    def test_a_pending_institute_cannot_create(self):
        self.institute.status = InstituteStatus.PENDING
        self.institute.save()
        self.assertEqual(self.create().status_code, 400)


class PortalEditTests(PortalTestCase):
    def test_patch_a_draft_keeps_or_replaces_children(self):
        training = Training.objects.get(pk=self.create().data["id"])
        res = self.client.patch(self.url(training), {"title": "Renamed"}, format="json")
        self.assertEqual((res.status_code, res.data["status"]), (200, S.DRAFT))
        self.assertEqual(len(res.data["sessions"]), 1)
        res = self.client.patch(self.url(training), {"modules": []}, format="json")
        self.assertEqual(res.data["modules"], [])

    def test_patch_of_an_approved_training_sends_it_back_to_review(self):
        training = make_training(self.institute)
        res = self.client.patch(self.url(training), {"fee_npr": "999.00"}, format="json")
        self.assertEqual((res.status_code, res.data["status"]), (200, S.SUBMITTED), res.data)
        self.assertEqual(self.client.get(PUBLIC).data["count"], 0)

    def test_an_incomplete_edit_of_an_approved_training_is_400_and_saves_nothing(self):
        training = make_training(self.institute)
        res = self.client.patch(
            self.url(training), {"title": "Changed", "short_description": ""}, format="json"
        )
        self.assertEqual(res.status_code, 400)
        training.refresh_from_db()
        self.assertEqual((training.status, training.title), (S.APPROVED, "Python Bootcamp"))

    def test_some_statuses_cannot_be_edited_and_put_is_not_allowed(self):
        for status in (S.SUBMITTED, S.CANCELLED, S.EXPIRED):
            with self.subTest(status=status):
                training = make_training(self.institute, status=status)
                res = self.client.patch(self.url(training), {"title": "x"}, format="json")
                self.assertEqual(res.status_code, 400)
        self.assertEqual(self.client.put(self.url(training), {}, format="json").status_code, 405)

    def test_delete_only_a_draft(self):
        draft = make_training(self.institute, status=S.DRAFT)
        approved = make_training(self.institute)
        self.assertEqual(self.client.delete(self.url(approved)).status_code, 400)
        self.assertEqual(self.client.delete(self.url(draft)).status_code, 204)


class CoverTests(TempMediaMixin, PortalTestCase):
    def upload(self, training, file):
        return self.client.post(self.url(training, "cover"), {"cover_image": file}, format="multipart")

    def test_upload_while_editable(self):
        training = make_training(self.institute, status=S.DRAFT)
        res = self.upload(training, png())
        self.assertEqual(res.status_code, 200, res.data)
        self.assertTrue(res.data["cover_image"])

    def test_bad_files_are_400(self):
        training = make_training(self.institute, status=S.DRAFT)
        exe = SimpleUploadedFile("a.exe", b"MZ", content_type="application/octet-stream")
        self.assertEqual(self.upload(training, exe).status_code, 400)
        with override_settings(INSTITUTE_UPLOAD_MAX_BYTES=10):
            self.assertEqual(self.upload(training, png()).status_code, 400)

    def test_refused_once_submitted_or_approved(self):
        for status in (S.SUBMITTED, S.APPROVED):
            with self.subTest(status=status):
                training = make_training(self.institute, status=status)
                self.assertEqual(self.upload(training, png()).status_code, 400)


class LifecycleTests(PortalTestCase):
    def test_the_whole_lifecycle(self):
        reviewer = make_admin("reviewer@example.com")
        res = self.create(short_description="")
        training_id = res.data["id"]
        portal = f"{PORTAL}{training_id}/"
        admin = f"{ADMIN}{training_id}/"

        res = self.client.post(f"{portal}submit/")
        self.assertEqual(res.status_code, 400)
        self.assertIn("short_description", res.data)
        self.client.patch(portal, {"short_description": "Coffee basics"}, format="json")
        self.assertEqual(self.client.post(f"{portal}submit/").data["status"], S.SUBMITTED)

        self.client.force_authenticate(reviewer)
        res = self.client.post(f"{admin}request-changes/", {"reason": "Add a photo"}, format="json")
        self.assertEqual(res.data["status"], S.CHANGES_REQUESTED)

        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.get(portal).data["review_feedback"], "Add a photo")
        self.client.patch(portal, {"title": "Barista Course II"}, format="json")
        self.client.post(f"{portal}submit/")

        self.client.force_authenticate(reviewer)
        self.assertEqual(self.client.post(f"{admin}approve/").data["status"], S.APPROVED)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(PUBLIC).data["count"], 1)

        self.client.force_authenticate(self.staff)
        self.client.patch(portal, {"fee_npr": "17000.00"}, format="json")
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(PUBLIC).data["count"], 0)  # hidden until re-approved

        self.client.force_authenticate(reviewer)
        self.client.post(f"{admin}approve/")
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.post(f"{portal}unpublish/").data["status"], S.UNPUBLISHED)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(PUBLIC).data["count"], 0)
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.post(f"{portal}republish/").data["status"], S.APPROVED)
        self.assertEqual(self.client.post(f"{portal}cancel/").data["status"], S.CANCELLED)
        self.assertEqual(self.client.post(f"{portal}republish/").status_code, 400)


class AdminApiTests(APITestCase):
    def setUp(self):
        self.institute, self.owner, _ = approved_institute()
        self.reviewer = make_admin("reviewer@example.com")
        self.training = make_training(self.institute, status=S.SUBMITTED)

    def test_access_matrix(self):
        other_admin = make_admin("other@example.com", permissions=["manage_institutes"])
        for user, expected in ((None, 401), (self.owner, 403), (other_admin, 403), (self.reviewer, 200)):
            with self.subTest(user=getattr(user, "email", "anonymous")):
                self.client.force_authenticate(user)
                self.assertEqual(self.client.get(ADMIN).status_code, expected)

    def test_list_filters_on_status(self):
        make_training(self.institute, status=S.DRAFT, title="Draft")
        self.client.force_authenticate(self.reviewer)
        rows = self.client.get(ADMIN, {"status": S.SUBMITTED}).data["results"]
        self.assertEqual([r["id"] for r in rows], [self.training.pk])
        self.assertEqual(rows[0]["institute_name"], "Alpha Institute")

    def test_detail_shows_the_whole_training(self):
        self.client.force_authenticate(self.reviewer)
        data = self.client.get(f"{ADMIN}{self.training.pk}/").data
        self.assertEqual(data["institute"]["status"], InstituteStatus.APPROVED)
        self.assertEqual(len(data["sessions"]), 1)

    def test_review_actions(self):
        self.client.force_authenticate(self.reviewer)
        url = f"{ADMIN}{self.training.pk}/"
        for action in ("request-changes", "reject"):
            with self.subTest(action=action):
                self.assertEqual(self.client.post(f"{url}{action}/", {}, format="json").status_code, 400)
        res = self.client.post(f"{url}reject/", {"reason": "Duplicate"}, format="json")
        self.assertEqual((res.data["status"], res.data["review_feedback"]), (S.REJECTED, "Duplicate"))

    def test_cannot_approve_a_draft_or_an_unpublished_training(self):
        self.client.force_authenticate(self.reviewer)
        for status in (S.DRAFT, S.UNPUBLISHED):
            with self.subTest(status=status):
                training = make_training(self.institute, status=status)
                self.assertEqual(self.client.post(f"{ADMIN}{training.pk}/approve/").status_code, 400)


class QueryCountTests(PortalTestCase):
    def test_portal_and_admin_lists_are_constant(self):
        reviewer = make_admin("reviewer@example.com")
        make_training(self.institute, location=self.location)
        self.client.force_authenticate(reviewer)
        self.client.get(ADMIN)  # warm-up: permissions are cached per user
        admin_one = count_queries(lambda: self.client.get(ADMIN))
        self.client.force_authenticate(self.staff)
        portal_one = count_queries(lambda: self.client.get(PORTAL))
        for i in range(9):
            make_training(self.institute, title=f"T{i}", location=self.location)
        self.assertEqual(count_queries(lambda: self.client.get(PORTAL)), portal_one)
        self.client.force_authenticate(reviewer)
        self.assertEqual(count_queries(lambda: self.client.get(ADMIN)), admin_one)
