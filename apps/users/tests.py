from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.users.constants import Role

User = get_user_model()


class UserConstraintTests(TestCase):
    def test_create_superuser_sets_role(self):
        user = User.objects.create_superuser("root@example.com", "pass12345!")
        self.assertEqual(user.role, Role.SUPER_ADMIN)
        self.assertTrue(user.is_superuser and user.is_staff)
        self.assertTrue(user.is_platform_admin)

    def test_only_one_super_admin(self):
        User.objects.create_superuser("root@example.com", "pass12345!")
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_superuser("root2@example.com", "pass12345!")

    def test_email_is_unique_case_insensitively(self):
        User.objects.create_user("a@example.com", "pass12345!")
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user("A@Example.com", "pass12345!")

    def test_blank_phone_numbers_are_stored_as_null(self):
        first = User.objects.create_user("a@example.com", "pass12345!", phone_number="")
        second = User.objects.create_user("b@example.com", "pass12345!", phone_number="")
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertIsNone(first.phone_number)
        self.assertIsNone(second.phone_number)

    def test_admin_and_staff_roles_are_not_platform_admin_for_staff(self):
        staff = User.objects.create_user("s@example.com", "pass12345!")
        admin = User.objects.create_user("ad@example.com", "pass12345!", role=Role.ADMIN)
        self.assertEqual(staff.role, Role.INSTITUTE_STAFF)
        self.assertFalse(staff.is_platform_admin)
        self.assertTrue(admin.is_platform_admin)

    def test_flags_follow_role(self):
        staff = User.objects.create_user("s@example.com", "pass12345!", is_staff=True, is_superuser=True)
        admin = User.objects.create_user("ad@example.com", "pass12345!", role=Role.ADMIN)
        self.assertFalse(staff.is_staff or staff.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertFalse(admin.is_superuser)

    def test_inconsistent_flags_rejected_by_database(self):
        user = User.objects.create_user("s@example.com", "pass12345!")
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.filter(pk=user.pk).update(is_superuser=True)
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.filter(pk=user.pk).update(is_staff=True)

    def test_email_domain_is_normalized(self):
        user = User.objects.create_user("Name@EXAMPLE.com", "pass12345!")
        self.assertEqual(user.email, "Name@example.com")


from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users import services

PASSWORD = "Str0ng-pass-123!"
ADMIN_PAYLOAD = {
    "email": "new.admin@example.com",
    "full_name": "New Admin",
    "password": PASSWORD,
    "permissions": ["manage_enquiries"],
}


class UsersApiTestCase(APITestCase):
    def setUp(self):
        cache.delete_pattern("throttle_*")  # throttle counters live in Redis; do not flush the django-q broker
        self.super_admin = User.objects.create_superuser("root@example.com", PASSWORD)
        self.admin = services.create_admin(
            email="admin@example.com", password=PASSWORD, full_name="Admin"
        )
        self.staff = User.objects.create_user("staff@example.com", PASSWORD)


class AuthApiTests(UsersApiTestCase):
    def test_login_returns_tokens_and_profile(self):
        res = self.client.post(
            "/api/v1/user/auth/login/", {"email": "staff@example.com", "password": PASSWORD}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)
        self.assertEqual(res.data["user"]["role"], Role.INSTITUTE_STAFF)

    def test_suspended_user_cannot_login(self):
        self.staff.is_active = False
        self.staff.save()
        res = self.client.post(
            "/api/v1/user/auth/login/", {"email": "staff@example.com", "password": PASSWORD}
        )
        self.assertEqual(res.status_code, 401)

    def test_logout_blacklists_refresh_token(self):
        refresh = RefreshToken.for_user(self.staff)
        res = self.client.post("/api/v1/user/auth/logout/", {"refresh": str(refresh)})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=refresh["jti"]).exists())

    def test_me_cannot_change_email_or_role(self):
        self.client.force_authenticate(self.staff)
        res = self.client.patch(
            "/api/v1/user/me/", {"full_name": "Renamed", "role": Role.ADMIN, "email": "x@example.com"}
        )
        self.assertEqual(res.status_code, 200)
        self.staff.refresh_from_db()
        self.assertEqual(self.staff.full_name, "Renamed")
        self.assertEqual(self.staff.role, Role.INSTITUTE_STAFF)
        self.assertEqual(self.staff.email, "staff@example.com")

    def test_password_change_revokes_refresh_tokens(self):
        refresh = RefreshToken.for_user(self.staff)
        self.client.force_authenticate(self.staff)
        res = self.client.put(
            "/api/v1/user/me/password/", {"old_password": PASSWORD, "new_password": "An0ther-pass-456!"}
        )
        self.assertEqual(res.status_code, 200)
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.check_password("An0ther-pass-456!"))
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=refresh["jti"]).exists())

    def test_password_change_rejects_same_password(self):
        self.client.force_authenticate(self.staff)
        res = self.client.put(
            "/api/v1/user/me/password/", {"old_password": PASSWORD, "new_password": PASSWORD}
        )
        self.assertEqual(res.status_code, 400)


