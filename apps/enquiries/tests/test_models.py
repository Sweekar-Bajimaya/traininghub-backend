from django.db import DataError, IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from apps.enquiries.constants import EnquiryStatus
from apps.enquiries.models import Enquiry, EnquiryNote
from apps.enquiries.tests.helpers import (
    PASSWORD,
    User,
    approved_institute,
    make_enquiry,
    make_training,
    next_phone,
)

S = EnquiryStatus


class EnquiryConstraintTests(TestCase):
    def setUp(self):
        self.institute, _, _ = approved_institute()
        self.training = make_training(self.institute)

    def assertRejected(self, **fields):
        # too long for the column is a DataError; every other rule is an IntegrityError
        with self.assertRaises((IntegrityError, DataError)), transaction.atomic():
            make_enquiry(self.training, **fields)

    def test_status_type_and_preferred_time_must_be_known_values(self):
        self.assertRejected(status="WON")
        self.assertRejected(type="QUESTION")
        self.assertRejected(preferred_time="NIGHT")

    def test_preferred_time_may_be_empty(self):
        self.assertEqual(make_enquiry(self.training, preferred_time="").preferred_time, "")

    def test_phone_must_be_a_ten_digit_mobile_number(self):
        for phone in ("984152637", "98415263700", "9541526370", "98415x6370", "+9779841526370"):
            with self.subTest(phone=phone):
                self.assertRejected(phone=phone)

    def test_one_open_enquiry_per_phone_and_training(self):
        phone = next_phone()
        make_enquiry(self.training, phone=phone)
        for status in S.OPEN:  # any open status counts
            with self.subTest(status=status):
                self.assertRejected(phone=phone, status=status)

    def test_closed_enquiries_do_not_block_a_new_one(self):
        phone = next_phone()
        for status in (S.CONVERTED, S.NOT_INTERESTED, S.CLOSED, S.CLOSED):
            make_enquiry(self.training, phone=phone, status=status)
        make_enquiry(self.training, phone=phone)  # and one open one is still fine
        self.assertEqual(Enquiry.objects.filter(phone=phone).count(), 5)

    def test_the_same_phone_may_have_an_open_enquiry_per_training(self):
        phone = next_phone()
        other = make_training(self.institute, title="Other course")
        make_enquiry(self.training, phone=phone)
        make_enquiry(other, phone=phone)

    def test_a_note_cannot_be_blank(self):
        enquiry = make_enquiry(self.training)
        with self.assertRaises(IntegrityError), transaction.atomic():
            EnquiryNote.objects.create(enquiry=enquiry, text="")


class EnquiryRelationTests(TestCase):
    def setUp(self):
        self.institute, self.owner, _ = approved_institute()
        self.training = make_training(self.institute)

    def test_a_training_with_enquiries_cannot_be_deleted(self):
        make_enquiry(self.training)
        with self.assertRaises(ProtectedError):
            self.training.delete()

    def test_deleting_an_author_keeps_the_note(self):
        staff = User.objects.create_user("staff@example.com", PASSWORD, role="INSTITUTE_STAFF")
        note = EnquiryNote.objects.create(
            enquiry=make_enquiry(self.training), author=staff, text="Called"
        )
        staff.delete()
        note.refresh_from_db()
        self.assertIsNone(note.author)

    def test_notes_come_newest_first(self):
        enquiry = make_enquiry(self.training)
        first = EnquiryNote.objects.create(enquiry=enquiry, text="first")
        second = EnquiryNote.objects.create(enquiry=enquiry, text="second")
        self.assertEqual(list(enquiry.notes.all()), [second, first])
