from django.test import SimpleTestCase
from rest_framework import serializers

from apps.common.validators import validate_pan_vat_number, validate_phone_number


class ValidatePhoneNumberTests(SimpleTestCase):
    def test_existing_formats_still_pass_and_are_returned_unchanged(self):
        for value in (
            "9811111111",
            "08256666",
            "014123456",
            "977-9833333333",
            "+977-9833333333",
            "977-08256666",
            9811111111,
        ):
            with self.subTest(value=value):
                self.assertEqual(validate_phone_number(value), value)

    def test_a_landline_with_a_hyphenated_area_code_passes(self):
        for value in (
            "01-4122234",  # Kathmandu
            "061-523456",  # Pokhara
            "056-520123",
        ):
            with self.subTest(value=value):
                self.assertEqual(validate_phone_number(value), value)

    def test_anything_else_is_refused(self):
        for value in (
            "abc",
            "12345",
            "0141234567890123",
            "01-412",  # local number too short
            "01-41222345",  # local number too long
            "1-4122234",  # area code must start with 0
            "0123-4122234",  # area code too long
            "01--4122234",
            "01-41222a4",
            "-4122234",
            "01-",
            "",
        ):
            with self.subTest(value=value):
                with self.assertRaises(serializers.ValidationError):
                    validate_phone_number(value)


class ValidatePanVatNumberTests(SimpleTestCase):
    def test_nine_digits_pass_and_are_returned_unchanged(self):
        for value in ("123456789", "000000001", 123456789):
            with self.subTest(value=value):
                self.assertEqual(validate_pan_vat_number(value), value)

    def test_anything_else_is_refused(self):
        for value in (
            "12345678",  # too short
            "1234567890",  # too long
            "12345678a",
            "123 456 789",
            "123-456-789",
            "123456789\n",  # fullmatch, so a trailing newline does not slip through
            "१२३४५६७८९",  # Devanagari digits: \d would accept them, [0-9] does not
            "",
            None,
        ):
            with self.subTest(value=value):
                with self.assertRaises(serializers.ValidationError):
                    validate_pan_vat_number(value)
