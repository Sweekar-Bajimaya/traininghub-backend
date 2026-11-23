from rest_framework.test import APITestCase

from apps.training.constants import TrainingMode, TrainingStatus
from apps.training.tests.helpers import approved_institute, count_queries, make_training

URL = "/api/v1/institutes/"
S = TrainingStatus
ONLINE, PHYSICAL = TrainingMode.ONLINE, TrainingMode.PHYSICAL


class InstituteTrainingModesTests(APITestCase):
    """`training_modes` on the public institute detail: the modes of the institute's approved
    trainings."""

    def setUp(self):
        self.institute, _, self.location = approved_institute()

    def modes(self, institute=None):
        institute = institute or self.institute
        res = self.client.get(f"{URL}{institute.slug}/")
        self.assertEqual(res.status_code, 200, res.data)
        return res.data["training_modes"]

    def test_an_online_only_institute(self):
        make_training(self.institute)  # online unless it is given a location
        self.assertEqual(self.modes(), [ONLINE])

    def test_a_physical_only_institute(self):
        make_training(self.institute, location=self.location)
        self.assertEqual(self.modes(), [PHYSICAL])

    def test_both_modes_are_listed_once_each_in_alphabetical_order(self):
        make_training(self.institute, title="Online one")
        make_training(self.institute, title="Online two")
        make_training(self.institute, location=self.location, title="Physical one")
        make_training(self.institute, location=self.location, title="Physical two")
        self.assertEqual(self.modes(), [ONLINE, PHYSICAL])

    def test_only_approved_trainings_count(self):
        make_training(self.institute, title="Live")  # online
        for status in S.TRANSITIONS:
            if status == S.APPROVED:
                continue
            make_training(
                self.institute, location=self.location, status=status, title=f"T {status}"
            )  # physical, but never public
        self.assertEqual(self.modes(), [ONLINE])

    def test_an_institute_without_approved_trainings_has_an_empty_list(self):
        self.assertEqual(self.modes(), [])
        make_training(self.institute, status=S.DRAFT)
        self.assertEqual(self.modes(), [])

    def test_another_institutes_modes_do_not_leak(self):
        other, _, other_location = approved_institute("Beta Institute", "beta@example.com", code=2)
        make_training(self.institute, title="Mine")  # online
        make_training(other, location=other_location, title="Theirs")  # physical
        self.assertEqual(self.modes(), [ONLINE])
        self.assertEqual(self.modes(other), [PHYSICAL])

    def test_the_list_does_not_carry_it(self):
        make_training(self.institute)
        self.assertNotIn("training_modes", self.client.get(URL).data["results"][0])

    def test_the_detail_costs_the_same_queries_with_one_or_both_modes(self):
        make_training(self.institute, title="Online")
        detail = f"{URL}{self.institute.slug}/"
        one = count_queries(lambda: self.client.get(detail))
        make_training(self.institute, location=self.location, title="Physical")
        both = count_queries(lambda: self.client.get(detail))
        self.assertEqual(one, both)
        self.assertLessEqual(both, 4)  # the modes come with the institute query
        self.assertEqual(self.client.get(detail).data["training_modes"], [ONLINE, PHYSICAL])
