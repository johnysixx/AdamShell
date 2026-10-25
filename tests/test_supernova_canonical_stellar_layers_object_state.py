import unittest

from universe.chemical_objects import ChemicalElement
from universe.cosmic_objects import StellarMaterialCloud
from universe.stars import Stars
from universe.stars_process_state import StarsProcessState
from universe.stellar_nucleosynthesis import (
    StellarNucleosynthesis,
)
from universe.stellar_nucleosynthesis_process_state import (
    StellarNucleosynthesisProcessState,
)
from universe.supernova_enrichment import SupernovaEnrichment
from universe.supernova_enrichment_process_state import (
    SupernovaEnrichmentProcessState,
)
from universe.universe import Universe


class SupernovaCanonicalStellarLayersTests(
    unittest.TestCase
):

    def _formed_stars(self):
        universe = Universe()

        cloud = StellarMaterialCloud(
            name="canonical_cloud",
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

        result = stars.form_first_stars()

        self.assertIs(
            result.state,
            StarsProcessState.FORMED,
        )

        return universe, stars

    def _forged_layers(self):
        universe, stars = self._formed_stars()

        nucleosynthesis = StellarNucleosynthesis(
            universe
        )

        result = nucleosynthesis.forge_elements_up_to_iron()

        self.assertIs(
            result.state,
            StellarNucleosynthesisProcessState.FORGED,
        )

        return universe, stars, nucleosynthesis

    def test_nucleosynthesis_registers_canonical_layer(
        self
    ):
        universe = Universe()

        self.assertFalse(
            hasattr(
                universe,
                "stellar_nucleosynthesis_layer",
            )
        )

        layer = StellarNucleosynthesis(universe)

        self.assertIs(
            universe.stellar_nucleosynthesis_layer,
            layer,
        )

        self.assertEqual(
            layer.elements_up_to_iron,
            {},
        )

    def test_supernova_uses_canonical_star_and_iron(
        self
    ):
        universe, stars, nuc = self._forged_layers()

        result = SupernovaEnrichment(
            universe
        ).enrich_space()

        self.assertIs(
            result.state,
            SupernovaEnrichmentProcessState.ENRICHED,
        )

        self.assertEqual(
            len(result.supernovae),
            1,
        )

        self.assertEqual(
            len(result.enriched_clouds),
            1,
        )

        self.assertIs(
            result.supernovae[0].source_star,
            stars.stars[0],
        )

        iron = nuc.elements_up_to_iron["iron"]

        self.assertIsInstance(
            iron,
            ChemicalElement,
        )

        self.assertIs(
            result.enriched_clouds[0]
            .composition["iron"],
            iron,
        )

        self.assertEqual(
            iron.atomic_number,
            26,
        )

        self.assertIn(
            "iron",
            result.supernovae[0].released_elements,
        )

    def test_public_decoys_cannot_override_layers(
        self
    ):
        universe, stars, nuc = self._forged_layers()

        universe.world["first_stars"] = [
            {"name": "legacy_star"},
        ]

        universe.world["elements_up_to_iron"] = {
            "iron": object(),
        }

        result = SupernovaEnrichment(
            universe
        ).enrich_space()

        self.assertIs(
            result.state,
            SupernovaEnrichmentProcessState.ENRICHED,
        )

        self.assertIs(
            result.supernovae[0].source_star,
            stars.stars[0],
        )

        self.assertIs(
            result.enriched_clouds[0]
            .composition["iron"],
            nuc.elements_up_to_iron["iron"],
        )

    def test_missing_public_aliases_do_not_block(
        self
    ):
        universe, stars, nuc = self._forged_layers()

        universe.world.pop(
            "first_stars",
            None,
        )
        universe.world.pop(
            "elements_up_to_iron",
            None,
        )

        result = SupernovaEnrichment(
            universe
        ).enrich_space()

        self.assertIs(
            result.state,
            SupernovaEnrichmentProcessState.ENRICHED,
        )

        self.assertIs(
            result.supernovae[0].source_star,
            stars.stars[0],
        )

        self.assertIs(
            result.enriched_clouds[0]
            .composition["iron"],
            nuc.elements_up_to_iron["iron"],
        )

    def test_world_only_inputs_cannot_trigger_supernova(
        self
    ):
        universe = Universe()

        universe.world["first_stars"] = [
            object(),
        ]
        universe.world["elements_up_to_iron"] = {
            "iron": object(),
        }

        process = SupernovaEnrichment(universe)
        result = process.enrich_space()

        self.assertIs(
            result.state,
            SupernovaEnrichmentProcessState.FAILED,
        )

        self.assertFalse(
            process.supernova_enrichment_state.stars_available
        )

        self.assertEqual(
            process.supernovae,
            [],
        )

    def test_missing_canonical_iron_preserves_failure(
        self
    ):
        universe, stars = self._formed_stars()

        nucleosynthesis = StellarNucleosynthesis(
            universe
        )

        self.assertIs(
            universe.stars_layer,
            stars,
        )

        self.assertEqual(
            nucleosynthesis.elements_up_to_iron,
            {},
        )

        result = SupernovaEnrichment(
            universe
        ).enrich_space()

        self.assertIs(
            result.state,
            SupernovaEnrichmentProcessState.FAILED,
        )

        self.assertTrue(
            result.supernova_enrichment_state.stars_available
        )

        self.assertFalse(
            result.supernova_enrichment_state.iron_available
        )

    def test_invalid_canonical_star_is_rejected(
        self
    ):
        universe = Universe()
        stars = Stars(universe)

        stars.stars.append(
            {"name": "legacy_star"}
        )

        nucleosynthesis = StellarNucleosynthesis(
            universe
        )

        nucleosynthesis.elements_up_to_iron = {
            "iron": ChemicalElement(
                name="iron",
                symbol="Fe",
                atomic_number=26,
                official=True,
                discovered=True,
                state="forged",
            ),
        }

        result = SupernovaEnrichment(
            universe
        ).enrich_space()

        self.assertEqual(
            result.type,
            "quantum_error",
        )

        self.assertIn(
            "PrimordialStar",
            result.cronenberg.origin.error_message,
        )

    def test_invalid_canonical_iron_is_rejected(
        self
    ):
        universe, stars = self._formed_stars()

        nucleosynthesis = StellarNucleosynthesis(
            universe
        )

        nucleosynthesis.elements_up_to_iron = {
            "iron": {
                "name": "iron",
                "atomic_number": 26,
            },
        }

        self.assertIs(
            universe.stars_layer,
            stars,
        )

        result = SupernovaEnrichment(
            universe
        ).enrich_space()

        self.assertEqual(
            result.type,
            "quantum_error",
        )

        self.assertIn(
            "ChemicalElement",
            result.cronenberg.origin.error_message,
        )


if __name__ == "__main__":
    unittest.main()
