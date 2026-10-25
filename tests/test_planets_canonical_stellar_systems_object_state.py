import unittest
from dataclasses import replace

from universe.cosmic_objects import StellarMaterialCloud
from universe.planet_objects import EarthPlanet
from universe.planets import Planets
from universe.planets_process_state import (
    PlanetsProcessState,
)
from universe.planetary_materials import PlanetaryMaterials
from universe.planetary_materials_process_state import (
    PlanetaryMaterialsProcessState,
)
from universe.stellar_system_objects import StellarSystem
from universe.stellar_systems import StellarSystems
from universe.stellar_systems_process_state import (
    StellarSystemsProcessState,
)
from universe.supernova_enrichment import SupernovaEnrichment
from universe.universe import Universe


class PlanetsCanonicalStellarSystemsTests(
    unittest.TestCase
):

    def _ready_systems(self):
        universe = Universe()

        elements = (
            "hydrogen",
            "carbon",
            "nitrogen",
            "oxygen",
            "magnesium",
            "silicon",
            "calcium",
            "iron",
            "gold",
        )

        cloud = StellarMaterialCloud(
            name="planetary_source_cloud",
            type="enriched_stellar_cloud",
            state="expanding",
            composition={
                name: "present"
                for name in elements
            },
            can_form_stellar_systems=True,
        )

        supernova = SupernovaEnrichment(universe)
        supernova.enriched_clouds.append(cloud)

        systems = StellarSystems(universe)
        result = systems.form_stellar_systems()

        self.assertIs(
            result.state,
            StellarSystemsProcessState.FORMED,
        )

        self.assertEqual(len(systems.systems), 2)

        self.assertIs(
            systems.systems[0].source_cloud,
            cloud,
        )

        return universe, systems

    def test_planets_register_canonical_layer(self):
        universe = Universe()

        self.assertFalse(
            hasattr(universe, "planets_layer")
        )

        process = Planets(universe)

        self.assertIs(
            universe.planets_layer,
            process,
        )

        self.assertEqual(process.planets, [])

        result = process.form_planets()

        self.assertIs(
            result.state,
            PlanetsProcessState.FAILED,
        )

    def test_eight_planets_use_canonical_solar_system(
        self
    ):
        universe, systems = self._ready_systems()

        process = Planets(universe)
        result = process.form_planets()

        self.assertIs(
            result.state,
            PlanetsProcessState.FORMED,
        )

        self.assertEqual(
            [planet.name for planet in process.planets],
            [
                "mercury",
                "venus",
                "earth",
                "mars",
                "jupiter",
                "saturn",
                "uranus",
                "neptune",
            ],
        )

        self.assertIs(
            universe.stellar_systems_layer,
            systems,
        )

        self.assertIs(
            universe.world["solar_system"],
            systems.systems[0],
        )

        earth = process.find_planet("earth")

        self.assertIsInstance(earth, EarthPlanet)

        self.assertIs(
            universe.world["earth"],
            earth,
        )

        self.assertIs(
            result.planets[2],
            earth,
        )

        self.assertTrue(earth.has_iron_core)
        self.assertTrue(earth.has_rocky_crust)
        self.assertTrue(earth.water_possible)
        self.assertTrue(earth.organic_molecules_possible)

    def test_public_decoy_cannot_replace_solar_system(
        self
    ):
        universe, systems = self._ready_systems()

        universe.world["solar_system"] = {
            "name": "legacy_solar_system",
        }

        process = Planets(universe)
        result = process.form_planets()

        self.assertIs(
            result.state,
            PlanetsProcessState.FORMED,
        )

        self.assertIsInstance(
            systems.systems[0],
            StellarSystem,
        )

        self.assertIs(
            universe.planets_layer,
            process,
        )

        self.assertTrue(
            process.find_planet("earth").water_possible
        )

    def test_missing_public_alias_does_not_block(
        self
    ):
        universe, systems = self._ready_systems()

        universe.world.pop(
            "solar_system",
            None,
        )

        process = Planets(universe)
        result = process.form_planets()

        self.assertIs(
            result.state,
            PlanetsProcessState.FORMED,
        )

        self.assertEqual(len(process.planets), 8)

        self.assertIsInstance(
            systems.systems[0],
            StellarSystem,
        )

    def test_world_only_solar_system_is_not_runtime_input(
        self
    ):
        _, systems = self._ready_systems()

        universe = Universe()

        universe.world["solar_system"] = (
            systems.systems[0]
        )

        process = Planets(universe)
        result = process.form_planets()

        self.assertIs(
            result.state,
            PlanetsProcessState.FAILED,
        )

        self.assertEqual(process.planets, [])

        self.assertFalse(
            process.planetary_state.earth_formed
        )

    def test_inactive_canonical_disk_still_fails(
        self
    ):
        universe, systems = self._ready_systems()

        solar_system = systems.systems[0]

        inactive_disk = replace(
            solar_system.protoplanetary_disk,
            can_form_planets=False,
        )

        systems.systems[0] = replace(
            solar_system,
            protoplanetary_disk=inactive_disk,
        )

        result = Planets(universe).form_planets()

        self.assertIs(
            result.state,
            PlanetsProcessState.FAILED,
        )

        self.assertFalse(
            result.planetary_state.planets_formed
        )

    def test_invalid_canonical_solar_system_is_rejected(
        self
    ):
        universe = Universe()

        systems = StellarSystems(universe)

        systems.systems.append(
            {
                "name": "legacy_solar_system",
                "protoplanetary_disk": {},
            }
        )

        process = Planets(universe)

        with self.assertRaisesRegex(
            TypeError,
            "StellarSystem",
        ):
            process._form_planets_unprotected()

    def test_no_public_read_and_materialization_works(
        self
    ):
        class GuardedWorld(dict):

            def get(self, key, default=None):
                if key == "solar_system":
                    raise AssertionError(
                        "Planets read public solar system"
                    )

                return super().get(key, default)

            def __getitem__(self, key):
                if key == "solar_system":
                    raise AssertionError(
                        "Planets indexed public solar system"
                    )

                return super().__getitem__(key)

        universe, systems = self._ready_systems()

        universe.world = GuardedWorld(
            universe.world
        )

        process = Planets(universe)
        result = process.form_planets()

        self.assertIs(
            result.state,
            PlanetsProcessState.FORMED,
        )

        self.assertIs(
            universe.stellar_systems_layer,
            systems,
        )

        materials = PlanetaryMaterials(universe)
        material_result = materials.materialize()

        self.assertIs(
            material_result.state,
            PlanetaryMaterialsProcessState.MATERIALIZED,
        )

        self.assertEqual(
            set(materials.available_materials),
            {
                "water",
                "ice",
                "minerals",
                "organic_molecules",
            },
        )

        self.assertIs(
            universe.world["earth"],
            process.find_planet("earth"),
        )


if __name__ == "__main__":
    unittest.main()
