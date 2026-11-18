from datetime import timedelta

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.institutes import services as institute_services
from apps.institutes.constants import InstituteStatus
from apps.training import services as training_services
from apps.training.constants import TrainingStatus
from apps.training.models import Training
from apps.training.tests.helpers import (
    approved_institute,
    make_admin,
    make_institute,
    make_training,
)

User = get_user_model()
ADMIN_TRAININGS_URL = "/api/v1/admin/trainings/"
PUBLIC_TRAININGS_URL = "/api/v1/trainings/"


class AdminTrainingsFeaturedAndReviewApiTests(APITestCase):
    """`PATCH admin/trainings/{slug}/ {"is_featured": bool}` is the one edit an admin makes to a
    training; the flag also shows and filters on the admin and public lists."""

    def setUp(self):
        super().setUp()
        self.institute, self.owner, self.location = approved_institute()
        self.reviewer = make_admin("reviewer@example.com", permissions=("manage_trainings",))
        self.client.force_authenticate(self.reviewer)

    def url(self, training):
        return f"{ADMIN_TRAININGS_URL}{training.slug}/"

    def set_featured(self, training, value):
        return self.client.patch(self.url(training), {"is_featured": value}, format="json")

    def public_slugs(self, **params):
        """What an anonymous visitor sees on the public list."""
        self.client.force_authenticate(None)
        res = self.client.get(PUBLIC_TRAININGS_URL, params)
        self.client.force_authenticate(self.reviewer)
        self.assertEqual(res.status_code, 200)
        return {row["slug"] for row in res.data["results"]}

    # ==========================================
    # Featuring: PATCH admin/trainings/{slug}/
    # ==========================================

    def test_patch_features_and_unfeatures_an_approved_training_of_an_approved_institute(self):
        training = make_training(self.institute, status=TrainingStatus.APPROVED)

        res = self.set_featured(training, True)
        self.assertEqual(res.status_code, 200, res.data)
        self.assertTrue(res.data["is_featured"])
        self.assertEqual(res.data["title"], training.title)  # the answer is the full admin detail
        training.refresh_from_db()
        self.assertTrue(training.is_featured)

        # the value it already has changes nothing
        self.assertEqual(self.set_featured(training, True).status_code, 200)
        training.refresh_from_db()
        self.assertTrue(training.is_featured)

        res = self.set_featured(training, False)
        self.assertEqual(res.status_code, 200, res.data)
        self.assertFalse(res.data["is_featured"])
        training.refresh_from_db()
        self.assertFalse(training.is_featured)

    def test_featuring_is_refused_unless_the_training_and_its_institute_are_approved(self):
        for number, status in enumerate(
            (
                TrainingStatus.DRAFT,
                TrainingStatus.SUBMITTED,
                TrainingStatus.REJECTED,
                TrainingStatus.UNPUBLISHED,
            )
        ):
            with self.subTest(status=status):
                training = make_training(self.institute, status=status, title=f"Course {number}")
                self.assertEqual(self.set_featured(training, True).status_code, 400)
                training.refresh_from_db()
                self.assertFalse(training.is_featured)

        suspended, _ = make_institute(
            "Suspended Inst", status=InstituteStatus.SUSPENDED, email="susp_tr@example.com"
        )
        training = make_training(suspended, status=TrainingStatus.APPROVED, title="Suspended course")
        self.assertEqual(self.set_featured(training, True).status_code, 400)
        training.refresh_from_db()
        self.assertFalse(training.is_featured)

    def test_unfeaturing_is_always_allowed(self):
        suspended, _ = make_institute(
            "Suspended Inst", status=InstituteStatus.SUSPENDED, email="susp_un@example.com"
        )
        training = make_training(suspended, status=TrainingStatus.APPROVED)
        Training.objects.filter(pk=training.pk).update(is_featured=True)
        res = self.set_featured(training, False)
        self.assertEqual(res.status_code, 200, res.data)
        training.refresh_from_db()
        self.assertFalse(training.is_featured)

    def test_the_body_is_one_required_boolean_and_nothing_else(self):
        training = make_training(self.institute, status=TrainingStatus.APPROVED)
        bad_bodies = (
            {},
            {"is_featured": "not-a-bool"},
            {"is_featured": None},
            {"is_featured": True, "title": "Hijacked"},  # nothing else can be changed here
        )
        for body in bad_bodies:
            with self.subTest(body=body):
                res = self.client.patch(self.url(training), body, format="json")
                self.assertEqual(res.status_code, 400)
        training.refresh_from_db()
        self.assertFalse(training.is_featured)
        self.assertNotEqual(training.title, "Hijacked")

    def test_featuring_needs_manage_trainings(self):
        training = make_training(self.institute, status=TrainingStatus.APPROVED)
        enquiries_only = make_admin("enq@example.com", permissions=("manage_enquiries",))
        cases = ((None, 401), (self.owner, 403), (enquiries_only, 403), (self.reviewer, 200))
        for user, expected in cases:
            with self.subTest(user=getattr(user, "email", "anonymous")):
                self.client.force_authenticate(user)
                self.assertEqual(self.set_featured(training, True).status_code, expected)

    # ==========================================
    # Where the flag shows and filters
    # ==========================================

    def test_admin_list_and_detail_show_and_filter_is_featured(self):
        featured = make_training(self.institute, status=TrainingStatus.APPROVED, title="Featured Python")
        Training.objects.filter(pk=featured.pk).update(is_featured=True)
        normal = make_training(self.institute, status=TrainingStatus.APPROVED, title="Normal Django")

        res = self.client.get(ADMIN_TRAININGS_URL, {"is_featured": "true"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual([r["slug"] for r in res.data["results"]], [featured.slug])
        self.assertTrue(res.data["results"][0]["is_featured"])

        res = self.client.get(ADMIN_TRAININGS_URL, {"is_featured": "false"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual([r["slug"] for r in res.data["results"]], [normal.slug])
        self.assertFalse(res.data["results"][0]["is_featured"])

        self.assertTrue(self.client.get(self.url(featured)).data["is_featured"])
        self.assertFalse(self.client.get(self.url(normal)).data["is_featured"])

    def test_the_public_list_and_detail_show_and_filter_is_featured(self):
        featured = make_training(self.institute, status=TrainingStatus.APPROVED, title="Featured Python")
        Training.objects.filter(pk=featured.pk).update(is_featured=True)
        normal = make_training(self.institute, status=TrainingStatus.APPROVED, title="Normal Django")

        self.assertEqual(self.public_slugs(), {featured.slug, normal.slug})  # no ordering or hiding by the flag
        self.assertEqual(self.public_slugs(is_featured="true"), {featured.slug})
        self.assertEqual(self.public_slugs(is_featured="false"), {normal.slug})

        self.client.force_authenticate(None)
        self.assertTrue(self.client.get(f"{PUBLIC_TRAININGS_URL}{featured.slug}/").data["is_featured"])
        self.assertFalse(self.client.get(f"{PUBLIC_TRAININGS_URL}{normal.slug}/").data["is_featured"])

    # ==========================================
    # When the flag clears
    # ==========================================

    def test_is_featured_is_cleared_when_a_training_leaves_approved(self):
        def featured_approved(title):
            training = make_training(self.institute, status=TrainingStatus.APPROVED, title=title)
            Training.objects.filter(pk=training.pk).update(is_featured=True)
            return training

        # unpublish
        training = featured_approved("Unpublished")
        training_services.unpublish(training, by=self.owner)
        training.refresh_from_db()
        self.assertFalse(training.is_featured)

        # cancel
        training = featured_approved("Cancelled")
        training_services.cancel(training, by=self.owner)
        training.refresh_from_db()
        self.assertFalse(training.is_featured)

        # an edit that sends it back to review
        training = featured_approved("Edited")
        training_services.update_training(training, title="Updated Title")
        training.refresh_from_db()
        self.assertEqual(training.status, TrainingStatus.SUBMITTED)
        self.assertFalse(training.is_featured)

        # expiry
        training = featured_approved("Expired")
        training_services.expire_trainings(today=training.end_date + timedelta(days=1))
        training.refresh_from_db()
        self.assertEqual(training.status, TrainingStatus.EXPIRED)
        self.assertFalse(training.is_featured)

    def test_suspending_the_institute_keeps_the_flag_and_the_public_rule_hides_the_training(self):
        training = make_training(self.institute, status=TrainingStatus.APPROVED)
        Training.objects.filter(pk=training.pk).update(is_featured=True)
        self.assertEqual(self.public_slugs(is_featured="true"), {training.slug})

        institute_services.suspend(self.institute, by=self.reviewer, reason="Late compliance")
        training.refresh_from_db()
        self.assertTrue(training.is_featured)  # not cleared
        self.assertEqual(self.public_slugs(is_featured="true"), set())  # but hidden

        institute_services.reinstate(self.institute, by=self.reviewer)
        self.assertEqual(self.public_slugs(is_featured="true"), {training.slug})  # featured again

    # ==========================================
    # Review
    # ==========================================

    def test_approving_a_training_of_a_suspended_institute_works_but_the_public_rule_hides_it(self):
        # Current behaviour: `training.services.approve` does not look at the institute (only submit,
        # republish and featuring do), and the public listing rule keeps the training hidden until
        # the institute is approved again. Change this test if approval should be refused instead.
        suspended, _ = make_institute(
            "Suspended Inst", status=InstituteStatus.SUSPENDED, email="susp_app@example.com"
        )
        training = make_training(suspended, status=TrainingStatus.SUBMITTED)

        res = self.client.post(f"{self.url(training)}approve/")
        self.assertEqual(res.status_code, 200, res.data)
        training.refresh_from_db()
        self.assertEqual(training.status, TrainingStatus.APPROVED)
        self.assertNotIn(training.slug, self.public_slugs())
