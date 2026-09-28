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


class HeavyElementNucleosynthesisProcessStateObjectStateTests(
    unittest.TestCase
):

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
        self.assertEqual(
            result["state"],
            "failed",
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

        process = HeavyElementNucleosynthesis(
            universe
        )

        result = process.forge_heavy_elements()

        self.assertIs(
            process.state,
            HeavyElementNucleosynthesisProcessState.FAILED,
        )
        self.assertEqual(
            result["state"],
            "failed",
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
        self.assertEqual(
            result["state"],
            "forged",
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
