from django.test import Client, TestCase
from rest_framework.test import APIClient

from apps.institutes.models import InstituteContact
from apps.institutes.tests.helpers import (
    PASSWORD,
    User,
    count_queries,
    make_institute,
    reset_throttles,
)
from apps.users.constants import Role

LIST_URL = "/admin/institutes/institute/"
CONTACT_URL = "/api/v1/institute/contact/"


def add_contact(institute):
    return InstituteContact.objects.create(
        institute=institute,
        contact_person="Ram",
        contact_phone="9811111111",
        contact_email="ram@example.com",
        telephone_number="014444444",
    )


class InstituteAdminSiteTests(TestCase):
    """The Django admin shows the website an institute typed into its contact form."""

    def setUp(self):
        reset_throttles()
        self.institute, self.owner = make_institute()
        add_contact(self.institute)
        self.admin_client = Client()
        self.admin_client.force_login(
            User.objects.create_user("root@example.com", PASSWORD, role=Role.SUPER_ADMIN)
        )

    def save_website_in_the_portal(self, institute_owner, url):
        api = APIClient()
        api.force_authenticate(institute_owner)
        res = api.patch(CONTACT_URL, {"website": url}, format="json")
        self.assertEqual(res.status_code, 200, res.data)

    def test_a_website_typed_into_the_contact_form_is_listed(self):
        self.save_website_in_the_portal(self.owner, "https://site.example/")
        res = self.admin_client.get(LIST_URL)
        self.assertEqual(res.status_code, 200)
        self.assertIn("https://site.example/", res.content.decode())

    def test_the_edit_page_shows_it_too(self):
        self.save_website_in_the_portal(self.owner, "https://site.example/")
        res = self.admin_client.get(f"{LIST_URL}{self.institute.pk}/change/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("https://site.example/", res.content.decode())

    def test_an_institute_without_a_website_or_contact_still_lists(self):
        make_institute(name="No Contact", email="nocontact@example.com")
        res = self.admin_client.get(LIST_URL)
        self.assertEqual(res.status_code, 200)

    def test_the_list_needs_the_same_queries_for_one_institute_or_many(self):
        one = count_queries(lambda: self.admin_client.get(LIST_URL))
        for i in range(4):
            institute, owner = make_institute(
                name=f"Institute {i}", email=f"o{i}@example.com"
            )
            add_contact(institute)
            self.save_website_in_the_portal(owner, f"https://site{i}.example/")
        many = count_queries(lambda: self.admin_client.get(LIST_URL))
        self.assertEqual(one, many)
