import unittest

from universe.biochemical_foundations import (
    BiochemicalFoundations,
)
from universe.biochemical_foundations_process_state import (
    BiochemicalFoundationsProcessState,
)
from universe.cosmic_objects import StellarMaterialCloud
from universe.planet_state import PlanetFormationState
from universe.planets import Planets
from universe.planets_process_state import (
    PlanetsProcessState,
)
from universe.planetary_material_objects import (
    AvailablePlanetaryMaterial,
    PlanetaryMaterial,
)
from universe.planetary_materials import PlanetaryMaterials
from universe.planetary_materials_process_state import (
    PlanetaryMaterialsProcessState,
)
from universe.stellar_systems import StellarSystems
from universe.stellar_systems_process_state import (
    StellarSystemsProcessState,
)
from universe.supernova_enrichment import (
    SupernovaEnrichment,
)
from universe.universe import Universe


class PlanetaryMaterialsCanonicalPlanetsTests(
    unittest.TestCase
):

    def _formed_planets(self):
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
        )

        cloud = StellarMaterialCloud(
            name="material_source_cloud",
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

        system_result = systems.form_stellar_systems()

        self.assertIs(
            system_result.state,
            StellarSystemsProcessState.FORMED,
        )

        planets = Planets(universe)
        planet_result = planets.form_planets()

        self.assertIs(
            planet_result.state,
            PlanetsProcessState.FORMED,
        )

        self.assertTrue(planets.planetary_state.earth_formed)

        return universe, planets

    def test_materials_register_canonical_layer(self):
        universe = Universe()

        self.assertFalse(
            hasattr(
                universe,
                "planetary_materials_layer",
            )
        )

        layer = PlanetaryMaterials(universe)

        self.assertIs(
            universe.planetary_materials_layer,
            layer,
        )

        self.assertEqual(layer.available_materials, {})

    def test_full_canonical_materialization_preserves_identity(
        self
    ):
        universe, planets = self._formed_planets()

        process = PlanetaryMaterials(universe)
        result = process.materialize()

        self.assertIs(
            result.state,
            PlanetaryMaterialsProcessState.MATERIALIZED,
        )

        expected = {
            "water",
            "ice",
            "minerals",
            "organic_molecules",
        }

        self.assertEqual(
            set(process.available_materials),
            expected,
        )

        self.assertIs(
            universe.planetary_materials_layer,
            process,
        )

        self.assertIs(
            universe.world["available_planetary_materials"],
            process.available_materials,
        )

        self.assertIs(
            universe.world["planetary_material_state"],
            process.material_state,
        )

        for name in expected:
            with self.subTest(material=name):
                available = process.available_materials[
                    name
                ]

                self.assertIsInstance(
                    available,
                    AvailablePlanetaryMaterial,
                )

                self.assertIs(
                    available.material,
                    planets.planetary_materials[name],
                )

                self.assertIs(
                    result.available_materials[name],
                    available,
                )

    def test_public_decoys_cannot_override_planets(
        self
    ):
        universe, planets = self._formed_planets()

        universe.world["planetary_state"] = (
            PlanetFormationState()
        )

        universe.world["planetary_materials"] = {
            "water": {
                "name": "legacy_material",
            },
        }

        process = PlanetaryMaterials(universe)
        result = process.materialize()

        self.assertIs(
            result.state,
            PlanetaryMaterialsProcessState.MATERIALIZED,
        )

        self.assertEqual(
            len(process.available_materials),
            4,
        )

        self.assertIs(
            process.available_materials["water"].material,
            planets.planetary_materials["water"],
        )

    def test_missing_public_aliases_do_not_block(
        self
    ):
        universe, planets = self._formed_planets()

        universe.world.pop("planetary_state", None)
        universe.world.pop("planetary_materials", None)

        process = PlanetaryMaterials(universe)
        result = process.materialize()

        self.assertIs(
            result.state,
            PlanetaryMaterialsProcessState.MATERIALIZED,
        )

        self.assertIs(
            process.available_materials[
                "organic_molecules"
            ].material,
            planets.planetary_materials[
                "organic_molecules"
            ],
        )

    def test_world_only_planet_data_cannot_materialize(
        self
    ):
        universe = Universe()

        universe.world["planetary_state"] = (
            PlanetFormationState(
                earth_formed=True,
                water_possible=True,
            )
        )

        universe.world["planetary_materials"] = {
            "water": PlanetaryMaterial(
                name="water",
                requires=("hydrogen", "oxygen"),
            ),
        }

        process = PlanetaryMaterials(universe)
        result = process.materialize()

        self.assertIs(
            result.state,
            PlanetaryMaterialsProcessState.FAILED,
        )

        self.assertEqual(
            process.available_materials,
            {},
        )

    def test_canonical_possibility_flags_control_materials(
        self
    ):
        universe = Universe()

        planets = Planets(universe)
        planets.planetary_state = PlanetFormationState(
            earth_formed=True,
            water_possible=True,
        )

        universe.world["planetary_state"] = (
            PlanetFormationState(
                earth_formed=True,
                water_possible=False,
                ice_possible=True,
                minerals_possible=True,
                organic_molecules_possible=True,
            )
        )

        process = PlanetaryMaterials(universe)
        result = process.materialize()

        self.assertIs(
            result.state,
            PlanetaryMaterialsProcessState.MATERIALIZED,
        )

        self.assertEqual(
            set(process.available_materials),
            {"water"},
        )

        self.assertTrue(process.material_state.water_available)
        self.assertFalse(process.material_state.ice_available)
        self.assertFalse(
            process.material_state.minerals_available
        )
        self.assertFalse(
            process.material_state.organic_molecules_available
        )

    def test_invalid_canonical_definition_is_rejected(
        self
    ):
        universe = Universe()

        planets = Planets(universe)
        planets.planetary_state = PlanetFormationState(
            earth_formed=True,
            water_possible=True,
        )

        planets.planetary_materials["water"] = {
            "name": "legacy_water",
        }

        process = PlanetaryMaterials(universe)

        with self.assertRaisesRegex(
            TypeError,
            "PlanetaryMaterial",
        ):
            process._materialize_unprotected()

    def test_no_public_reads_and_biochemistry_works(
        self
    ):
        class GuardedWorld(dict):

            def get(self, key, default=None):
                if key in (
                    "planetary_state",
                    "planetary_materials",
                ):
                    raise AssertionError(
                        "Read from public planetary registry"
                    )

                return super().get(key, default)

            def __getitem__(self, key):
                if key in (
                    "planetary_state",
                    "planetary_materials",
                ):
                    raise AssertionError(
                        "Indexed public planetary registry"
                    )

                return super().__getitem__(key)

        universe, planets = self._formed_planets()

        universe.world = GuardedWorld(
            universe.world
        )

        process = PlanetaryMaterials(universe)
        result = process.materialize()

        self.assertIs(
            result.state,
            PlanetaryMaterialsProcessState.MATERIALIZED,
        )

        self.assertIs(
            universe.planets_layer,
            planets,
        )

        biochemical = BiochemicalFoundations(universe)
        biochemical_result = (
            biochemical.form_biochemical_foundations()
        )

        self.assertIs(
            biochemical_result.state,
            BiochemicalFoundationsProcessState.FORMED,
        )

        self.assertIn(
            "sugars",
            biochemical.compounds,
        )

        self.assertIn(
            "amino_acids",
            biochemical.compounds,
        )

        self.assertIn(
            "lipids",
            biochemical.compounds,
        )


if __name__ == "__main__":
    unittest.main()
