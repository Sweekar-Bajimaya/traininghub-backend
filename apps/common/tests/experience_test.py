from datetime import date
from unittest import mock

from django.test import SimpleTestCase

from apps.common.utils.helpers import institute_experience


class InstituteExperienceTests(SimpleTestCase):
    def at(self, today, year):
        with mock.patch("apps.common.utils.helpers.timezone.localdate", return_value=today):
            return institute_experience(year)

    def test_cases(self):
        today = date(2026, 11, 2)
        self.assertIsNone(self.at(today, None))
        self.assertIsNone(self.at(today, 2027))  # future
        self.assertEqual(self.at(today, 2026)["text"], "10 months")
        self.assertEqual(self.at(date(2026, 1, 15), 2026)["text"], "1 month")
        self.assertEqual(self.at(today, 2025)["text"], "1 year")
        self.assertEqual(self.at(today, 2020), {"value": 6, "unit": "YEARS", "text": "6 years"})
