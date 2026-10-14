from django.test import SimpleTestCase
from rest_framework import serializers

from apps.common.validators import validate_pan_vat_number


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
