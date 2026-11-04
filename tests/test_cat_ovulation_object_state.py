import unittest

from universe.universe import Universe
from cats import Cats
from cats.ovulation_resolver import (
    CatInducedOvulationResolvedEvent,
    CatOvulationResolver,
    CatOvulationStimulationRecordedEvent,
)


class CatOvulationObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.start_big_bang()

        self.cats = Cats(
            self.universe
        )

        self.female = self.cats.create_cat(
            name="female",
            color="black",
            fur_length="short",
            sex="female",
        )

        self.resolver = CatOvulationResolver(
            self.universe
        )

    def test_stimulation_history_uses_object_state(
        self
    ):
        result = (
            self.resolver
            .record_stimulation(
                self.female,
                amount=1,
                day=4,
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            result,
            CatOvulationStimulationRecordedEvent,
        )

        self.assertIs(
            result,
            event,
        )

        self.assertEqual(
            event.stimulation,
            1,
        )
        self.assertEqual(
            event.day,
            4,
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
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = event["stimulation"]

        with self.assertRaises(TypeError):
            _ = result[
                "stimulation"
            ]

        self.assertEqual(
            result.stimulation,
            1,
        )

        self.assertEqual(
            result.threshold_reached,
            False,
        )

    def test_stimulation_records_canonical_male(self):
        male = self.cats.create_cat(
            name="ovulation_male",
            color="white",
            fur_length="short",
            sex="male",
        )

        result = self.resolver.record_stimulation(
            self.female,
            male=male,
            amount=1,
            day=4,
        )

        self.assertEqual(result.male, male.name)
        self.assertIs(self.resolver.history[-1], result)

    def test_mapping_male_is_rejected_atomically(self):
        before_stimulation = (
            self.female.reproduction.ovulation_stimulation
        )
        before_history = tuple(self.resolver.history)

        with self.assertRaisesRegex(TypeError, "Cat or None"):
            self.resolver.record_stimulation(
                self.female,
                male={"name": "legacy_male"},
                amount=1,
                day=4,
            )

        self.assertEqual(
            self.female.reproduction.ovulation_stimulation,
            before_stimulation,
        )
        self.assertEqual(
            tuple(self.resolver.history),
            before_history,
        )

    def test_resolution_history_uses_object_state(
        self
    ):
        (
            self.female
            .reproduction
            .ovulation_threshold
        ) = 1

        self.resolver.record_stimulation(
            self.female,
            amount=1,
            day=4,
        )

        result = self.resolver.resolve(
            self.female,
            day=5,
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            result,
            CatInducedOvulationResolvedEvent,
        )

        self.assertIs(
            result,
            event,
        )

        self.assertTrue(
            event.ovulation_induced
        )
        self.assertIsNone(
            event.reason
        )

        with self.assertRaises(TypeError):
            _ = result[
                "ovulation_induced"
            ]

        self.assertFalse(
            hasattr(
                event,
                "to_dict",
            )
        )

        self.assertTrue(
            event.ovulation_induced
        )

        with self.assertRaises(TypeError):
            _ = event["reason"]

    def test_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(TypeError):
            self.resolver.record_event(
                {
                    "name": (
                        "cat_ovulation_stimulation_recorded"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
