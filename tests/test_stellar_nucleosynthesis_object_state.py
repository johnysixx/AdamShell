import unittest

from universe.chemical_objects import ChemicalElement
from universe.cosmic_objects import StellarMaterialCloud
from universe.stellar_nucleosynthesis import StellarNucleosynthesis
from universe.stellar_nucleosynthesis_state import (
    StellarNucleosynthesisState,
)
from universe.stellar_nucleosynthesis_result_state import (
    StellarNucleosynthesisResult,
)
from universe.stars import Stars
from universe.universe import Universe


class StellarNucleosynthesisObjectStateTests(unittest.TestCase):

    def _forged_process(self):
        universe = Universe()
        source_clouds = [
            StellarMaterialCloud(
                name="cloud_a",
                type="germinal_cloud",
                state="condensing",
                composition={},
                can_form_stars=True,
            ),
        ]

        Stars(
            universe,
            source_clouds=source_clouds,
        ).form_first_stars()

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

        self.assertNotIn(
            "stellar_nucleosynthesis_state",
            universe.world,
        )
        self.assertIs(
            process.result.stellar_nucleosynthesis_state,
            process.stellar_nucleosynthesis_state,
        )

    def test_runtime_result_is_object_and_snapshot_is_dict(
        self
    ):
        _, process, result = self._forged_process()

        self.assertIsInstance(
            result,
            StellarNucleosynthesisResult,
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
            _ = result[
                "stellar_nucleosynthesis_state"
            ]

        self.assertIs(
            result.stellar_nucleosynthesis_state,
            process.stellar_nucleosynthesis_state,
        )
        self.assertIs(
            result.elements_up_to_iron["iron"],
            process.elements_up_to_iron["iron"],
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot[
                "stellar_nucleosynthesis_state"
            ],
            dict,
        )
        self.assertIsInstance(
            snapshot["elements_up_to_iron"],
            dict,
        )
        self.assertTrue(
            snapshot[
                "stellar_nucleosynthesis_state"
            ][
                "elements_up_to_iron_forged"
            ]
        )

    def test_public_result_is_detached(self):
        _, process, result = self._forged_process()

        snapshot = result.to_dict()

        snapshot[
            "stellar_nucleosynthesis_state"
        ]["element_count"] = 999
        snapshot[
            "elements_up_to_iron"
        ]["iron"]["atomic_number"] = 999

        self.assertEqual(
            process.stellar_nucleosynthesis_state.element_count,
            len(process.elements_up_to_iron),
        )
        self.assertEqual(
            process.elements_up_to_iron["iron"].atomic_number,
            26,
        )

    def test_forged_elements_are_chemical_objects(self):
        _, process, result = self._forged_process()

        iron = process.elements_up_to_iron["iron"]

        self.assertIsInstance(iron, ChemicalElement)
        self.assertEqual(
            (iron.symbol, iron.atomic_number),
            ("Fe", 26),
        )
        self.assertEqual(
            iron.origin,
            "stellar_nucleosynthesis",
        )
        self.assertFalse(hasattr(iron, "get"))

        with self.assertRaises(TypeError):
            _ = iron["atomic_number"]

        self.assertIs(
            result.elements_up_to_iron["iron"],
            iron,
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot["elements_up_to_iron"]["iron"],
            dict,
        )

    def test_failure_updates_object_state(self):
        universe = Universe()
        process = StellarNucleosynthesis(universe)

        result = process.forge_elements_up_to_iron()

        self.assertTrue(
            process.stellar_nucleosynthesis_state.failed
        )
        self.assertIsInstance(
            result,
            StellarNucleosynthesisResult,
        )
        self.assertTrue(
            result
            .stellar_nucleosynthesis_state
            .failed
        )

    def test_to_dict_is_detached_boundary(self):
        state = StellarNucleosynthesisState()
        state.element_count = 26

        snapshot = state.to_dict()
        snapshot["element_count"] = 999

        self.assertEqual(state.element_count, 26)


if __name__ == "__main__":
    unittest.main()
