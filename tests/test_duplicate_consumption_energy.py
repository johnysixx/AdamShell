import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.kitten_growth import KittenGrowth
from cats.duplicate_consumption_energy import (
    DuplicateConsumptionEnergy
)


class DuplicateConsumptionEnergyTests(
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

        self.energy = (
            DuplicateConsumptionEnergy(
                self.universe
            )
        )

        self.kitten = self.cats.create_cat(
            name="kitten",
            color="white",
            fur_length="short",
            origin="test"
        )

    def create_cronenberg(
        self
    ):
        return (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "Test Cronenberg."
                ),
                source_component="test",
                source_operation=(
                    "duplicate_consumption"
                )
            )
        )

    def test_second_milk_is_stored_as_energy(
        self
    ):
        first = self.growth.feed_cat_milk(
            kitten=self.kitten,
            day=1,
            amount=1.0
        )

        second = self.growth.feed_cat_milk(
            kitten=self.kitten,
            day=1,
            amount=1.0
        )

        self.assertTrue(
            first["grew"]
        )

        self.assertFalse(
            second["grew"]
        )

        self.assertTrue(
            second["energy_conserved"]
        )

        self.assertEqual(
            len(
                self.universe
                .pending_cat_consumption_energy
            ),
            1
        )

    def test_lower_half_creates_cronenberg(
        self
    ):
        self.growth.feed_cat_milk(
            self.kitten,
            day=1
        )

        self.growth.feed_cat_milk(
            self.kitten,
            day=1
        )

        before = len(
            self.universe.cronenbergs
        )

        result = self.energy.resolve_next(
            cat_d20_value=7
        )

        self.assertEqual(
            result["resolution"],
            "cronenberg_manifested"
        )

        self.assertEqual(
            len(
                self.universe.cronenbergs
            ),
            before + 1
        )

    def test_upper_half_creates_quantum_twin(
        self
    ):
        original = self.create_cronenberg()

        self.growth.feed_cat_milk(
            self.kitten,
            day=1
        )

        self.growth.feed_cat_milk(
            self.kitten,
            day=1
        )

        result = self.energy.resolve_next(
            cat_d20_value=16
        )

        self.assertEqual(
            result["resolution"],
            (
                "cronenberg_quantum_"
                "counterpart_created"
            )
        )

        self.assertEqual(
            result[
                "original_cronenberg_id"
            ],
            original.id
        )

        self.assertIsNotNone(
            original.quantum_state[
                "counterpart_id"
            ]
        )

    def test_missing_twin_target_falls_back(
        self
    ):
        self.growth.feed_cat_milk(
            self.kitten,
            day=1
        )

        self.growth.feed_cat_milk(
            self.kitten,
            day=1
        )

        result = self.energy.resolve_next(
            cat_d20_value=20
        )

        self.assertEqual(
            result["resolution"],
            "cronenberg_manifested"
        )

        self.assertEqual(
            result["fallback_reason"],
            (
                "quantum_twin_target_"
                "unavailable"
            )
        )

    def test_one_resolution_consumes_one_item(
        self
    ):
        self.growth.feed_cat_milk(
            self.kitten,
            day=1
        )

        self.growth.feed_cat_milk(
            self.kitten,
            day=1
        )

        self.growth.feed_cat_milk(
            self.kitten,
            day=1
        )

        self.assertEqual(
            len(
                self.universe
                .pending_cat_consumption_energy
            ),
            2
        )

        self.energy.resolve_next(
            cat_d20_value=1
        )

        pending = [
            item
            for item
            in self.universe
            .pending_cat_consumption_energy
            if not item["resolved"]
        ]

        self.assertEqual(
            len(pending),
            1
        )


if __name__ == "__main__":
    unittest.main()