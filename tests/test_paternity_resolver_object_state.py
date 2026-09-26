import unittest

from cats.mating_contact import CatMatingContact
from cats.paternity_resolver import (
    KittenFatherSelectedEvent,
    MultipleSirePaternityResolver,
)


class FakeFather:

    def __init__(
        self,
        name,
    ):
        self.name = name


class FirstChoiceRng:

    def choice(
        self,
        values,
    ):
        return list(values)[0]


class PaternityResolverObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.resolver = (
            MultipleSirePaternityResolver()
        )

        self.first = FakeFather(
            "father_one"
        )
        self.second = FakeFather(
            "father_two"
        )

        self.contacts = [
            CatMatingContact(
                contact_number=1,
                female="mother",
                male="father_one",
                successful=True,
                day=0,
                male_ref=self.first,
            ),
            CatMatingContact(
                contact_number=2,
                female="mother",
                male="father_one",
                successful=True,
                day=0,
                male_ref=self.first,
            ),
            CatMatingContact(
                contact_number=3,
                female="mother",
                male="father_two",
                successful=True,
                day=0,
                male_ref=self.second,
            ),
        ]

    def test_history_uses_object_state(
        self
    ):
        result = (
            self.resolver
            .select_father(
                self.contacts,
                rng=FirstChoiceRng(),
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            KittenFatherSelectedEvent,
        )

        self.assertEqual(
            event.father,
            "father_one",
        )

        self.assertEqual(
            event.successful_contact_count,
            2,
        )

        self.assertEqual(
            event.total_successful_contacts,
            3,
        )

        self.assertEqual(
            event.weighted_candidate_names,
            (
                "father_one",
                "father_one",
                "father_two",
            ),
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = event["father"]

        result[
            "event"
        ][
            "weighted_candidate_names"
        ].append(
            "changed"
        )

        self.assertNotIn(
            "changed",
            event.weighted_candidate_names,
        )

    def test_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(TypeError):
            self.resolver.record_selection(
                {
                    "name": (
                        "kitten_father_selected"
                    ),
                }
            )


    def test_selection_rejects_mapping_contacts(
        self
    ):
        with self.assertRaises(TypeError):
            self.resolver.select_father(
                [
                    {
                        "successful": True,
                    },
                ],
                rng=FirstChoiceRng(),
            )


if __name__ == "__main__":
    unittest.main()
