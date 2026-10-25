import unittest

from universe.chemical_objects import ChemicalElement
from universe.cosmic_objects import StellarMaterialCloud
from universe.heavy_element_nucleosynthesis import (
    HeavyElementNucleosynthesis,
)
from universe.heavy_element_nucleosynthesis_process_state import (
    HeavyElementNucleosynthesisProcessState,
)
from universe.stars import Stars
from universe.stellar_nucleosynthesis import (
    StellarNucleosynthesis,
)
from universe.supernova_enrichment import (
    SupernovaEnrichment,
)
from universe.supernova_enrichment_process_state import (
    SupernovaEnrichmentProcessState,
)
from universe.universe import Universe


class HeavyElementsCanonicalStellarLayersTests(
    unittest.TestCase
):

    def _iron(self):
        return ChemicalElement(
            name="iron",
            symbol="Fe",
            atomic_number=26,
            official=True,
            discovered=True,
            state="forged",
            origin="stellar_nucleosynthesis",
        )

    def _prepared_chain(self):
        universe = Universe()

        cloud = StellarMaterialCloud(
            name="primordial_source",
            type="germinal_cloud",
            state="condensing",
            composition={
                "hydrogen": "dominant",
                "helium": "secondary",
            },
            can_form_stars=True,
        )

        stars = Stars(
            universe,
            source_clouds=[cloud],
        )

        stars.form_first_stars()

        nucleosynthesis = StellarNucleosynthesis(
            universe
        )

        nucleosynthesis.forge_elements_up_to_iron()

        supernova = SupernovaEnrichment(
            universe
        )

        result = supernova.enrich_space()

        self.assertIs(
            result.state,
            SupernovaEnrichmentProcessState.ENRICHED,
        )

        return (
            universe,
            stars,
            nucleosynthesis,
            supernova,
        )

    def test_full_canonical_chain_preserves_identity(
        self
    ):
        universe, stars, nuc, supernova = (
            self._prepared_chain()
        )

        process = HeavyElementNucleosynthesis(
            universe
        )

        result = process.forge_heavy_elements()

        self.assertIs(
            result.state,
            HeavyElementNucleosynthesisProcessState.FORGED,
        )

        self.assertIs(
            universe.supernova_enrichment_layer,
            supernova,
        )

        self.assertIs(
            universe.stellar_nucleosynthesis_layer,
            nuc,
        )

        self.assertIs(
            supernova.supernovae[0].source_star,
            stars.stars[0],
        )

        self.assertEqual(
            len(process.heavy_elements),
            11,
        )

        enriched = supernova.enriched_clouds[0]

        for element_name, atomic_number in (
            ("gold", 79),
            ("platinum", 78),
            ("uranium", 92),
        ):
            with self.subTest(element=element_name):
                element = process.heavy_elements[
                    element_name
                ]

                self.assertIsInstance(
                    element,
                    ChemicalElement,
                )

                self.assertEqual(
                    element.atomic_number,
                    atomic_number,
                )

                self.assertIs(
                    enriched.composition[element_name],
                    element,
                )

                self.assertIs(
                    result.heavy_elements[element_name],
                    element,
                )

        self.assertIs(
            enriched.composition["iron"],
            nuc.elements_up_to_iron["iron"],
        )

        self.assertTrue(
            enriched.contains_heavy_elements
        )

        self.assertTrue(
            enriched.can_form_metal_rich_systems
        )

        self.assertTrue(
            process.process_state.enriched_clouds_updated
        )

    def test_public_decoys_cannot_override_sources(
        self
    ):
        universe, _, nuc, supernova = (
            self._prepared_chain()
        )

        universe.world["elements_up_to_iron"] = {
            "iron": object(),
        }

        universe.world["enriched_clouds"] = [
            object(),
        ]

        process = HeavyElementNucleosynthesis(
            universe
        )

        result = process.forge_heavy_elements()

        self.assertIs(
            result.state,
            HeavyElementNucleosynthesisProcessState.FORGED,
        )

        self.assertIs(
            supernova.enriched_clouds[0]
            .composition["gold"],
            process.heavy_elements["gold"],
        )

        self.assertIs(
            universe.world["elements"]["iron"],
            nuc.elements_up_to_iron["iron"],
        )

        self.assertIs(
            universe.world["elements"]["gold"],
            process.heavy_elements["gold"],
        )

    def test_missing_public_aliases_do_not_block(
        self
    ):
        universe, _, nuc, supernova = (
            self._prepared_chain()
        )

        universe.world.pop(
            "elements_up_to_iron",
            None,
        )

        universe.world.pop(
            "enriched_clouds",
            None,
        )

        result = HeavyElementNucleosynthesis(
            universe
        ).forge_heavy_elements()

        self.assertIs(
            result.state,
            HeavyElementNucleosynthesisProcessState.FORGED,
        )

        self.assertIs(
            universe.world["elements"]["iron"],
            nuc.elements_up_to_iron["iron"],
        )

        self.assertIn(
            "gold",
            supernova.enriched_clouds[0].composition,
        )

    def test_world_only_iron_does_not_enable_forging(
        self
    ):
        universe = Universe()

        universe.world["elements_up_to_iron"] = {
            "iron": self._iron(),
        }

        universe.world["enriched_clouds"] = [
            object(),
        ]

        process = HeavyElementNucleosynthesis(
            universe
        )

        result = process.forge_heavy_elements()

        self.assertIs(
            result.state,
            HeavyElementNucleosynthesisProcessState.FAILED,
        )

        self.assertFalse(
            process.process_state.iron_seed_available
        )

        self.assertEqual(
            process.heavy_elements,
            {},
        )

    def test_missing_canonical_clouds_still_fails(
        self
    ):
        universe = Universe()

        nuc = StellarNucleosynthesis(universe)
        nuc.elements_up_to_iron["iron"] = self._iron()

        universe.world["enriched_clouds"] = [
            object(),
        ]

        process = HeavyElementNucleosynthesis(
            universe
        )

        result = process.forge_heavy_elements()

        self.assertIs(
            result.state,
            HeavyElementNucleosynthesisProcessState.FAILED,
        )

        self.assertFalse(
            process.process_state.heavy_elements_forged
        )

        self.assertFalse(
            process.process_state.supernova_enrichment_available
        )

    def test_invalid_canonical_iron_is_rejected(
        self
    ):
        universe = Universe()

        nuc = StellarNucleosynthesis(universe)

        nuc.elements_up_to_iron = {
            "iron": {
                "name": "iron",
                "atomic_number": 26,
            },
        }

        with self.assertRaisesRegex(
            TypeError,
            "ChemicalElement",
        ):
            HeavyElementNucleosynthesis(
                universe
            ).forge_heavy_elements()

    def test_invalid_canonical_cloud_is_rejected(
        self
    ):
        universe = Universe()

        nuc = StellarNucleosynthesis(universe)
        nuc.elements_up_to_iron["iron"] = self._iron()

        supernova = SupernovaEnrichment(universe)

        supernova.enriched_clouds = [
            {"name": "legacy_cloud"},
        ]

        with self.assertRaisesRegex(
            TypeError,
            "StellarMaterialCloud",
        ):
            HeavyElementNucleosynthesis(
                universe
            ).forge_heavy_elements()

    def test_no_public_registry_reads_during_forging(
        self
    ):
        class GuardedWorld(dict):

            def get(self, key, default=None):
                if key in (
                    "elements_up_to_iron",
                    "enriched_clouds",
                ):
                    raise AssertionError(
                        "Heavy elements read public registry"
                    )

                return super().get(key, default)

            def __getitem__(self, key):
                if key in (
                    "elements_up_to_iron",
                    "enriched_clouds",
                ):
                    raise AssertionError(
                        "Heavy elements indexed public registry"
                    )

                return super().__getitem__(key)

        universe, _, nuc, supernova = (
            self._prepared_chain()
        )

        universe.world = GuardedWorld(
            universe.world
        )

        process = HeavyElementNucleosynthesis(
            universe
        )

        result = process.forge_heavy_elements()

        self.assertIs(
            result.state,
            HeavyElementNucleosynthesisProcessState.FORGED,
        )

        self.assertIs(
            universe.world["elements"]["iron"],
            nuc.elements_up_to_iron["iron"],
        )

        self.assertIs(
            supernova.enriched_clouds[0]
            .composition["gold"],
            process.heavy_elements["gold"],
        )


if __name__ == "__main__":
    unittest.main()
