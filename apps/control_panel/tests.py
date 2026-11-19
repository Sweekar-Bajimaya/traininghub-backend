from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.common.models.category import Category
from apps.enquiries.constants import EnquiryStatus
from apps.enquiries.models import Enquiry
from apps.enquiries.tests.helpers import (
    approved_institute,
    count_queries,
    make_admin,
    make_category,
    make_enquiry,
    make_training,
)
from apps.institutes.constants import InstituteStatus
from apps.institutes.models import Institute
from apps.institutes.tests.helpers import make_institute
from apps.training.constants import TrainingStatus
from apps.training.models import Training
from apps.users.constants import Role

User = get_user_model()

PASSWORD = "Str0ng-pass-123!"
ROOT = "/api/v1/admin/"


class ControlPanelRoutesTests(APITestCase):
    """The admin endpoints themselves are tested with their own resource (users, common, institutes,
    training); this pins the routing the control panel adds on top."""

    def setUp(self):
        self.client.force_authenticate(
            User.objects.create_superuser("root@example.com", PASSWORD)
        )

    def test_root_lists_every_admin_group(self):
        response = self.client.get(ROOT)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.data),
            {"users/admins", "categories", "institutes", "trainings", "enquiries"},
        )

    def test_admins_live_under_the_control_panel(self):
        payload = {
            "email": "new.admin@example.com",
            "full_name": "New Admin",
            "password": PASSWORD,
            "permissions": ["manage_enquiries"],
        }
        response = self.client.post(f"{ROOT}users/admins/", payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(
            User.objects.get(email=payload["email"]).role, Role.ADMIN
        )
        self.assertEqual(self.client.get(f"{ROOT}users/admins/").status_code, 200)

    def test_the_old_admins_path_is_gone(self):
        self.assertEqual(self.client.get("/api/v1/user/admins/").status_code, 404)


class AdminEnquiryTests(APITestCase):
    """`admin/enquiries/`: a read-only monitor of every institute's enquiries, behind
    `users.manage_enquiries`."""

    URL = ROOT + "enquiries/"
    SUMMARY_URL = URL + "summary/"

    def setUp(self):
        self.institute, _, _ = approved_institute()
        self.training = make_training(self.institute)  # Python, under Technology
        make_enquiry(self.training)
        make_enquiry(self.training, status=EnquiryStatus.CONVERTED)
        self.monitor = make_admin("monitor@example.com", permissions=("manage_enquiries",))
        self.client.force_authenticate(self.monitor)

    def second_institute_enquiry(self, **overrides):
        """An enquiry of another institute, for a training under a top-level category used directly."""
        institute, _, _ = approved_institute("Beta Institute", "beta@example.com", code=2)
        design = Category.objects.create(name="Design")
        training = make_training(institute, category=design, title="Logo design")
        return make_enquiry(training, **overrides)

    def test_access(self):
        reviewer = make_admin("reviewer@example.com")  # manage_trainings only
        root = User.objects.create_superuser("root@example.com", PASSWORD)
        cases = ((None, 401), (reviewer, 403), (self.monitor, 200), (root, 200))
        for url in (self.URL, self.SUMMARY_URL):
            for user, expected in cases:
                with self.subTest(url=url, user=getattr(user, "email", "anonymous")):
                    self.client.force_authenticate(user)
                    self.assertEqual(self.client.get(url).status_code, expected)

    def test_a_row_shows_the_institute_and_the_parent_category(self):
        row = self.client.get(self.URL).data["results"][0]
        self.assertEqual(
            set(row),
            {
                "id", "name", "type", "status", "training_title",
                "institute_name", "category", "created_at",
            },
        )
        self.assertEqual(row["institute_name"], self.institute.name)
        self.assertEqual(row["training_title"], self.training.title)
        self.assertEqual(row["category"], "Technology")

    def test_a_top_level_category_shows_itself(self):
        self.second_institute_enquiry()
        row = next(
            r for r in self.client.get(self.URL).data["results"]
            if r["institute_name"] == "Beta Institute"
        )
        self.assertEqual(row["category"], "Design")

    def test_every_institutes_enquiries_are_listed_newest_first(self):
        newest = self.second_institute_enquiry()
        res = self.client.get(self.URL)
        self.assertEqual(res.data["count"], 3)
        self.assertEqual(res.data["results"][0]["id"], newest.pk)

    def test_nothing_can_be_written(self):
        row = self.client.get(self.URL).data["results"][0]
        for method in (self.client.post, self.client.put, self.client.patch, self.client.delete):
            for url in (self.URL, self.SUMMARY_URL):
                with self.subTest(method=method.__name__, url=url):
                    self.assertEqual(method(url).status_code, 405)
        self.assertEqual(self.client.get(f"{self.URL}{row['id']}/").status_code, 404)

    def test_filter_by_status_and_institute(self):
        self.second_institute_enquiry()
        res = self.client.get(self.URL, {"status": EnquiryStatus.CONVERTED})
        self.assertEqual([r["status"] for r in res.data["results"]], [EnquiryStatus.CONVERTED])
        res = self.client.get(self.URL, {"institute": self.institute.slug})
        self.assertEqual(res.data["count"], 2)
        res = self.client.get(self.URL, {"institute": "no-such-institute"})
        self.assertEqual(res.data["count"], 0)

    def test_filter_by_the_top_level_category(self):
        self.second_institute_enquiry()
        technology = self.training.category.parent.slug  # the training sits in its sub-category
        res = self.client.get(self.URL, {"category": technology})
        self.assertEqual(res.status_code, 200)
        self.assertEqual({r["category"] for r in res.data["results"]}, {"Technology"})
        self.assertEqual(res.data["count"], 2)
        res = self.client.get(self.URL, {"category": Category.objects.get(name="Design").slug})
        self.assertEqual([r["category"] for r in res.data["results"]], ["Design"])

    def test_search_matches_the_visitor_the_training_and_the_institute(self):
        self.second_institute_enquiry(name="Sita Rai")
        for term, expected in (("sita", 1), ("logo", 1), ("beta", 1), ("python", 2), ("zzz", 0)):
            with self.subTest(term=term):
                res = self.client.get(self.URL, {"search": term})
                self.assertEqual(res.data["count"], expected)

    def test_summary_counts_total_and_converted(self):
        self.assertEqual(self.client.get(self.SUMMARY_URL).data, {"total": 2, "converted": 1})
        self.second_institute_enquiry(status=EnquiryStatus.CONVERTED)
        self.assertEqual(self.client.get(self.SUMMARY_URL).data, {"total": 3, "converted": 2})

    def test_summary_follows_the_filters(self):
        self.second_institute_enquiry(status=EnquiryStatus.CONVERTED)
        res = self.client.get(self.SUMMARY_URL, {"institute": self.institute.slug})
        self.assertEqual(res.data, {"total": 2, "converted": 1})
        res = self.client.get(self.SUMMARY_URL, {"institute": "no-such-institute"})
        self.assertEqual(res.data, {"total": 0, "converted": 0})

    def test_the_list_query_count_does_not_grow_with_the_rows(self):
        self.client.get(self.URL)  # warm-up: the admin's permissions are cached on the user after it
        before = count_queries(lambda: self.client.get(self.URL))
        for _ in range(5):
            make_enquiry(self.training)
        self.assertEqual(count_queries(lambda: self.client.get(self.URL)), before)


class AdminDashboardSummaryTests(APITestCase):
    """`admin/dashboard/summary/`: the dashboard's cards in one call, a section per permission."""

    URL = ROOT + "dashboard/summary/"

    def setUp(self):
        # institutes: 5 in all, 1 PENDING (INFO_REQUESTED waits for the owner, so it is not counted), 2 APPROVED
        self.institute, _, _ = approved_institute()
        for number, status in enumerate(
            (
                InstituteStatus.APPROVED,
                InstituteStatus.PENDING,
                InstituteStatus.INFO_REQUESTED,
                InstituteStatus.REJECTED,
            )
        ):
            make_institute(f"Institute {number}", status, f"owner{number}@example.com")
        # trainings: 9 rows, the DRAFT is left out of the total (8); CHANGES_REQUESTED is not "rejected"
        self.category = make_category()
        self.trainings = {}
        for number, status in enumerate(
            (
                TrainingStatus.DRAFT,
                TrainingStatus.SUBMITTED,
                TrainingStatus.SUBMITTED,
                TrainingStatus.APPROVED,
                TrainingStatus.APPROVED,
                TrainingStatus.APPROVED,
                TrainingStatus.REJECTED,
                TrainingStatus.CHANGES_REQUESTED,
                TrainingStatus.UNPUBLISHED,
            )
        ):
            self.trainings[number] = make_training(
                self.institute, category=self.category, status=status, title=f"Course {number}"
            )
        # enquiries: 4 in all, 2 NEW, 1 CONVERTED
        training = self.trainings[3]
        make_enquiry(training)
        make_enquiry(training)
        make_enquiry(training, status=EnquiryStatus.CONTACTED)
        make_enquiry(training, status=EnquiryStatus.CONVERTED)
        self.root = User.objects.create_superuser("root@example.com", PASSWORD)
        self.client.force_authenticate(self.root)

    def test_every_section_for_a_super_admin(self):
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.data,
            {
                "institutes": {"total": 5, "pending": 1, "approved": 2},
                "trainings": {"total": 8, "pending_review": 2, "approved": 3, "rejected": 1},
                "enquiries": {"total": 4, "new": 2, "converted": 1},
            },
        )

    def test_an_empty_platform_reads_zero(self):
        Enquiry.objects.all().delete()
        Training.objects.all().delete()
        Institute.objects.all().delete()
        self.assertEqual(
            self.client.get(self.URL).data,
            {
                "institutes": {"total": 0, "pending": 0, "approved": 0},
                "trainings": {"total": 0, "pending_review": 0, "approved": 0, "rejected": 0},
                "enquiries": {"total": 0, "new": 0, "converted": 0},
            },
        )

    def test_access(self):
        owner = make_institute("Gamma", InstituteStatus.APPROVED, "gamma@example.com")[1]
        no_rights = make_admin("none@example.com", permissions=())
        cases = ((None, 401), (owner, 403), (no_rights, 403), (self.root, 200))
        for user, expected in cases:
            with self.subTest(user=getattr(user, "email", "anonymous")):
                self.client.force_authenticate(user)
                self.assertEqual(self.client.get(self.URL).status_code, expected)

    def test_a_section_needs_its_own_permission(self):
        cases = (
            (("manage_institutes",), {"institutes"}),
            (("manage_trainings",), {"trainings"}),
            (("manage_enquiries",), {"enquiries"}),
            (("manage_institutes", "manage_enquiries"), {"institutes", "enquiries"}),
        )
        for permissions, expected in cases:
            with self.subTest(permissions=permissions):
                admin = make_admin("admin@example.com", permissions=permissions)
                self.client.force_authenticate(admin)
                res = self.client.get(self.URL)
                self.assertEqual(res.status_code, 200)
                self.assertEqual(set(res.data), expected)
                admin.delete()

    def test_the_counts_ignore_filters(self):
        res = self.client.get(self.URL, {"status": "APPROVED", "institute": self.institute.slug})
        self.assertEqual(res.data["enquiries"]["total"], 4)
        self.assertEqual(res.data["institutes"]["total"], 5)

    def test_nothing_can_be_written(self):
        for method in (self.client.post, self.client.put, self.client.patch, self.client.delete):
            with self.subTest(method=method.__name__):
                self.assertEqual(method(self.URL).status_code, 405)

    def test_three_queries_however_many_rows(self):
        self.assertEqual(count_queries(lambda: self.client.get(self.URL)), 3)
        for _ in range(5):
            make_enquiry(self.trainings[3])
        self.assertEqual(count_queries(lambda: self.client.get(self.URL)), 3)
