from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

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
            {"users/admins", "categories", "institutes", "trainings"},
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
