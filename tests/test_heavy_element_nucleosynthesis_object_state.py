import unittest

from universe.chemical_objects import ChemicalElement
from universe.cosmic_objects import StellarMaterialCloud
from universe.heavy_element_nucleosynthesis import (
    HeavyElementNucleosynthesis,
)
from universe.heavy_element_nucleosynthesis_state import (
    HeavyElementNucleosynthesisState,
)
from universe.universe import Universe


class HeavyElementNucleosynthesisObjectStateTests(unittest.TestCase):

    def _forged_process(self):
        universe = Universe()

        universe.world["elements_up_to_iron"] = {
            "iron": ChemicalElement(
                name="iron",
                symbol="Fe",
                atomic_number=26,
                official=True,
                discovered=True,
                state="forged",
                origin="stellar_nucleosynthesis",
            )
        }

        universe.world["enriched_clouds"] = [
            StellarMaterialCloud(
                name="enriched_cloud",
                type="enriched_stellar_cloud",
                state="expanding",
                composition={},
                can_form_stellar_systems=True,
            )
        ]

        process = HeavyElementNucleosynthesis(universe)
        result = process.forge_heavy_elements()

        return universe, process, result

    def test_state_is_object_only(self):
        state = HeavyElementNucleosynthesisState()

        self.assertFalse(hasattr(state, "get"))
        self.assertFalse(hasattr(state, "keys"))

        with self.assertRaises(TypeError):
            _ = state["heavy_elements_forged"]

    def test_initial_values_are_preserved(self):
        state = HeavyElementNucleosynthesisState()

        self.assertFalse(state.iron_seed_available)
        self.assertFalse(state.supernova_enrichment_available)
        self.assertFalse(state.neutron_capture_possible)
        self.assertFalse(state.heavy_elements_forged)
        self.assertFalse(state.enriched_clouds_updated)

    def test_forging_mutates_same_state_object(self):
        _, process, _ = self._forged_process()

        state = process.process_state

        self.assertIs(process.process_state, state)
        self.assertTrue(state.iron_seed_available)
        self.assertTrue(state.supernova_enrichment_available)
        self.assertTrue(state.neutron_capture_possible)
        self.assertTrue(state.heavy_elements_forged)
        self.assertTrue(state.enriched_clouds_updated)

    def test_world_stores_state_object(self):
        universe, process, _ = self._forged_process()

        self.assertIs(
            universe.world["heavy_element_state"],
            process.process_state,
        )

    def test_enrichment_updates_cloud_through_object_api(self):
        universe, _, _ = self._forged_process()
        cloud = universe.world["enriched_clouds"][0]

        self.assertIn("gold", cloud.composition)
        self.assertTrue(cloud.contains_heavy_elements)
        self.assertTrue(cloud.can_form_metal_rich_systems)

    def test_public_result_remains_dict_boundary(self):
        _, _, result = self._forged_process()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["process_state"],
            dict,
        )
        self.assertIsInstance(
            result["heavy_elements"],
            dict,
        )
        self.assertTrue(
            result["process_state"]["heavy_elements_forged"]
        )

    def test_public_result_is_detached(self):
        _, process, result = self._forged_process()

        result["process_state"]["heavy_elements_forged"] = False
        result["heavy_elements"]["gold"]["atomic_number"] = 999

        self.assertTrue(process.process_state.heavy_elements_forged)
        self.assertEqual(
            process.heavy_elements["gold"].atomic_number,
            79,
        )

    def test_heavy_elements_are_chemical_objects(self):
        universe, process, result = self._forged_process()

        gold = process.heavy_elements["gold"]

        self.assertIsInstance(gold, ChemicalElement)
        self.assertEqual(
            (gold.symbol, gold.atomic_number),
            ("Au", 79),
        )
        self.assertEqual(
            gold.origin,
            "post_iron_nucleosynthesis",
        )
        self.assertEqual(
            gold.requires,
            (
                "iron_seed",
                "supernova_enrichment",
                "neutron_capture",
            ),
        )
        self.assertIs(
            universe.world["heavy_elements"]["gold"],
            gold,
        )
        self.assertIs(
            universe.world["enriched_clouds"][0]
            .composition["gold"],
            gold,
        )
        self.assertIsInstance(
            result["heavy_elements"]["gold"],
            dict,
        )
        self.assertFalse(hasattr(gold, "get"))

        with self.assertRaises(TypeError):
            _ = gold["atomic_number"]

    def test_rejects_legacy_iron_dict(self):
        universe = Universe()

        universe.world["elements_up_to_iron"] = {
            "iron": {
                "name": "iron",
                "atomic_number": 26,
            }
        }

        universe.world["enriched_clouds"] = [
            StellarMaterialCloud(
                name="enriched_cloud",
                type="enriched_stellar_cloud",
                state="expanding",
                composition={},
                can_form_stellar_systems=True,
            )
        ]

        with self.assertRaises(TypeError):
            HeavyElementNucleosynthesis(
                universe
            ).forge_heavy_elements()

    def test_failure_preserves_object_state(self):
        universe = Universe()
        process = HeavyElementNucleosynthesis(universe)

        result = process.forge_heavy_elements()

        self.assertEqual(process.state, "failed")
        self.assertFalse(process.process_state.iron_seed_available)
        self.assertFalse(process.process_state.heavy_elements_forged)
        self.assertEqual(
            result["process_state"]["iron_seed_available"],
            False,
        )

    def test_to_dict_is_detached_boundary(self):
        state = HeavyElementNucleosynthesisState()
        state.heavy_elements_forged = True

        snapshot = state.to_dict()
        snapshot["heavy_elements_forged"] = False

        self.assertTrue(state.heavy_elements_forged)


if __name__ == "__main__":
    unittest.main()
