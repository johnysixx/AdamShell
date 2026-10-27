import unittest

from universe.chemical_objects import ChemicalElement
from universe.cosmic_objects import StellarMaterialCloud
from universe.heavy_element_nucleosynthesis import (
    HeavyElementNucleosynthesis,
)
from universe.heavy_element_nucleosynthesis_state import (
    HeavyElementNucleosynthesisState,
)
from universe.heavy_element_nucleosynthesis_result_state import (
    HeavyElementNucleosynthesisResult,
)
from universe.heavy_element_nucleosynthesis_process_state import (
    HeavyElementNucleosynthesisProcessState,
)
from universe.universe import Universe
from universe.stellar_nucleosynthesis import StellarNucleosynthesis
from universe.supernova_enrichment import SupernovaEnrichment


class HeavyElementNucleosynthesisObjectStateTests(unittest.TestCase):

    def _wire_canonical_inputs(
        self, universe, source_elements, source_clouds=None
    ):
        if source_elements is not None:
            nucleosynthesis = StellarNucleosynthesis(
                universe
            )
            nucleosynthesis.elements_up_to_iron = (
                source_elements
            )

        if source_clouds is not None:
            supernova = SupernovaEnrichment(universe)
            supernova.enriched_clouds = (
                source_clouds
            )

    def _forged_process(self):
        universe = Universe()

        source_elements = {
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

        source_clouds = [
            StellarMaterialCloud(
                name="enriched_cloud",
                type="enriched_stellar_cloud",
                state="expanding",
                composition={},
                can_form_stellar_systems=True,
            )
        ]

        self._wire_canonical_inputs(
            universe, source_elements, source_clouds
        )

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

        self.assertNotIn("heavy_element_state", universe.world)
        self.assertIs(
            process.result.process_state,
            process.process_state,
        )

    def test_enrichment_updates_cloud_through_object_api(self):
        universe, _, _ = self._forged_process()
        self.assertNotIn("enriched_clouds", universe.world)
        cloud = universe.supernova_enrichment_layer.enriched_clouds[0]

        self.assertIn("gold", cloud.composition)
        self.assertTrue(cloud.contains_heavy_elements)
        self.assertTrue(cloud.can_form_metal_rich_systems)

    def test_runtime_result_is_object_and_snapshot_is_dict(
        self
    ):
        _, process, result = self._forged_process()

        self.assertIsInstance(
            result,
            HeavyElementNucleosynthesisResult,
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
            _ = result["process_state"]

        self.assertIs(
            result.process_state,
            process.process_state,
        )
        self.assertIs(
            result.heavy_elements["gold"],
            process.heavy_elements["gold"],
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot["process_state"],
            dict,
        )
        self.assertIsInstance(
            snapshot["heavy_elements"],
            dict,
        )
        self.assertTrue(
            snapshot["process_state"][
                "heavy_elements_forged"
            ]
        )

    def test_public_result_is_detached(self):
        _, process, result = self._forged_process()

        snapshot = result.to_dict()

        snapshot[
            "process_state"
        ]["heavy_elements_forged"] = False
        snapshot[
            "heavy_elements"
        ]["gold"]["atomic_number"] = 999

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
            universe.supernova_enrichment_layer.enriched_clouds[0]
            .composition["gold"],
            gold,
        )
        self.assertIs(
            result.heavy_elements["gold"],
            gold,
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot["heavy_elements"]["gold"],
            dict,
        )
        self.assertFalse(hasattr(gold, "get"))

        with self.assertRaises(TypeError):
            _ = gold["atomic_number"]

    def test_rejects_legacy_iron_dict(self):
        universe = Universe()

        source_elements = {
            "iron": {
                "name": "iron",
                "atomic_number": 26,
            }
        }

        source_clouds = [
            StellarMaterialCloud(
                name="enriched_cloud",
                type="enriched_stellar_cloud",
                state="expanding",
                composition={},
                can_form_stellar_systems=True,
            )
        ]

        self._wire_canonical_inputs(
            universe, source_elements, source_clouds
        )

        with self.assertRaises(TypeError):
            HeavyElementNucleosynthesis(
                universe
            ).forge_heavy_elements()

    def test_failure_preserves_object_state(self):
        universe = Universe()
        process = HeavyElementNucleosynthesis(universe)

        result = process.forge_heavy_elements()

        self.assertIs(
            process.state,
            HeavyElementNucleosynthesisProcessState.FAILED,
        )
        self.assertFalse(process.process_state.iron_seed_available)
        self.assertFalse(process.process_state.heavy_elements_forged)
        self.assertIsInstance(
            result,
            HeavyElementNucleosynthesisResult,
        )
        self.assertFalse(
            result.process_state.iron_seed_available
        )

    def test_to_dict_is_detached_boundary(self):
        state = HeavyElementNucleosynthesisState()
        state.heavy_elements_forged = True

        snapshot = state.to_dict()
        snapshot["heavy_elements_forged"] = False

        self.assertTrue(state.heavy_elements_forged)


if __name__ == "__main__":
    unittest.main()
