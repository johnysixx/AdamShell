import unittest

from universe.stellar_nucleosynthesis import StellarNucleosynthesis
from universe.stellar_nucleosynthesis_state import (
    StellarNucleosynthesisState,
)
from universe.stars import Stars
from universe.universe import Universe


class StellarNucleosynthesisObjectStateTests(unittest.TestCase):

    def _forged_process(self):
        universe = Universe()
        universe.world["germinal_clouds"] = [
            {"name": "cloud_a", "can_form_stars": True},
        ]

        Stars(universe).form_first_stars()

        process = StellarNucleosynthesis(universe)
        result = process.forge_elements_up_to_iron()

        return universe, process, result

    def test_state_is_object_only(self):
        state = StellarNucleosynthesisState()

        self.assertFalse(hasattr(state, "get"))
        self.assertFalse(hasattr(state, "keys"))

        with self.assertRaises(TypeError):
            _ = state["failed"]

    def test_initial_values_are_preserved(self):
        state = StellarNucleosynthesisState()

        self.assertFalse(state.stellar_fusion_active)
        self.assertFalse(state.elements_up_to_iron_forged)
        self.assertFalse(state.iron_limit_reached)
        self.assertFalse(state.failed)
        self.assertEqual(state.element_count, 0)

    def test_forging_mutates_same_state_object(self):
        _, process, _ = self._forged_process()

        state = process.stellar_nucleosynthesis_state

        self.assertIs(process.stellar_nucleosynthesis_state, state)
        self.assertTrue(state.stellar_fusion_active)
        self.assertTrue(state.elements_up_to_iron_forged)
        self.assertTrue(state.iron_limit_reached)
        self.assertFalse(state.failed)
        self.assertEqual(
            state.element_count,
            len(process.elements_up_to_iron),
        )

    def test_world_stores_state_object(self):
        universe, process, _ = self._forged_process()

        self.assertIs(
            universe.world["stellar_nucleosynthesis_state"],
            process.stellar_nucleosynthesis_state,
        )

    def test_public_result_remains_dict_boundary(self):
        _, _, result = self._forged_process()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["stellar_nucleosynthesis_state"],
            dict,
        )
        self.assertIsInstance(
            result["elements_up_to_iron"],
            dict,
        )
        self.assertTrue(
            result["stellar_nucleosynthesis_state"][
                "elements_up_to_iron_forged"
            ]
        )

    def test_public_result_is_detached(self):
        _, process, result = self._forged_process()

        result["stellar_nucleosynthesis_state"]["element_count"] = 999
        result["elements_up_to_iron"]["iron"]["atomic_number"] = 999

        self.assertEqual(
            process.stellar_nucleosynthesis_state.element_count,
            len(process.elements_up_to_iron),
        )
        self.assertEqual(
            process.elements_up_to_iron["iron"]["atomic_number"],
            26,
        )

    def test_failure_updates_object_state(self):
        universe = Universe()
        process = StellarNucleosynthesis(universe)

        result = process.forge_elements_up_to_iron()

        self.assertTrue(
            process.stellar_nucleosynthesis_state.failed
        )
        self.assertTrue(
            result["stellar_nucleosynthesis_state"]["failed"]
        )

    def test_to_dict_is_detached_boundary(self):
        state = StellarNucleosynthesisState()
        state.element_count = 26

        snapshot = state.to_dict()
        snapshot["element_count"] = 999

        self.assertEqual(state.element_count, 26)


if __name__ == "__main__":
    unittest.main()
