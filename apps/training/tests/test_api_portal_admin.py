from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.institutes.constants import InstituteStatus, MemberRole
from apps.institutes.models import InstituteMember
from apps.training.constants import TrainingShift, TrainingStatus
from apps.training.models import Training, TrainingContact, TrainingDetail
from apps.training.tests.helpers import (
    PASSWORD,
    TempMediaMixin,
    User,
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
MORNING, DAY, EVENING = TrainingShift.MORNING, TrainingShift.DAY, TrainingShift.EVENING


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
        return f"{PORTAL}{training.slug}/{action + '/' if action else ''}"


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

    def test_portal_slug_lookup_and_numeric_id_404_and_action(self):
        training = make_training(self.institute, status=S.APPROVED)
        # retrieve by slug = 200
        res = self.client.get(f"{PORTAL}{training.slug}/")
        self.assertEqual(res.status_code, 200)
        # retrieve by numeric id = 404
        res_numeric = self.client.get(f"{PORTAL}{training.pk}/")
        self.assertEqual(res_numeric.status_code, 404)
        # one action by slug works
        res_action = self.client.post(f"{PORTAL}{training.slug}/cancel/")
        self.assertEqual(res_action.status_code, 200)


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

    def test_detail_and_contact_are_written_to_their_rows_and_answered_flat(self):
        res = self.create(
            eligibility="Age 18+",
            certification="Certificate",
            contact_person="Ram",
            contact_phone="9800000000",
            contact_email="ram@example.com",
        )
        self.assertEqual(res.status_code, 201, res.data)
        training = Training.objects.get(pk=res.data["id"])
        self.assertEqual(
            (training.detail.overview, training.detail.eligibility, training.detail.skills),
            ("Espresso, milk and latte art", "Age 18+", ["Espresso", "Latte art"]),
        )
        self.assertEqual(
            (training.contact.contact_person, training.contact.contact_phone),
            ("Ram", "9800000000"),
        )
        for name in ("overview", "eligibility", "certification", "skills", "contact_person", "contact_email"):
            self.assertIn(name, res.data)
        self.assertEqual(res.data["skills"], ["Espresso", "Latte art"])
        self.assertEqual(res.data["contact_person"], "Ram")

    def test_a_create_without_them_still_makes_both_rows(self):
        res = self.create(overview="")
        training = Training.objects.get(pk=res.data["id"])
        self.assertEqual(training.contact.contact_person, "")
        self.assertTrue(TrainingDetail.objects.filter(training=training).exists())

    def test_a_bad_phone_or_email_is_400(self):
        for label, overrides in (
            ("phone", dict(contact_phone="not a phone")),
            ("email", dict(contact_email="not an email")),
            ("long skill", dict(skills=["x" * 61])),
        ):
            with self.subTest(label):
                self.assertEqual(self.create(**overrides).status_code, 400)

    def test_a_top_level_category_is_accepted(self):
        res = self.create(category=self.category.parent.slug, sub_category=None)
        self.assertEqual(res.status_code, 201, res.data)

    def test_the_sub_category_is_optional_and_answered_next_to_the_category(self):
        top = self.category.parent
        res = self.create()  # the default body sends a sub-category
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual((res.data["category"], res.data["sub_category"]), (top.slug, self.category.slug))
        self.assertEqual(Training.objects.get(pk=res.data["id"]).category, self.category)  # the leaf is stored
        res = self.create(sub_category=None)
        self.assertEqual((res.data["category"], res.data["sub_category"]), (top.slug, None))
        self.assertEqual(Training.objects.get(pk=res.data["id"]).category, top)
        data = training_payload(self.category)
        del data["sub_category"]  # leaving it out is the same as null
        res = self.client.post(PORTAL, data, format="json")
        self.assertEqual((res.status_code, res.data["sub_category"]), (201, None))

    def test_a_sub_category_must_belong_to_the_category(self):
        stranger = make_category("Barista", parent="Hospitality")
        res = self.create(sub_category=stranger.slug)
        self.assertEqual(res.status_code, 400)
        self.assertIn("sub_category", res.data)

    def test_the_two_category_fields_only_take_their_own_level(self):
        for label, overrides in (
            ("a sub-category as the category", dict(category=self.category.slug, sub_category=None)),
            ("a top-level category as the sub-category", dict(sub_category=self.category.parent.slug)),
        ):
            with self.subTest(label):
                self.assertEqual(self.create(**overrides).status_code, 400)

    def test_shifts_are_cleaned_and_answered(self):
        res = self.create(shifts=[EVENING, MORNING, EVENING])
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["shifts"], [MORNING, EVENING])

    def test_a_draft_may_leave_the_shifts_out(self):
        data = training_payload(self.category)
        del data["shifts"]
        res = self.client.post(PORTAL, data, format="json")
        self.assertEqual((res.status_code, res.data["shifts"]), (201, []))

    def test_an_unknown_shift_is_400(self):
        for shifts in (["Night"], [MORNING, "Night"], MORNING):
            with self.subTest(shifts=shifts):
                self.assertEqual(self.create(shifts=shifts).status_code, 400)

    def test_physical_training_takes_a_municipality_and_an_address(self):
        venue = {
            "location": self.location.location_id,
            "address": "Lakeside, Pokhara",
            "map_url": "https://maps.example/lakeside",
        }
        res = self.create(mode="PHYSICAL", venue=venue)
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["venue"]["location"], self.location.location_id)
        self.assertEqual(res.data["venue"]["address"], "Lakeside, Pokhara")

    def test_online_training_takes_only_an_address_text(self):
        res = self.create(venue={"address": "Zoom, link sent after enrolment"})
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(
            (res.data["venue"]["location"], res.data["venue"]["address"]),
            (None, "Zoom, link sent after enrolment"),
        )

    def test_the_municipality_can_be_anywhere_not_only_the_institutes_own(self):
        elsewhere = make_municipality(9, "Elsewhere")
        res = self.create(mode="PHYSICAL", venue={"location": elsewhere.pk, "address": "Far Road"})
        self.assertEqual(res.status_code, 201, res.data)

    def test_refused(self):
        inactive = make_municipality(3, "M3")
        inactive.is_active = False
        inactive.save()
        district = self.location.location.parent
        retired = make_category("Retired", "Old")
        retired.is_active = False
        retired.save()
        cases = {
            "physical without a municipality": dict(mode="PHYSICAL"),
            "physical without a venue": dict(mode="PHYSICAL", venue=None),
            "online with a municipality": dict(
                venue={"location": self.location.location_id, "address": "Main Road"}
            ),
            "inactive municipality": dict(
                mode="PHYSICAL", venue={"location": inactive.pk, "address": "Main Road"}
            ),
            "a district, not a municipality": dict(
                mode="PHYSICAL", venue={"location": district.pk, "address": "Main Road"}
            ),
            "no address": dict(venue={"address": ""}),
            "inactive category": dict(category=retired.slug),
            "inactive sub-category": dict(sub_category=retired.slug),
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

    def test_patch_replaces_the_venue_and_keeps_it_when_left_out(self):
        training = Training.objects.get(pk=self.create().data["id"])
        res = self.client.patch(self.url(training), {"title": "Renamed"}, format="json")
        self.assertEqual(res.data["venue"]["address"], "Zoom link sent after enrolment")
        venue = {"location": self.location.location_id, "address": "Lakeside"}
        res = self.client.patch(self.url(training), {"mode": "PHYSICAL", "venue": venue}, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["venue"]["location"], self.location.location_id)

    def test_changing_the_mode_needs_the_new_venue(self):
        training = Training.objects.get(pk=self.create().data["id"])
        res = self.client.patch(self.url(training), {"mode": "PHYSICAL"}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("venue", res.data)
        training.refresh_from_db()
        self.assertEqual(training.mode, "ONLINE")

    def test_patch_changes_only_the_fields_it_sends_on_the_detail_and_contact_rows(self):
        training = make_training(
            self.institute, status=S.DRAFT, contact_person="Ram", contact_phone="9800000000"
        )
        res = self.client.patch(self.url(training), {"contact_phone": "9811111111"}, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        contact = TrainingContact.objects.get(training=training)
        self.assertEqual((contact.contact_person, contact.contact_phone), ("Ram", "9811111111"))
        res = self.client.patch(self.url(training), {"skills": ["Go"]}, format="json")
        self.assertEqual((res.data["skills"], res.data["overview"]), (["Go"], "A detailed description"))
        self.assertEqual(res.data["contact_phone"], "9811111111")

    def test_patch_builds_the_rows_for_a_training_that_has_none(self):
        training = Training.objects.create(
            institute=self.institute, category=self.category, title="Bare", mode="ONLINE"
        )
        res = self.client.patch(self.url(training), {"overview": "Now described"}, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(TrainingDetail.objects.get(training=training).overview, "Now described")

    def test_a_skills_edit_is_found_by_search(self):
        training = make_training(self.institute, status=S.DRAFT, skills=["Python"])
        self.client.patch(self.url(training), {"skills": ["Welding"]}, format="json")
        Training.objects.filter(pk=training.pk).update(status=S.APPROVED)  # public to search
        self.assertEqual(self.client.get(PUBLIC, {"search": "weld"}).data["count"], 1)

    def test_patching_the_category_alone_clears_the_sub_category(self):
        training = Training.objects.get(pk=self.create().data["id"])
        top = self.category.parent.slug
        res = self.client.patch(self.url(training), {"category": top}, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual((res.data["category"], res.data["sub_category"]), (top, None))

    def test_patching_the_sub_category_alone_is_checked_against_the_current_category(self):
        training = make_training(self.institute, status=S.DRAFT, category=self.category.parent)
        top = self.category.parent.slug
        res = self.client.patch(self.url(training), {"sub_category": self.category.slug}, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual((res.data["category"], res.data["sub_category"]), (top, self.category.slug))
        stranger = make_category("Barista", parent="Hospitality")
        res = self.client.patch(self.url(training), {"sub_category": stranger.slug}, format="json")
        self.assertEqual(res.status_code, 400)
        res = self.client.patch(self.url(training), {"sub_category": None}, format="json")
        self.assertEqual((res.data["category"], res.data["sub_category"]), (top, None))

    def test_the_category_and_sub_category_can_change_together(self):
        training = Training.objects.get(pk=self.create().data["id"])
        other = make_category("Barista", parent="Hospitality")
        body = {"category": other.parent.slug, "sub_category": other.slug}
        res = self.client.patch(self.url(training), body, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual((res.data["category"], res.data["sub_category"]), (other.parent.slug, other.slug))
        training.refresh_from_db()
        self.assertEqual(training.category, other)

    def test_patch_replaces_the_shifts(self):
        training = make_training(self.institute, status=S.DRAFT)
        res = self.client.patch(self.url(training), {"shifts": [EVENING, DAY]}, format="json")
        self.assertEqual((res.status_code, res.data["shifts"]), (200, [DAY, EVENING]))
        res = self.client.patch(self.url(training), {"title": "Renamed"}, format="json")
        self.assertEqual(res.data["shifts"], [DAY, EVENING])  # left out: kept

    def test_clearing_the_shifts_of_an_approved_training_is_400_and_saves_nothing(self):
        training = make_training(self.institute)
        res = self.client.patch(self.url(training), {"shifts": []}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("shifts", res.data)
        training.refresh_from_db()
        self.assertEqual((training.status, training.shifts), (S.APPROVED, [MORNING]))

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
        training_slug = res.data["slug"]
        portal = f"{PORTAL}{training_slug}/"
        admin = f"{ADMIN}{training_slug}/"

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


class SubmitNeedsShiftsTests(PortalTestCase):
    def test_submit_is_refused_without_shifts_until_they_are_added(self):
        portal = f"{PORTAL}{self.create(shifts=[]).data['slug']}/"
        res = self.client.post(f"{portal}submit/")
        self.assertEqual(res.status_code, 400)
        self.assertIn("shifts", res.data)
        self.client.patch(portal, {"shifts": [DAY]}, format="json")
        self.assertEqual(self.client.post(f"{portal}submit/").data["status"], S.SUBMITTED)

    def test_the_sub_category_is_not_needed_to_submit(self):
        portal = f"{PORTAL}{self.create(sub_category=None).data['slug']}/"
        self.assertEqual(self.client.post(f"{portal}submit/").data["status"], S.SUBMITTED)


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
        data = self.client.get(f"{ADMIN}{self.training.slug}/").data
        self.assertEqual(data["institute"]["status"], InstituteStatus.APPROVED)
        self.assertEqual(data["institute"]["slug"], self.institute.slug)
        self.assertEqual(len(data["sessions"]), 1)
        self.assertEqual(data["overview"], "A detailed description")
        self.assertEqual(data["skills"], ["Python", "Git"])
        self.assertEqual(data["contact_person"], "")
        self.assertEqual(data["shifts"], [MORNING])
        self.assertEqual(data["category"]["id"], self.training.category_id)  # the stored leaf
        self.assertEqual(data["category"]["slug"], self.training.category.slug)
        self.assertEqual(
            data["sub_category"], {
                "id": self.training.category_id,
                "slug": self.training.category.slug,
                "name": self.training.category.name,
            }
        )

    def test_detail_has_no_sub_category_for_a_top_level_category(self):
        top_only = make_training(self.institute, status=S.SUBMITTED, category=make_category().parent)
        self.client.force_authenticate(self.reviewer)
        data = self.client.get(f"{ADMIN}{top_only.slug}/").data
        self.assertIsNone(data["sub_category"])

    def test_review_actions(self):
        self.client.force_authenticate(self.reviewer)
        url = f"{ADMIN}{self.training.slug}/"
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
                self.assertEqual(self.client.post(f"{ADMIN}{training.slug}/approve/").status_code, 400)

    def test_slug_lookup_and_numeric_id_404_and_action(self):
        self.client.force_authenticate(self.reviewer)
        # retrieve by slug = 200
        res = self.client.get(f"{ADMIN}{self.training.slug}/")
        self.assertEqual(res.status_code, 200)
        # retrieve by numeric id = 404
        res_numeric = self.client.get(f"{ADMIN}{self.training.pk}/")
        self.assertEqual(res_numeric.status_code, 404)
        # one action by slug works
        res_action = self.client.post(f"{ADMIN}{self.training.slug}/approve/")
        self.assertEqual(res_action.status_code, 200)


class SummaryTests(PortalTestCase):
    SUMMARY = f"{PORTAL}summary/"

    def test_counts_only_this_institutes_trainings(self):
        for status in (S.DRAFT, S.SUBMITTED, S.APPROVED, S.APPROVED, S.CANCELLED):
            make_training(self.institute, status=status)
        other, _, _ = approved_institute("Beta Institute", "beta@example.com", code=2)
        make_training(other, status=S.APPROVED)
        response = self.client.get(self.SUMMARY)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data, {"total": 5, "active": 2, "pending_review": 1}
        )

    def test_is_one_aggregate_query(self):
        make_training(self.institute)
        self.client.get(self.SUMMARY)  # warm-up: permissions are cached per user
        self.assertEqual(count_queries(lambda: self.client.get(self.SUMMARY)), 1)

    def test_an_institute_without_trainings_gets_zeros(self):
        response = self.client.get(self.SUMMARY)
        self.assertEqual(response.data, {"total": 0, "active": 0, "pending_review": 0})

    def test_anonymous_is_refused(self):
        self.client.force_authenticate(None)
        self.assertIn(self.client.get(self.SUMMARY).status_code, (401, 403))


class ActionQueryCountTests(TempMediaMixin, PortalTestCase):
    """The services lock and re-read the row, so the viewset must not prefetch before them
    (measured: 12 queries per transition or cover upload with a prefetch in get_object, 9 without)."""

    def queries(self, call):
        self.client.get(PORTAL)  # warm-up: permissions are cached per user
        return count_queries(call)

    def test_a_transition_re_reads_the_row_once(self):
        training = make_training(self.institute, status=S.SUBMITTED)
        self.assertLessEqual(
            self.queries(lambda: self.client.post(self.url(training, "withdraw"))), 9
        )

    def test_cover_re_reads_the_row_once(self):
        training = make_training(self.institute, status=S.DRAFT)
        self.assertLessEqual(
            self.queries(
                lambda: self.client.post(
                    self.url(training, "cover"), {"cover_image": png()}, format="multipart"
                )
            ),
            9,
        )


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
