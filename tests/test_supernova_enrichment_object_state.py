import unittest

from universe.cosmic_objects import StellarMaterialCloud
from universe.heavy_element_nucleosynthesis import (
    HeavyElementNucleosynthesis,
)
from universe.supernova_enrichment import (
    SupernovaEnrichment,
)
from universe.supernova_enrichment_state import (
    SupernovaEnrichmentState,
)
from universe.universe import Universe


class SupernovaEnrichmentObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(value, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def _enriched_process(self):
        universe = Universe()

        universe.world["first_stars"] = [
            {
                "name": "first_star",
                "state": "ignited",
            }
        ]
        universe.world["elements_up_to_iron"] = {
            "hydrogen": {
                "name": "hydrogen",
                "atomic_number": 1,
            },
            "iron": {
                "name": "iron",
                "atomic_number": 26,
            },
        }

        process = SupernovaEnrichment(universe)
        result = process.enrich_space()

        return universe, process, result

    def test_state_is_object_only(self):
        state = SupernovaEnrichmentState()

        self._assert_object_only(
            state,
            "supernova_exploded",
        )

    def test_initial_values_are_preserved(self):
        state = SupernovaEnrichmentState()

        self.assertFalse(state.stars_available)
        self.assertFalse(state.iron_available)
        self.assertFalse(state.supernova_exploded)
        self.assertFalse(state.elements_released)
        self.assertFalse(
            state.enriched_clouds_formed
        )

    def test_enrichment_mutates_same_state_object(
        self
    ):
        universe = Universe()
        universe.world["first_stars"] = [
            {"name": "first_star"}
        ]
        universe.world["elements_up_to_iron"] = {
            "iron": {
                "name": "iron",
                "atomic_number": 26,
            }
        }

        process = SupernovaEnrichment(universe)
        state = process.supernova_enrichment_state

        process.enrich_space()

        self.assertIs(
            process.supernova_enrichment_state,
            state,
        )
        self.assertTrue(state.stars_available)
        self.assertTrue(state.iron_available)
        self.assertTrue(state.supernova_exploded)
        self.assertTrue(state.elements_released)
        self.assertTrue(
            state.enriched_clouds_formed
        )

    def test_world_stores_state_object_and_registries(
        self
    ):
        universe, process, _ = (
            self._enriched_process()
        )

        self.assertIs(
            universe.world[
                "supernova_enrichment_state"
            ],
            process.supernova_enrichment_state,
        )
        self.assertIs(
            universe.world["supernovae"],
            process.supernovae,
        )
        self.assertIs(
            universe.world["enriched_clouds"],
            process.enriched_clouds,
        )
        self.assertIsInstance(
            universe.world["supernovae"],
            list,
        )
        self.assertIsInstance(
            universe.world["enriched_clouds"],
            list,
        )

    def test_enriched_cloud_is_object_only(self):
        _, process, _ = self._enriched_process()

        cloud = process.enriched_clouds[0]

        self.assertIsInstance(cloud, StellarMaterialCloud)
        self._assert_object_only(cloud, "name")
        self.assertEqual(cloud.name, "first_enriched_cloud")
        self.assertTrue(cloud.contains_elements_up_to_iron)
        self.assertTrue(cloud.can_form_stellar_systems)

    def test_public_result_remains_dict_boundary(
        self
    ):
        _, _, result = self._enriched_process()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["supernova_enrichment_state"],
            dict,
        )
        self.assertIsInstance(
            result["supernovae"],
            list,
        )
        self.assertIsInstance(
            result["enriched_clouds"],
            list,
        )
        self.assertTrue(
            result["supernova_enrichment_state"][
                "supernova_exploded"
            ]
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        universe, process, result = (
            self._enriched_process()
        )

        result["supernova_enrichment_state"][
            "supernova_exploded"
        ] = False
        result["supernovae"][0][
            "released_elements"
        ].append("fake_element")
        result["enriched_clouds"][0][
            "composition"
        ]["iron"]["atomic_number"] = 999

        self.assertTrue(
            process
            .supernova_enrichment_state
            .supernova_exploded
        )
        self.assertNotIn(
            "fake_element",
            process.supernovae[0][
                "released_elements"
            ],
        )
        self.assertEqual(
            process.enriched_clouds[0]
            .composition["iron"]["atomic_number"],
            26,
        )
        self.assertEqual(
            universe.world[
                "elements_up_to_iron"
            ]["iron"]["atomic_number"],
            26,
        )

    def test_missing_stars_preserves_initial_state(
        self
    ):
        universe = Universe()
        process = SupernovaEnrichment(universe)

        result = process.enrich_space()

        self.assertEqual(process.state, "failed")
        self.assertFalse(
            process
            .supernova_enrichment_state
            .stars_available
        )
        self.assertFalse(
            result["supernova_enrichment_state"][
                "stars_available"
            ]
        )

    def test_missing_iron_records_available_stars(
        self
    ):
        universe = Universe()
        universe.world["first_stars"] = [
            {"name": "first_star"}
        ]

        process = SupernovaEnrichment(universe)
        result = process.enrich_space()

        state = process.supernova_enrichment_state

        self.assertEqual(process.state, "failed")
        self.assertTrue(state.stars_available)
        self.assertFalse(state.iron_available)
        self.assertTrue(
            result["supernova_enrichment_state"][
                "stars_available"
            ]
        )
        self.assertFalse(
            result["supernova_enrichment_state"][
                "iron_available"
            ]
        )

    def test_downstream_heavy_element_process_works(
        self
    ):
        universe, _, _ = self._enriched_process()

        process = HeavyElementNucleosynthesis(
            universe
        )
        result = process.forge_heavy_elements()

        self.assertEqual(result["state"], "forged")
        self.assertTrue(
            process.process_state.heavy_elements_forged
        )
        self.assertIn(
            "gold",
            universe.world["heavy_elements"],
        )

    def test_enrichment_error_creates_cronenberg(
        self
    ):
        universe = Universe()
        universe.world["first_stars"] = [
            {"name": "first_star"}
        ]
        universe.world["elements_up_to_iron"] = {
            "iron": {
                "name": "iron",
                "atomic_number": 26,
            }
        }

        process = SupernovaEnrichment(universe)

        def broken_history():
            raise RuntimeError(
                "supernova enrichment exploded"
            )

        process.record_history = broken_history

        result = process.enrich_space()
        cronenberg = result["cronenberg"]

        self.assertEqual(
            result["type"],
            "quantum_error",
        )
        self.assertIn(
            cronenberg,
            universe.cronenbergs,
        )
        self.assertEqual(
            cronenberg.origin.source_component,
            "supernova_enrichment",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "enrich_space",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "supernova enrichment exploded",
        )

    def test_to_dict_is_detached_boundary(self):
        state = SupernovaEnrichmentState()
        state.supernova_exploded = True

        snapshot = state.to_dict()
        snapshot["supernova_exploded"] = False

        self.assertTrue(state.supernova_exploded)


if __name__ == "__main__":
    unittest.main()
