import unittest

from cats import Cats

from cats.mating_pregnancy_event import (
    CatPregnancyAdvancedEvent,
    CatPregnancyStartedEvent,
)

from cats.mating_resolver import (
    CatMatingResolver,
)

from universe.universe import Universe


class FirstChoiceRng:

    def choice(
        self,
        values
    ):
        return list(
            values
        )[0]

    def randint(
        self,
        minimum,
        maximum
    ):
        return minimum

    def random(self):
        return 0.5


class CatPregnancyAdvancedObjectStateTests(
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
        self.female.reproduction.estrous_phase = "estrus"

        self.resolver = (
            CatMatingResolver(
                self.universe
            )
        )

        self.resolver.mate(
            self.female,
            self.male,
            current_day=10,
        )

        self.resolver.close_mating_window(
            self.female,
            current_day=11,
            embryo_count=1,
            gestation_days=63,
            rng=FirstChoiceRng(),
        )

        self.start_event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            self.start_event,
            CatPregnancyStartedEvent,
        )

    def test_history_uses_object_state(
        self
    ):
        result = (
            self.resolver
            .advance_pregnancy(
                self.female,
                days=3,
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            CatPregnancyAdvancedEvent,
        )

        self.assertEqual(
            event.mother,
            "mother",
        )

        self.assertEqual(
            event.days_advanced,
            3,
        )

        self.assertEqual(
            event.pregnancy_day,
            3,
        )

        self.assertEqual(
            event.gestation_days,
            63,
        )

        self.assertFalse(
            event.ready_for_birth
        )

        self.assertTrue(
            event.advanced
        )

        self.assertEqual(
            result,
            event.to_dict(),
        )

    def test_event_has_no_mapping_api(
        self
    ):
        self.resolver.advance_pregnancy(
            self.female,
            days=1,
        )

        event = (
            self.resolver
            .history[-1]
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

        with self.assertRaises(
            TypeError
        ):
            _ = event[
                "pregnancy_day"
            ]

    def test_ready_for_birth_is_derived_from_state(
        self
    ):
        (
            self.female
            .reproduction
            .pregnancy_day
        ) = 62

        result = (
            self.resolver
            .advance_pregnancy(
                self.female,
                days=1,
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertEqual(
            event.pregnancy_day,
            63,
        )

        self.assertTrue(
            event.ready_for_birth
        )

        self.assertTrue(
            result[
                "ready_for_birth"
            ]
        )

    def test_history_keeps_distinct_advance_events(
        self
    ):
        first_result = (
            self.resolver
            .advance_pregnancy(
                self.female,
                days=1,
            )
        )

        first_event = (
            self.resolver
            .history[-1]
        )

        second_result = (
            self.resolver
            .advance_pregnancy(
                self.female,
                days=2,
            )
        )

        second_event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            first_event,
            CatPregnancyAdvancedEvent,
        )

        self.assertIsInstance(
            second_event,
            CatPregnancyAdvancedEvent,
        )

        self.assertIsNot(
            first_event,
            second_event,
        )

        self.assertEqual(
            first_event.pregnancy_day,
            1,
        )

        self.assertEqual(
            second_event.pregnancy_day,
            3,
        )

        self.assertEqual(
            first_result[
                "pregnancy_day"
            ],
            1,
        )

        self.assertEqual(
            second_result[
                "pregnancy_day"
            ],
            3,
        )


if __name__ == "__main__":
    unittest.main()
