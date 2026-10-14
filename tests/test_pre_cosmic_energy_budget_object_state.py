import unittest
from dataclasses import FrozenInstanceError

from universe.energy_gate import (
    PLANCK_ENERGY_THRESHOLD_J,
)
from universe.pre_cosmic_energy_budget_result_state import (
    PreCosmicEnergyBudgetResult,
)
from universe.pre_cosmic_rules import (
    IDEA_DIMENSIONS,
    describe_pre_cosmic_energy_budget,
)


class PreCosmicEnergyBudgetObjectStateTests(
    unittest.TestCase
):

    def test_budget_is_object_only(self):
        result = (
            describe_pre_cosmic_energy_budget()
        )

        self.assertIsInstance(
            result,
            PreCosmicEnergyBudgetResult,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = result["threshold_j"]

    def test_budget_preserves_values(self):
        result = (
            describe_pre_cosmic_energy_budget()
        )

        self.assertEqual(
            result.idea_dimensions,
            IDEA_DIMENSIONS,
        )
        self.assertEqual(
            result.threshold_j,
            PLANCK_ENERGY_THRESHOLD_J,
        )
        self.assertGreater(
            result.reservoir_before_serving_j,
            result.reservoir_after_first_energy_servings_j,
        )

    def test_budget_is_immutable(self):
        result = (
            describe_pre_cosmic_energy_budget()
        )

        with self.assertRaises(
            FrozenInstanceError
        ):
            result.threshold_j = 0.0

    def test_to_dict_is_explicit_detached_boundary(
        self,
    ):
        result = (
            describe_pre_cosmic_energy_budget()
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot,
            dict,
        )
        self.assertEqual(
            snapshot["threshold_j"],
            result.threshold_j,
        )

        snapshot["threshold_j"] = 0.0

        self.assertEqual(
            result.threshold_j,
            PLANCK_ENERGY_THRESHOLD_J,
        )


if __name__ == "__main__":
    unittest.main()
