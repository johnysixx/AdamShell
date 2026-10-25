import unittest

from universe.chemical_objects import ChemicalElement
from universe.cosmic_objects import StellarMaterialCloud
from universe.heavy_element_nucleosynthesis import (
    HeavyElementNucleosynthesis,
)
from universe.heavy_element_nucleosynthesis_process_state import (
    HeavyElementNucleosynthesisProcessState,
)
from universe.universe import Universe
from universe.stellar_nucleosynthesis import StellarNucleosynthesis
from universe.supernova_enrichment import SupernovaEnrichment


class HeavyElementNucleosynthesisProcessStateObjectStateTests(
    unittest.TestCase
):

    def _wire_canonical_inputs(self, universe):
        if "elements_up_to_iron" in universe.world:
            nucleosynthesis = StellarNucleosynthesis(
                universe
            )
            nucleosynthesis.elements_up_to_iron = (
                universe.world["elements_up_to_iron"]
            )

        if "enriched_clouds" in universe.world:
            supernova = SupernovaEnrichment(universe)
            supernova.enriched_clouds = (
                universe.world["enriched_clouds"]
            )

    def _ready_universe(self):
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

        self._wire_canonical_inputs(universe)

        return universe

    def test_process_starts_ready_as_enum(self):
        process = HeavyElementNucleosynthesis(
            Universe()
        )

        self.assertIs(
            process.state,
            HeavyElementNucleosynthesisProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_missing_iron_sets_failed_enum(self):
        process = HeavyElementNucleosynthesis(
            Universe()
        )

        result = process.forge_heavy_elements()

        self.assertIs(
            process.state,
            HeavyElementNucleosynthesisProcessState.FAILED,
        )
        self.assertIs(
            result.state,
            HeavyElementNucleosynthesisProcessState.FAILED,
        )

    def test_missing_clouds_sets_failed_enum(self):
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

        self._wire_canonical_inputs(universe)

        process = HeavyElementNucleosynthesis(
            universe
        )

        result = process.forge_heavy_elements()

        self.assertIs(
            process.state,
            HeavyElementNucleosynthesisProcessState.FAILED,
        )
        self.assertIs(
            result.state,
            HeavyElementNucleosynthesisProcessState.FAILED,
        )

    def test_forging_sets_forged_enum(self):
        process = HeavyElementNucleosynthesis(
            self._ready_universe()
        )

        result = process.forge_heavy_elements()

        self.assertIs(
            process.state,
            HeavyElementNucleosynthesisProcessState.FORGED,
        )
        self.assertIs(
            result.state,
            HeavyElementNucleosynthesisProcessState.FORGED,
        )

    def test_string_state_is_rejected(self):
        process = HeavyElementNucleosynthesis(
            Universe()
        )

        with self.assertRaises(TypeError):
            process.state = "forged"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state
                in HeavyElementNucleosynthesisProcessState
            },
            {
                "ready",
                "failed",
                "forged",
            },
        )


if __name__ == "__main__":
    unittest.main()
