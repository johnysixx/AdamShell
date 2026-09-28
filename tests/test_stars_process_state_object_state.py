import unittest

from universe.cosmic_objects import StellarMaterialCloud
from universe.stars import Stars
from universe.stars_process_state import (
    StarsProcessState,
)
from universe.universe import Universe


class StarsProcessStateObjectStateTests(
    unittest.TestCase
):

    def test_process_starts_ready_as_enum(self):
        process = Stars(Universe())

        self.assertIs(
            process.state,
            StarsProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_missing_clouds_sets_failed_enum(self):
        process = Stars(Universe())

        result = process.form_first_stars()

        self.assertIs(
            process.state,
            StarsProcessState.FAILED,
        )
        self.assertEqual(
            result["state"],
            "failed",
        )

    def test_formation_sets_formed_enum(self):
        universe = Universe()
        universe.world["germinal_clouds"] = [
            StellarMaterialCloud(
                name="test_cloud",
                type="germinal_cloud",
                state="condensing",
                composition={},
                can_form_stars=True,
            ),
        ]
        process = Stars(universe)

        result = process.form_first_stars()

        self.assertIs(
            process.state,
            StarsProcessState.FORMED,
        )
        self.assertEqual(
            result["state"],
            "formed",
        )

    def test_string_state_is_rejected(self):
        process = Stars(Universe())

        with self.assertRaises(TypeError):
            process.state = "formed"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in StarsProcessState
            },
            {
                "ready",
                "failed",
                "formed",
            },
        )


if __name__ == "__main__":
    unittest.main()
