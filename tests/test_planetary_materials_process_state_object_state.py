import unittest

from universe.planet_state import PlanetFormationState
from universe.planetary_material_objects import (
    PlanetaryMaterial,
)
from universe.planetary_materials import PlanetaryMaterials
from universe.planetary_materials_process_state import (
    PlanetaryMaterialsProcessState,
)
from universe.universe import Universe


class PlanetaryMaterialsProcessStateObjectStateTests(
    unittest.TestCase
):

    def _possible_materials(self):
        return {
            "water": PlanetaryMaterial(
                name="water",
                requires=("hydrogen", "oxygen"),
            ),
            "ice": PlanetaryMaterial(
                name="ice",
                requires=("water", "cold"),
            ),
            "minerals": PlanetaryMaterial(
                name="minerals",
                requires=("silicon", "iron"),
            ),
            "organic_molecules": PlanetaryMaterial(
                name="organic_molecules",
                requires=(
                    "carbon",
                    "hydrogen",
                    "oxygen",
                    "nitrogen",
                ),
            ),
        }

    def test_process_starts_ready_as_enum(self):
        process = PlanetaryMaterials(Universe())

        self.assertIs(
            process.state,
            PlanetaryMaterialsProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_missing_earth_sets_failed_enum(self):
        process = PlanetaryMaterials(Universe())

        result = process.materialize()

        self.assertIs(
            process.state,
            PlanetaryMaterialsProcessState.FAILED,
        )
        self.assertEqual(
            result["state"],
            "failed",
        )

    def test_materialization_sets_materialized_enum(
        self
    ):
        universe = Universe()
        universe.world["planetary_state"] = (
            PlanetFormationState(
                planets_formed=True,
                earth_formed=True,
                water_possible=True,
                ice_possible=True,
                minerals_possible=True,
                organic_molecules_possible=True,
            )
        )
        universe.world["planetary_materials"] = (
            self._possible_materials()
        )
        process = PlanetaryMaterials(universe)

        result = process.materialize()

        self.assertIs(
            process.state,
            PlanetaryMaterialsProcessState.MATERIALIZED,
        )
        self.assertEqual(
            result["state"],
            "materialized",
        )

    def test_string_state_is_rejected(self):
        process = PlanetaryMaterials(Universe())

        with self.assertRaises(TypeError):
            process.state = "materialized"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state
                in PlanetaryMaterialsProcessState
            },
            {
                "ready",
                "failed",
                "materialized",
            },
        )


if __name__ == "__main__":
    unittest.main()
