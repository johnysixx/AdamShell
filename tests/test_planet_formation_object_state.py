import unittest

from universe.planet_state import PlanetFormationState
from universe.planetary_materials import PlanetaryMaterials
from universe.planets import Planets
from universe.universe import Universe


class PlanetFormationObjectStateTests(
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

    def _formed_process(self):
        universe = Universe()
        universe.world["solar_system"] = {
            "name": "solar_system",
            "protoplanetary_disk": {
                "can_form_planets": True,
                "available_elements": [
                    "hydrogen",
                    "carbon",
                    "nitrogen",
                    "oxygen",
                    "magnesium",
                    "silicon",
                    "calcium",
                    "iron",
                ],
            },
        }

        process = Planets(universe)
        result = process.form_planets()

        return universe, process, result

    def test_state_is_object_only(self):
        state = PlanetFormationState()

        self._assert_object_only(
            state,
            "planets_formed",
        )

    def test_initial_values_are_preserved(self):
        state = PlanetFormationState()

        self.assertFalse(state.planets_formed)
        self.assertFalse(state.earth_formed)
        self.assertFalse(state.water_possible)
        self.assertFalse(state.ice_possible)
        self.assertFalse(state.minerals_possible)
        self.assertFalse(
            state.organic_molecules_possible
        )

    def test_formation_mutates_same_state_object(
        self
    ):
        universe, process, _ = self._formed_process()
        state = process.planetary_state

        self.assertIs(process.planetary_state, state)
        self.assertIs(
            universe.world["planetary_state"],
            state,
        )
        self.assertTrue(state.planets_formed)
        self.assertTrue(state.earth_formed)
        self.assertTrue(state.water_possible)
        self.assertTrue(state.ice_possible)
        self.assertTrue(state.minerals_possible)
        self.assertTrue(
            state.organic_molecules_possible
        )

    def test_world_keeps_boundary_registries(
        self
    ):
        universe, process, _ = self._formed_process()

        self.assertIs(
            universe.world["solar_planets"],
            process.planets,
        )
        self.assertIs(
            universe.world["planetary_materials"],
            process.planetary_materials,
        )
        self.assertIs(
            universe.world["earth"],
            process.planets[2],
        )
        self.assertIsInstance(
            universe.world["solar_planets"],
            list,
        )
        self.assertIsInstance(
            universe.world["planetary_materials"],
            dict,
        )
        self.assertIsInstance(
            universe.world["earth"],
            dict,
        )

    def test_public_result_remains_dict_boundary(
        self
    ):
        _, _, result = self._formed_process()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["planetary_state"],
            dict,
        )
        self.assertIsInstance(result["planets"], list)
        self.assertIsInstance(
            result["planetary_materials"],
            dict,
        )
        self.assertTrue(
            result["planetary_state"][
                "earth_formed"
            ]
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = self._formed_process()

        result["planetary_state"][
            "earth_formed"
        ] = False
        result["planets"][2]["name"] = "fake_earth"
        result["planetary_materials"]["water"][
            "requires"
        ].append("fake_element")

        self.assertTrue(
            process.planetary_state.earth_formed
        )
        self.assertEqual(
            process.planets[2]["name"],
            "earth",
        )
        self.assertNotIn(
            "fake_element",
            process.planetary_materials["water"][
                "requires"
            ],
        )

    def test_possibilities_follow_available_elements(
        self
    ):
        universe = Universe()
        universe.world["solar_system"] = {
            "protoplanetary_disk": {
                "can_form_planets": True,
                "available_elements": ["hydrogen"],
            }
        }
        process = Planets(universe)

        process.form_planets()

        self.assertTrue(
            process.planetary_state.planets_formed
        )
        self.assertTrue(
            process.planetary_state.earth_formed
        )
        self.assertFalse(
            process.planetary_state.water_possible
        )
        self.assertFalse(
            process.planetary_state.ice_possible
        )
        self.assertFalse(
            process.planetary_state.minerals_possible
        )
        self.assertFalse(
            process
            .planetary_state
            .organic_molecules_possible
        )

    def test_missing_solar_system_preserves_state(
        self
    ):
        universe = Universe()
        process = Planets(universe)

        result = process.form_planets()

        self.assertEqual(process.state, "failed")
        self.assertFalse(
            process.planetary_state.planets_formed
        )
        self.assertFalse(
            result["planetary_state"][
                "planets_formed"
            ]
        )

    def test_inactive_disk_preserves_state(self):
        universe = Universe()
        universe.world["solar_system"] = {
            "protoplanetary_disk": {
                "can_form_planets": False,
            }
        }
        process = Planets(universe)

        result = process.form_planets()

        self.assertEqual(process.state, "failed")
        self.assertFalse(
            process.planetary_state.planets_formed
        )
        self.assertFalse(
            result["planetary_state"][
                "planets_formed"
            ]
        )

    def test_planetary_materials_reads_object_state(
        self
    ):
        universe, _, _ = self._formed_process()
        process = PlanetaryMaterials(universe)

        result = process.materialize()

        self.assertEqual(result["state"], "materialized")
        self.assertIn(
            "water",
            universe.world[
                "available_planetary_materials"
            ],
        )
        self.assertIn(
            "organic_molecules",
            process.available_materials,
        )

    def test_formation_error_creates_cronenberg(
        self
    ):
        universe = Universe()
        universe.world["solar_system"] = {
            "protoplanetary_disk": {
                "can_form_planets": True,
                "available_elements": ["iron"],
            }
        }
        process = Planets(universe)

        def broken_history():
            raise RuntimeError(
                "planet formation exploded"
            )

        process.record_history = broken_history

        result = process.form_planets()
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
            "planets",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "form_planets",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "planet formation exploded",
        )

    def test_to_dict_is_detached_boundary(self):
        state = PlanetFormationState()
        state.earth_formed = True

        snapshot = state.to_dict()
        snapshot["earth_formed"] = False

        self.assertTrue(state.earth_formed)


if __name__ == "__main__":
    unittest.main()
