from uuid import UUID

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from apps.app_key import services
from apps.app_key.api.v1.permissions import DistributedKeyAuthentication
from apps.app_key.models import DistributedAppKey

User = get_user_model()
FRONTEND = settings.CORS_ALLOWED_ORIGINS[0]


class GuardedView(APIView):
    authentication_classes = []  # the test signs a user in with force_authenticate
    permission_classes = [DistributedKeyAuthentication]

    def get(self, request):
        return Response({"ok": True})


def call(user=None, **headers):
    """GET the guarded view; `headers` are WSGI names, e.g. HTTP_APP_KEY."""
    request = APIRequestFactory().get("/guarded/", **headers)
    if user is not None:
        force_authenticate(request, user=user)
    return GuardedView.as_view()(request)


def reset_keys():
    cache.delete_pattern("app_key_*")  # never cache.clear(): it would wipe the django-q broker


class AppKeyModelTests(TestCase):
    def test_save_makes_a_key_when_none_is_given(self):
        row = DistributedAppKey.objects.create(client_name="Android", remarks="app")
        self.assertEqual(len(str(row.app_key).replace("-", "")), 32)

    def test_save_keeps_a_key_that_was_given(self):
        given = UUID("3f2504e0-4f89-41d3-9a0c-0305e82c3301")
        row = DistributedAppKey.objects.create(client_name="iOS", remarks="app", app_key=given)
        row.refresh_from_db()
        self.assertEqual(row.app_key, given)


class AppKeyPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.row = DistributedAppKey.objects.create(client_name="Android", remarks="app")
        cls.key = UUID(str(cls.row.app_key))

    def setUp(self):
        reset_keys()
        self.addCleanup(reset_keys)

    def test_a_valid_key_is_let_through(self):
        self.assertEqual(call(HTTP_APP_KEY=self.key.hex).status_code, 200)

    def test_dashes_and_letter_case_do_not_matter(self):
        for form in (str(self.key), self.key.hex.upper(), str(self.key).upper()):
            with self.subTest(form=form):
                self.assertEqual(call(HTTP_APP_KEY=form).status_code, 200)

    def test_no_key_junk_and_an_unknown_key_are_refused_with_a_403(self):
        unknown = "3f2504e0-4f89-41d3-9a0c-0305e82c3301"
        for headers in ({}, {"HTTP_APP_KEY": ""}, {"HTTP_APP_KEY": "not-a-uuid"}, {"HTTP_APP_KEY": unknown}):
            with self.subTest(headers=headers):
                response = call(**headers)
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.data["detail"], "A valid App-Key header is required.")

    def test_a_signed_in_user_needs_no_key(self):
        self.assertEqual(call(user=User(email="staff@example.com")).status_code, 200)

    def test_our_frontend_origin_needs_no_key(self):
        self.assertEqual(call(HTTP_ORIGIN=FRONTEND).status_code, 200)

    def test_another_origin_is_refused_without_a_key(self):
        self.assertEqual(call(HTTP_ORIGIN="https://other.example").status_code, 403)

    def test_another_origin_with_a_valid_key_is_let_through(self):
        response = call(HTTP_ORIGIN="https://other.example", HTTP_APP_KEY=self.key.hex)
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True)
    def test_debug_does_not_skip_the_check(self):
        self.assertEqual(call().status_code, 403)

    def test_a_checked_key_is_not_looked_up_again(self):
        call(HTTP_APP_KEY=self.key.hex)
        with self.assertNumQueries(0):
            self.assertEqual(call(HTTP_APP_KEY=self.key.hex).status_code, 200)

    def test_an_unknown_key_is_never_cached(self):
        unknown = "3f2504e0-4f89-41d3-9a0c-0305e82c3301"
        call(HTTP_APP_KEY=unknown)
        self.assertIsNone(cache.get(f"app_key_valid_{UUID(unknown).hex}"))

    def test_deleting_a_key_revokes_it_at_once(self):
        row = DistributedAppKey.objects.create(client_name="iOS", remarks="app")
        header = {"HTTP_APP_KEY": str(row.app_key)}
        self.assertEqual(call(**header).status_code, 200)  # now cached
        row.delete()
        self.assertEqual(call(**header).status_code, 403)

    def test_a_bulk_delete_revokes_keys_too(self):
        row = DistributedAppKey.objects.create(client_name="iOS", remarks="app")
        header = {"HTTP_APP_KEY": str(row.app_key)}
        self.assertEqual(call(**header).status_code, 200)
        DistributedAppKey.objects.filter(pk=row.pk).delete()  # what the admin's bulk action runs
        self.assertEqual(call(**header).status_code, 403)

    def test_services_reject_a_missing_header(self):
        self.assertFalse(services.is_valid_key(None))


class AppKeyCorsTests(TestCase):
    def test_a_browser_preflight_may_send_the_app_key_header(self):
        response = self.client.options(
            "/api/v1/trainings/",
            HTTP_ORIGIN=FRONTEND,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="app-key",
        )
        self.assertIn("app-key", response["Access-Control-Allow-Headers"].lower())


ENFORCED = (
    "/api/v1/enquiries/",
    "/api/v1/institute/register/",
    "/api/v1/institute/register/send-otp/",
    "/api/v1/institute/register/verify-otp/",
)


class EnforcedEndpointTests(TestCase):
    """The public write endpoints that need our frontend's origin or an App-Key. An empty body is
    refused by the serializer with a 400, so "400" here means the permission let the request in."""

    @classmethod
    def setUpTestData(cls):
        cls.key = str(DistributedAppKey.objects.create(client_name="Android", remarks="app").app_key)

    def setUp(self):
        reset_keys()
        cache.delete_pattern("throttle_*")  # the posts below count against the scoped throttles
        self.addCleanup(reset_keys)
        self.addCleanup(cache.delete_pattern, "throttle_*")

    def post_all(self, **headers):
        return {url: self.client.post(url, {}, format="json", **headers).status_code for url in ENFORCED}

    def test_each_is_refused_with_neither_an_origin_nor_a_key(self):
        self.assertEqual(self.post_all(), {url: 403 for url in ENFORCED})

    def test_each_is_refused_from_another_origin(self):
        self.assertEqual(self.post_all(HTTP_ORIGIN="https://other.example"), {url: 403 for url in ENFORCED})

    def test_each_is_refused_with_a_wrong_key(self):
        wrong = "3f2504e0-4f89-41d3-9a0c-0305e82c3301"
        self.assertEqual(self.post_all(HTTP_APP_KEY=wrong), {url: 403 for url in ENFORCED})

    def test_each_accepts_our_frontend_origin(self):
        self.assertEqual(self.post_all(HTTP_ORIGIN=FRONTEND), {url: 400 for url in ENFORCED})

    def test_each_accepts_a_valid_key(self):
        self.assertEqual(self.post_all(HTTP_APP_KEY=self.key), {url: 400 for url in ENFORCED})

    def test_public_reads_stay_open(self):
        for url in ("/api/v1/trainings/", "/api/v1/institutes/", "/api/v1/categories/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_the_other_anonymous_posts_are_not_gated(self):
        for url in ("/api/v1/institute/invitations/accept/", "/api/v1/user/auth/login/"):
            with self.subTest(url=url):
                self.assertNotEqual(self.client.post(url, {}, format="json").status_code, 403)