class AdminApiTests(UsersApiTestCase):
    url = "/api/v1/user/admins/"

    def test_super_admin_creates_admin_with_forced_role(self):
        self.client.force_authenticate(self.super_admin)
        res = self.client.post(self.url, {**ADMIN_PAYLOAD, "role": Role.SUPER_ADMIN}, format="json")
        self.assertEqual(res.status_code, 201, res.data)
        created = User.objects.get(email=ADMIN_PAYLOAD["email"])
        self.assertEqual(created.role, Role.ADMIN)
        self.assertTrue(created.check_password(PASSWORD))
        self.assertEqual(res.data["permissions"], ["manage_enquiries"])
        self.assertNotIn("password", res.data)

    def test_admin_with_permissions_cannot_manage_admins(self):
        services.update_admin(self.admin, permissions=["manage_account_status", "manage_institutes"])
        self.client.force_authenticate(User.objects.get(pk=self.admin.pk))
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(self.client.post(self.url, ADMIN_PAYLOAD, format="json").status_code, 403)

    def test_staff_cannot_access_admins(self):
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_manage_admins_is_not_grantable(self):
        self.client.force_authenticate(self.super_admin)
        res = self.client.post(
            self.url, {**ADMIN_PAYLOAD, "permissions": ["manage_admins"]}, format="json"
        )
        self.assertEqual(res.status_code, 400)

    def test_duplicate_email_is_case_insensitive_400(self):
        self.client.force_authenticate(self.super_admin)
        res = self.client.post(
            self.url, {**ADMIN_PAYLOAD, "email": "ADMIN@example.com"}, format="json"
        )
        self.assertEqual(res.status_code, 400)

    def test_patch_cannot_change_email_or_password(self):
        self.client.force_authenticate(self.super_admin)
        res = self.client.patch(
            f"{self.url}{self.admin.pk}/",
            {"email": "hacked@example.com", "password": "plaintext", "full_name": "Renamed"},
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.email, "admin@example.com")
        self.assertTrue(self.admin.check_password(PASSWORD))

    def test_patch_updates_name_and_permissions(self):
        self.client.force_authenticate(self.super_admin)
        res = self.client.patch(
            f"{self.url}{self.admin.pk}/",
            {"full_name": "Renamed", "permissions": ["manage_trainings"]},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["permissions"], ["manage_trainings"])

    def test_list_has_constant_query_count(self):
        for i in range(5):
            services.create_admin(
                email=f"a{i}@example.com", password=PASSWORD, full_name="A",
                permissions=["manage_enquiries", "manage_trainings"],
            )
        self.client.force_authenticate(self.super_admin)
        with self.assertNumQueries(3):  # count, admins, permissions prefetch
            res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)


class StatusApiTests(UsersApiTestCase):
    def url(self, user):
        return f"/api/v1/user/users/{user.pk}/status/"

    def test_suspend_blacklists_refresh_tokens(self):
        refresh = RefreshToken.for_user(self.staff)
        self.client.force_authenticate(self.super_admin)
        res = self.client.patch(self.url(self.staff), {"is_active": False})
        self.assertEqual(res.status_code, 200, res.data)
        self.staff.refresh_from_db()
        self.assertFalse(self.staff.is_active)
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=refresh["jti"]).exists())

    def test_cannot_suspend_super_admin_or_self(self):
        services.update_admin(self.admin, permissions=["manage_account_status"])
        actor = User.objects.get(pk=self.admin.pk)
        self.client.force_authenticate(actor)
        self.assertEqual(self.client.patch(self.url(self.super_admin), {"is_active": False}).status_code, 403)
        self.assertEqual(self.client.patch(self.url(actor), {"is_active": False}).status_code, 400)

    def test_admin_with_permission_can_suspend_staff_but_not_admins(self):
        services.update_admin(self.admin, permissions=["manage_account_status"])
        other_admin = services.create_admin(
            email="other@example.com", password=PASSWORD, full_name="Other"
        )
        self.client.force_authenticate(User.objects.get(pk=self.admin.pk))
        self.assertEqual(self.client.patch(self.url(self.staff), {"is_active": False}).status_code, 200)
        self.assertEqual(self.client.patch(self.url(other_admin), {"is_active": False}).status_code, 403)

    def test_admin_without_permission_gets_403(self):
        self.client.force_authenticate(User.objects.get(pk=self.admin.pk))
        self.assertEqual(self.client.patch(self.url(self.staff), {"is_active": False}).status_code, 403)
