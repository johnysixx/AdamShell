import unittest

from universe.cosmic_objects import StellarMaterialCloud
from universe.stellar_systems import StellarSystems
from universe.stellar_systems_process_state import (
    StellarSystemsProcessState,
)
from universe.universe import Universe


class StellarSystemsProcessStateObjectStateTests(
    unittest.TestCase
):

    def test_process_starts_ready_as_enum(self):
        process = StellarSystems(Universe())

        self.assertIs(
            process.state,
            StellarSystemsProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_missing_clouds_sets_failed_enum(self):
        process = StellarSystems(Universe())

        result = process.form_stellar_systems()

        self.assertIs(
            process.state,
            StellarSystemsProcessState.FAILED,
        )
        self.assertEqual(
            result["state"],
            "failed",
        )

    def test_formation_sets_formed_enum(self):
        universe = Universe()
        universe.world["enriched_clouds"] = [
            StellarMaterialCloud(
                name="test_enriched_cloud",
                type="enriched_stellar_cloud",
                state="expanding",
                composition={
                    "hydrogen": {},
                    "oxygen": {},
                    "silicon": {},
                    "iron": {},
                },
                can_form_stellar_systems=True,
            ),
        ]
        process = StellarSystems(universe)

        result = process.form_stellar_systems()

        self.assertIs(
            process.state,
            StellarSystemsProcessState.FORMED,
        )
        self.assertEqual(
            result["state"],
            "formed",
        )

    def test_string_state_is_rejected(self):
        process = StellarSystems(Universe())

        with self.assertRaises(TypeError):
            process.state = "formed"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state
                in StellarSystemsProcessState
            },
            {
                "ready",
                "failed",
                "formed",
            },
        )


if __name__ == "__main__":
    unittest.main()
