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
            event,
            CatOvulationStimulationRecordedEvent,
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
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = event["stimulation"]

        result["stimulation"] = 99

        self.assertEqual(
            event.stimulation,
            1,
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
            event,
            CatInducedOvulationResolvedEvent,
        )

        self.assertTrue(
            event.ovulation_induced
        )
        self.assertIsNone(
            event.reason
        )

        result[
            "ovulation_induced"
        ] = False

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
