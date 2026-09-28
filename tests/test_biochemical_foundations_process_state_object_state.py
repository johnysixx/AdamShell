import unittest

from universe.biochemical_foundations import (
    BiochemicalFoundations,
)
from universe.biochemical_foundations_process_state import (
    BiochemicalFoundationsProcessState,
)
from universe.planetary_material_objects import (
    PlanetaryMaterial,
)
from universe.universe import Universe


class BiochemicalFoundationsProcessStateObjectStateTests(
    unittest.TestCase
):

    def _materials(self):
        water = PlanetaryMaterial(
            name="water",
            requires=("hydrogen", "oxygen"),
        )
        organic_molecules = PlanetaryMaterial(
            name="organic_molecules",
            requires=(
                "carbon",
                "hydrogen",
                "oxygen",
                "nitrogen",
            ),
        )

        return {
            "water": water.make_available(
                origin="test"
            ),
            "organic_molecules": (
                organic_molecules.make_available(
                    origin="test"
                )
            ),
        }

    def test_process_starts_ready_as_enum(self):
        process = BiochemicalFoundations(
            Universe()
        )

        self.assertIs(
            process.state,
            BiochemicalFoundationsProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_missing_material_sets_failed_enum(self):
        process = BiochemicalFoundations(
            Universe()
        )

        result = (
            process.form_biochemical_foundations()
        )

        self.assertIs(
            process.state,
            BiochemicalFoundationsProcessState.FAILED,
        )
        self.assertEqual(
            result["state"],
            "failed",
        )

    def test_formation_sets_formed_enum(self):
        universe = Universe()
        universe.world[
            "available_planetary_materials"
        ] = self._materials()

        process = BiochemicalFoundations(
            universe
        )

        result = (
            process.form_biochemical_foundations()
        )

        self.assertIs(
            process.state,
            BiochemicalFoundationsProcessState.FORMED,
        )
        self.assertEqual(
            result["state"],
            "formed",
        )

    def test_string_state_is_rejected(self):
        process = BiochemicalFoundations(
            Universe()
        )

        with self.assertRaises(TypeError):
            process.state = "formed"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state
                in BiochemicalFoundationsProcessState
            },
            {
                "ready",
                "failed",
                "formed",
            },
        )


if __name__ == "__main__":
    unittest.main()
