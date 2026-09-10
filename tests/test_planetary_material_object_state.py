import unittest

from universe.biochemical_foundations import (
    BiochemicalFoundations,
)
from universe.planet_state import PlanetFormationState
from universe.planetary_material_state import (
    PlanetaryMaterialState,
)
from universe.planetary_materials import PlanetaryMaterials
from universe.universe import Universe


class PlanetaryMaterialObjectStateTests(
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

    def _possible_materials(self):
        return {
            "water": {
                "name": "water",
                "requires": ["hydrogen", "oxygen"],
            },
            "ice": {
                "name": "ice",
                "requires": ["water", "cold"],
            },
            "minerals": {
                "name": "minerals",
                "requires": ["silicon", "iron"],
            },
            "organic_molecules": {
                "name": "organic_molecules",
                "requires": [
                    "carbon",
                    "hydrogen",
                    "oxygen",
                    "nitrogen",
                ],
            },
        }

    def _materialized_process(self):
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

        return universe, process, result

    def test_state_is_object_only(self):
        state = PlanetaryMaterialState()

        self._assert_object_only(
            state,
            "water_available",
        )

    def test_initial_values_are_preserved(self):
        state = PlanetaryMaterialState()

        self.assertFalse(state.water_available)
        self.assertFalse(state.ice_available)
        self.assertFalse(state.minerals_available)
        self.assertFalse(
            state.organic_molecules_available
        )

    def test_materialization_mutates_same_state_object(
        self
    ):
        universe, process, _ = (
            self._materialized_process()
        )
        state = process.material_state

        self.assertIs(process.material_state, state)
        self.assertIs(
            universe.world["planetary_material_state"],
            state,
        )
        self.assertTrue(state.water_available)
        self.assertTrue(state.ice_available)
        self.assertTrue(state.minerals_available)
        self.assertTrue(
            state.organic_molecules_available
        )

    def test_world_keeps_material_registry_boundary(
        self
    ):
        universe, process, _ = (
            self._materialized_process()
        )

        self.assertIs(
            universe.world[
                "available_planetary_materials"
            ],
            process.available_materials,
        )
        self.assertIsInstance(
            universe.world[
                "available_planetary_materials"
            ],
            dict,
        )

    def test_public_result_remains_dict_boundary(
        self
    ):
        _, _, result = self._materialized_process()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["material_state"],
            dict,
        )
        self.assertIsInstance(
            result["available_materials"],
            dict,
        )
        self.assertTrue(
            result["material_state"][
                "water_available"
            ]
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = (
            self._materialized_process()
        )

        result["material_state"][
            "water_available"
        ] = False
        result["available_materials"]["water"][
            "requires"
        ].append("fake_element")

        self.assertTrue(
            process.material_state.water_available
        )
        self.assertNotIn(
            "fake_element",
            process.available_materials["water"][
                "requires"
            ],
        )

    def test_availability_follows_planet_state(
        self
    ):
        universe = Universe()
        universe.world["planetary_state"] = (
            PlanetFormationState(
                planets_formed=True,
                earth_formed=True,
                water_possible=True,
            )
        )
        universe.world["planetary_materials"] = (
            self._possible_materials()
        )
        process = PlanetaryMaterials(universe)

        process.materialize()

        self.assertTrue(
            process.material_state.water_available
        )
        self.assertFalse(
            process.material_state.ice_available
        )
        self.assertFalse(
            process.material_state.minerals_available
        )
        self.assertFalse(
            process
            .material_state
            .organic_molecules_available
        )

    def test_missing_definition_stays_unavailable(
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
        universe.world["planetary_materials"] = {
            "water": {
                "name": "water",
                "requires": ["hydrogen", "oxygen"],
            }
        }
        process = PlanetaryMaterials(universe)

        process.materialize()

        self.assertTrue(
            process.material_state.water_available
        )
        self.assertFalse(
            process.material_state.ice_available
        )
        self.assertFalse(
            process.material_state.minerals_available
        )
        self.assertFalse(
            process
            .material_state
            .organic_molecules_available
        )

    def test_missing_earth_preserves_initial_state(
        self
    ):
        universe = Universe()
        process = PlanetaryMaterials(universe)

        result = process.materialize()

        self.assertEqual(process.state, "failed")
        self.assertFalse(
            process.material_state.water_available
        )
        self.assertFalse(
            result["material_state"][
                "water_available"
            ]
        )

    def test_biochemical_process_uses_registry_boundary(
        self
    ):
        universe, _, _ = self._materialized_process()
        process = BiochemicalFoundations(universe)

        result = process.form_biochemical_foundations()

        self.assertEqual(result["state"], "formed")
        self.assertIn(
            "sugars",
            universe.world["biochemical_compounds"],
        )

    def test_materialization_error_creates_cronenberg(
        self
    ):
        universe = Universe()
        universe.world["planetary_state"] = (
            PlanetFormationState(
                earth_formed=True,
                water_possible=True,
            )
        )
        universe.world["planetary_materials"] = (
            self._possible_materials()
        )
        process = PlanetaryMaterials(universe)

        def broken_history():
            raise RuntimeError(
                "planetary materialization exploded"
            )

        process.record_history = broken_history

        result = process.materialize()
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
            "planetary_materials",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "materialize",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "planetary materialization exploded",
        )

    def test_to_dict_is_detached_boundary(self):
        state = PlanetaryMaterialState()
        state.water_available = True

        snapshot = state.to_dict()
        snapshot["water_available"] = False

        self.assertTrue(state.water_available)


if __name__ == "__main__":
    unittest.main()
