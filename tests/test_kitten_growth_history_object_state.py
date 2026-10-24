import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.duplicate_consumption_energy_state import (
    DuplicateConsumptionEnergyState,
)
from cats.kitten_growth import KittenGrowth
from cats.kitten_growth_state import (
    KittenGrowthAlreadyProcessedEvent,
    KittenGrowthAppliedEvent,
)
from meeting_place.cat_bar_lifecycle_state import (
    CatDrankMilkAtBarEvent,
)


class KittenGrowthHistoryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.growth = KittenGrowth(
            self.universe
        )

        self.kitten = self.cats.create_cat(
            name="growth_history_kitten",
            color="white",
            fur_length="short",
            origin="test",
        )

    def test_applied_growth_history_uses_object(
        self
    ):
        result = self.growth.feed_cat_milk(
            kitten=self.kitten,
            day=1,
            amount=1.0,
            source="mother",
        )

        state_event = (
            self.kitten
            .growth
            .history[-1]
        )

        resolver_event = (
            self.growth
            .history[-1]
        )

        self.assertIsInstance(
            result,
            KittenGrowthAppliedEvent,
        )

        self.assertIs(
            result,
            state_event,
        )

        self.assertIs(
            state_event,
            resolver_event,
        )

        self.assertIs(
            self.universe
            .quantum_events[-1],
            state_event,
        )

        self.assertEqual(
            state_event.source,
            "cat_milk",
        )

        self.assertTrue(
            result.grew
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
                    state_event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = state_event["source"]

    def test_growth_metadata_is_read_only_and_bar_event_stays_object_state(
        self
    ):
        result = (
            self.growth
            .feed_cronenberg_portion(
                kitten=self.kitten,
                day=2,
                mass=0.5,
                source="test_portion",
            )
        )

        event = (
            self.growth
            .history[-1]
        )

        self.assertEqual(
            event.metadata[
                "portion_mass"
            ],
            0.5,
        )

        with self.assertRaises(
            TypeError
        ):
            event.metadata[
                "portion_mass"
            ] = 9.0

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        bar_event = (
            CatDrankMilkAtBarEvent(
                cat=self.kitten.name,
                bowl="test_bowl",
                growth=result,
                distribution=None,
            )
        )

        self.assertIs(
            bar_event.growth,
            result,
        )

        self.assertEqual(
            bar_event.growth.metadata[
                "portion_mass"
            ],
            0.5,
        )

        self.assertFalse(
            hasattr(
                bar_event,
                "to_dict",
            )
        )

        with self.assertRaises(
            TypeError
        ):
            bar_event.growth.metadata[
                "portion_mass"
            ] = 9.0

        self.assertEqual(
            event.metadata[
                "portion_mass"
            ],
            0.5,
        )

    def test_duplicate_growth_uses_object_event_and_energy_state(
        self
    ):
        self.growth.feed_cat_milk(
            kitten=self.kitten,
            day=3,
        )

        result = self.growth.feed_cat_milk(
            kitten=self.kitten,
            day=3,
        )

        event = (
            self.growth
            .history[-1]
        )

        self.assertIsInstance(
            result,
            KittenGrowthAlreadyProcessedEvent,
        )

        self.assertIs(
            result,
            event,
        )

        self.assertFalse(
            hasattr(
                event,
                "to_dict",
            )
        )

        self.assertIs(
            self.universe
            .quantum_events[-1],
            event,
        )

        self.assertIsInstance(
            event.stored_energy,
            DuplicateConsumptionEnergyState,
        )

        self.assertIs(
            event.stored_energy,
            self.universe
            .pending_cat_consumption_energy[-1],
        )

        self.assertIs(
            result.stored_energy,
            event.stored_energy,
        )

        self.assertFalse(
            event.grew
        )

        self.assertEqual(
            len(
                self.kitten
                .growth
                .history
            ),
            1,
        )

    def test_growth_histories_reject_mapping_events(
        self
    ):
        state = (
            self.growth
            .ensure_state(
                self.kitten
            )
        )

        with self.assertRaises(TypeError):
            state.record_event(
                {
                    "name":
                        "kitten_growth_applied",
                }
            )

        with self.assertRaises(TypeError):
            self.growth._record(
                {
                    "name":
                        "kitten_growth_applied",
                }
            )


if __name__ == "__main__":
    unittest.main()
