import unittest

from universe.cosmic_objects import StellarMaterialCloud
from universe.planet_objects import EarthPlanet, Planet
from universe.planetary_material_objects import PlanetaryMaterial
from universe.planet_state import PlanetFormationState
from universe.planet_formation_result_state import (
    PlanetFormationResult,
)
from universe.planetary_materials import PlanetaryMaterials
from universe.planetary_materials_process_state import (
    PlanetaryMaterialsProcessState,
)
from universe.planets import Planets
from universe.planets_process_state import (
    PlanetsProcessState,
)
from universe.stellar_system_objects import (
    ProtoplanetaryDisk,
    SecondGenerationStar,
    StellarSystem,
)
from universe.universe import Universe
from universe.stellar_systems import StellarSystems


class PlanetFormationObjectStateTests(
    unittest.TestCase
):

    def _wire_canonical_system(
        self, universe, source_system=None
    ):
        if source_system is not None:
            systems_layer = StellarSystems(universe)
            systems_layer.systems.append(source_system)


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

    def _solar_system(
        self,
        available_elements,
        *,
        can_form_planets=True,
    ):
        elements = tuple(available_elements)
        source_cloud = StellarMaterialCloud(
            name="planet_test_cloud",
            type="enriched_stellar_cloud",
            state="expanding",
            composition={
                element_name: {}
                for element_name in elements
            },
            can_form_stellar_systems=True,
        )
        return StellarSystem(
            name="solar_system",
            type="stellar_system",
            state="forming",
            generation=2,
            source_cloud=source_cloud,
            star=SecondGenerationStar(
                name="sun",
                type="main_sequence_star",
                state="ignited",
                generation=2,
            ),
            protoplanetary_disk=ProtoplanetaryDisk(
                name="solar_protoplanetary_disk",
                type="protoplanetary_disk",
                state="rotating",
                available_elements=elements,
                can_form_planets=can_form_planets,
                can_form_water=(
                    "hydrogen" in elements
                    and "oxygen" in elements
                ),
                can_form_iron_cores="iron" in elements,
                can_form_rocky_worlds=(
                    "silicon" in elements
                    and "iron" in elements
                ),
            ),
        )

    def _formed_process(self):
        universe = Universe()
        source_system = self._solar_system(
            (
                "hydrogen",
                "carbon",
                "nitrogen",
                "oxygen",
                "magnesium",
                "silicon",
                "calcium",
                "iron",
            )
        )

        self._wire_canonical_system(universe, source_system)

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
        self.assertNotIn(
            "planetary_state",
            universe.world,
        )
        self.assertIs(
            process.result.planetary_state,
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
        self.assertTrue(
            all(
                isinstance(material, PlanetaryMaterial)
                for material in process.planetary_materials.values()
            )
        )
        self.assertIsInstance(
            universe.world["earth"],
            EarthPlanet,
        )
        self.assertTrue(
            all(
                isinstance(planet, Planet)
                for planet in universe.world["solar_planets"]
            )
        )

    def test_runtime_result_is_object_and_snapshot_is_dict(
        self
    ):
        _, process, result = self._formed_process()

        self.assertIsInstance(
            result,
            PlanetFormationResult,
        )
        self._assert_object_only(
            result,
            "state",
        )

        self.assertIs(
            result.planetary_state,
            process.planetary_state,
        )
        self.assertIsInstance(
            result.planets,
            tuple,
        )
        self.assertIs(
            result.planets[2],
            process.planets[2],
        )
        self.assertIs(
            result.planetary_materials["water"],
            process.planetary_materials["water"],
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot["planetary_state"],
            dict,
        )
        self.assertIsInstance(
            snapshot["planets"],
            list,
        )
        self.assertIsInstance(
            snapshot["planetary_materials"],
            dict,
        )
        self.assertTrue(
            snapshot["planetary_state"][
                "earth_formed"
            ]
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = self._formed_process()

        snapshot = result.to_dict()

        snapshot["planetary_state"][
            "earth_formed"
        ] = False
        snapshot["planets"][2]["name"] = "fake_earth"
        snapshot["planetary_materials"]["water"][
            "requires"
        ].append("fake_element")

        self.assertTrue(
            process.planetary_state.earth_formed
        )
        self.assertEqual(
            process.planets[2].name,
            "earth",
        )
        self.assertNotIn(
            "fake_element",
            process.planetary_materials["water"].requires,
        )

    def test_possibilities_follow_available_elements(
        self
    ):
        universe = Universe()
        source_system = self._solar_system(
            ("hydrogen",)
        )
        self._wire_canonical_system(universe, source_system)

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
        self._wire_canonical_system(universe, None)

        process = Planets(universe)

        result = process.form_planets()

        self.assertIs(
            process.state,
            PlanetsProcessState.FAILED,
        )
        self.assertFalse(
            process.planetary_state.planets_formed
        )
        self.assertFalse(
            result
            .planetary_state
            .planets_formed
        )

    def test_inactive_disk_preserves_state(self):
        universe = Universe()
        source_system = self._solar_system(
            (),
            can_form_planets=False,
        )
        self._wire_canonical_system(universe, source_system)

        process = Planets(universe)

        result = process.form_planets()

        self.assertIs(
            process.state,
            PlanetsProcessState.FAILED,
        )
        self.assertFalse(
            process.planetary_state.planets_formed
        )
        self.assertFalse(
            result
            .planetary_state
            .planets_formed
        )


    def test_legacy_solar_system_dict_is_rejected(self):
        universe = Universe()
        source_system = {
            "name": "legacy_solar_system",
            "protoplanetary_disk": {},
        }
        self._wire_canonical_system(universe, source_system)

        process = Planets(universe)

        with self.assertRaises(TypeError):
            process._form_planets_unprotected()

    def test_planetary_materials_reads_object_state(
        self
    ):
        universe, _, _ = self._formed_process()
        process = PlanetaryMaterials(universe)

        result = process.materialize()

        self.assertIs(
            result.state,
            PlanetaryMaterialsProcessState.MATERIALIZED,
        )
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
        source_system = self._solar_system(
            ("iron",)
        )
        self._wire_canonical_system(universe, source_system)

        process = Planets(universe)

        def broken_history():
            raise RuntimeError(
                "planet formation exploded"
            )

        process.record_history = broken_history

        result = process.form_planets()
        cronenberg = result.cronenberg

        self.assertEqual(
            result.type,
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
