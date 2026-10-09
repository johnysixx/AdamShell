from cats.cat_estrous_phase import CatEstrousPhase
import unittest

from cats import Cats
from cats.mating_contact import (
    CatMatingContact,
    CatMatingContactRecordedEvent,
    CatMatingDeniedResult,
)
from cats.mating_resolver import (
    CatMatingResolver,
)
from universe.universe import Universe


class CatMatingContactObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.start_big_bang()

        self.cats = Cats(
            self.universe
        )

        self.female = (
            self.cats.create_cat(
                name="mother",
                color="black",
                fur_length="short",
                sex="female",
            )
        )

        self.male = (
            self.cats.create_cat(
                name="father",
                color="orange",
                fur_length="long",
                sex="male",
            )
        )

        self.female.reproduction.ovulation_threshold = 1
        self.female.reproduction.estrus_active = True
        self.female.reproduction.estrous_phase = CatEstrousPhase.ESTRUS

        self.resolver = (
            CatMatingResolver(
                self.universe
            )
        )

    def test_contact_and_history_use_object_state(
        self
    ):
        result = (
            self.resolver.mate(
                self.female,
                self.male,
                current_day=10,
            )
        )

        contact = (
            self.female
            .reproduction
            .mating_contacts[-1]
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            contact,
            CatMatingContact,
        )

        self.assertIsInstance(
            result,
            CatMatingContactRecordedEvent,
        )

        self.assertIs(
            result,
            event,
        )

        self.assertIs(
            event.contact,
            contact,
        )

        self.assertEqual(
            event.contact_number,
            1,
        )

        self.assertEqual(
            event.potential_fathers,
            (
                "father",
            ),
        )

    def test_contact_and_event_have_no_mapping_api(
        self
    ):
        self.resolver.mate(
            self.female,
            self.male,
            current_day=10,
        )

        contact = (
            self.female
            .reproduction
            .mating_contacts[-1]
        )

        event = (
            self.resolver
            .history[-1]
        )

        for obj in (
            contact,
            event,
        ):
            for mapping_method in (
                "get",
                "keys",
                "items",
                "values",
            ):
                self.assertFalse(
                    hasattr(
                        obj,
                        mapping_method,
                    )
                )

            with self.assertRaises(
                TypeError
            ):
                _ = obj["name"]

        self.assertFalse(
            hasattr(
                event,
                "to_dict",
            )
        )

    def test_boundaries_are_detached(
        self
    ):
        result = (
            self.resolver.mate(
                self.female,
                self.male,
                current_day=10,
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.female.reproduction.potential_fathers.append(
            "changed"
        )

        snapshot = (
            self.female
            .reproduction
            .to_dict()
        )

        snapshot[
            "mating_contacts"
        ][0][
            "successful"
        ] = False

        self.assertNotIn(
            "changed",
            event.potential_fathers,
        )

        self.assertTrue(
            event.contact.successful
        )

    def test_denied_mating_uses_object_state(
        self
    ):
        self.female.reproduction.estrus_active = False
        self.female.reproduction.estrous_phase = (
            CatEstrousPhase.INTERESTRUS
        )

        result = (
            self.resolver.mate(
                self.female,
                self.male,
            )
        )

        self.assertIsInstance(
            result,
            CatMatingDeniedResult,
        )

        self.assertEqual(
            result.female,
            "mother",
        )

        self.assertEqual(
            result.male,
            "father",
        )

        self.assertEqual(
            result.reason,
            "female_not_in_estrus",
        )

        self.assertFalse(
            result.mating_recorded
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = result[
                "reason"
            ]

        self.assertEqual(
            result.name,
            "cat_mating_denied",
        )

        self.assertFalse(
            result.mating_recorded
        )

    def test_history_rejects_mapping(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            self.resolver._record_history_event(
                {
                    "name": (
                        "cat_mating_contact_recorded"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
