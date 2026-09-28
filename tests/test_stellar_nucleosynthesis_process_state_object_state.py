import unittest

from universe.cosmic_objects import StellarMaterialCloud
from universe.stars import Stars
from universe.stellar_nucleosynthesis import (
    StellarNucleosynthesis,
)
from universe.stellar_nucleosynthesis_process_state import (
    StellarNucleosynthesisProcessState,
)
from universe.universe import Universe


class StellarNucleosynthesisProcessStateObjectStateTests(
    unittest.TestCase
):

    def _forged_process(self):
        universe = Universe()
        universe.world["germinal_clouds"] = [
            StellarMaterialCloud(
                name="cloud_a",
                type="germinal_cloud",
                state="condensing",
                composition={},
                can_form_stars=True,
            ),
        ]

        Stars(universe).form_first_stars()

        process = StellarNucleosynthesis(
            universe
        )
        result = (
            process.forge_elements_up_to_iron()
        )

        return process, result

    def test_process_starts_ready_as_enum(self):
        process = StellarNucleosynthesis(
            Universe()
        )

        self.assertIs(
            process.state,
            StellarNucleosynthesisProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_missing_stars_sets_failed_enum(self):
        process = StellarNucleosynthesis(
            Universe()
        )

        result = (
            process.forge_elements_up_to_iron()
        )

        self.assertIs(
            process.state,
            StellarNucleosynthesisProcessState.FAILED,
        )
        self.assertEqual(
            result["state"],
            "failed",
        )

    def test_forging_sets_forged_enum(self):
        process, result = self._forged_process()

        self.assertIs(
            process.state,
            StellarNucleosynthesisProcessState.FORGED,
        )
        self.assertEqual(
            result["state"],
            "forged",
        )

    def test_string_state_is_rejected(self):
        process = StellarNucleosynthesis(
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
                in StellarNucleosynthesisProcessState
            },
            {
                "ready",
                "failed",
                "forged",
            },
        )


if __name__ == "__main__":
    unittest.main()
