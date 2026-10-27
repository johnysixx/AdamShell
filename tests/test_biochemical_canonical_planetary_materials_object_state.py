import unittest

from universe.biochemical_foundations import (
    BiochemicalFoundations,
)
from universe.biochemical_foundations_process_state import (
    BiochemicalFoundationsProcessState,
)
from universe.biochemical_objects import BiochemicalCompound
from universe.cosmic_objects import StellarMaterialCloud
from universe.planets import Planets
from universe.planets_process_state import PlanetsProcessState
from universe.planetary_materials import PlanetaryMaterials
from universe.planetary_material_objects import (
    AvailablePlanetaryMaterial,
)
from universe.planetary_materials_process_state import (
    PlanetaryMaterialsProcessState,
)
from universe.stellar_systems import StellarSystems
from universe.stellar_systems_process_state import (
    StellarSystemsProcessState,
)
from universe.supernova_enrichment import SupernovaEnrichment
from universe.universe import Universe


class BiochemicalCanonicalPlanetaryMaterialsTests(
    unittest.TestCase
):

    def _materialized_chain(self):
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
            name="biochemical_source_cloud",
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

        self.assertIs(
            systems.form_stellar_systems().state,
            StellarSystemsProcessState.FORMED,
        )

        planets = Planets(universe)

        self.assertIs(
            planets.form_planets().state,
            PlanetsProcessState.FORMED,
        )

        materials = PlanetaryMaterials(universe)

        self.assertIs(
            materials.materialize().state,
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

        return universe, planets, materials

    def test_biochemical_layer_registration(self):
        universe = Universe()

        self.assertFalse(
            hasattr(
                universe,
                "biochemical_foundations_layer",
            )
        )

        process = BiochemicalFoundations(universe)

        self.assertIs(
            universe.biochemical_foundations_layer,
            process,
        )

        self.assertEqual(process.compounds, {})

    def test_complete_canonical_biochemical_chain(self):
        universe, planets, materials = (
            self._materialized_chain()
        )

        process = BiochemicalFoundations(universe)
        result = process.form_biochemical_foundations()

        self.assertIs(
            result.state,
            BiochemicalFoundationsProcessState.FORMED,
        )

        self.assertEqual(
            set(process.compounds),
            {
                "sugars",
                "amino_acids",
                "lipids",
                "fermentation_substrate",
            },
        )

        self.assertIs(
            universe.biochemical_foundations_layer,
            process,
        )

        self.assertIs(
            universe.planetary_materials_layer,
            materials,
        )

        self.assertIs(
            universe.planets_layer,
            planets,
        )

        self.assertIs(
            universe.world["biochemical_compounds"],
            process.compounds,
        )

        for name in process.compounds:
            with self.subTest(compound=name):
                self.assertIsInstance(
                    process.compounds[name],
                    BiochemicalCompound,
                )

                self.assertIs(
                    result.compounds[name],
                    process.compounds[name],
                )

        self.assertIs(
            materials.available_materials["water"].material,
            planets.planetary_materials["water"],
        )

        self.assertTrue(
            process.biochemical_state.sugars_possible
        )

        self.assertTrue(
            process.biochemical_state.amino_acids_possible
        )

        self.assertTrue(
            process.biochemical_state.lipids_possible
        )

        self.assertTrue(
            process.biochemical_state
            .fermentation_substrate_possible
        )

    def test_public_decoys_cannot_override_materials(
        self
    ):
        universe, _, materials = self._materialized_chain()

        universe.world["available_planetary_materials"] = {
            "water": {
                "name": "legacy_water",
            },
        }

        process = BiochemicalFoundations(universe)
        result = process.form_biochemical_foundations()

        self.assertIs(
            result.state,
            BiochemicalFoundationsProcessState.FORMED,
        )

        self.assertIsInstance(
            materials.available_materials["water"],
            AvailablePlanetaryMaterial,
        )

        self.assertIn("sugars", process.compounds)

    def test_missing_public_alias_does_not_block(
        self
    ):
        universe, _, materials = self._materialized_chain()

        self.assertNotIn(
            "available_planetary_materials",
            universe.world,
        )

        process = BiochemicalFoundations(universe)
        result = process.form_biochemical_foundations()

        self.assertIs(
            result.state,
            BiochemicalFoundationsProcessState.FORMED,
        )

        self.assertIn(
            "organic_molecules",
            materials.available_materials,
        )

        self.assertIn(
            "fermentation_substrate",
            process.compounds,
        )

    def test_world_only_materials_cannot_start_biochemistry(
        self
    ):
        universe = Universe()

        universe.world["available_planetary_materials"] = {
            "water": object(),
            "organic_molecules": object(),
        }

        process = BiochemicalFoundations(universe)
        result = process.form_biochemical_foundations()

        self.assertIs(
            result.state,
            BiochemicalFoundationsProcessState.FAILED,
        )

        self.assertEqual(process.compounds, {})

        self.assertFalse(
            process.biochemical_state.sugars_possible
        )

    def test_missing_canonical_organic_material_fails(
        self
    ):
        universe, _, materials = self._materialized_chain()

        # Deliberately inject a detached world decoy.
        # The canonical materials layer does not publish
        # this runtime collection into Universe.world.
        universe.world["available_planetary_materials"] = dict(
            materials.available_materials
        )

        self.assertIsNot(
            universe.world["available_planetary_materials"],
            materials.available_materials,
        )

        materials.available_materials.pop(
            "organic_molecules"
        )

        self.assertIn(
            "organic_molecules",
            universe.world["available_planetary_materials"],
        )

        process = BiochemicalFoundations(universe)
        result = process.form_biochemical_foundations()

        self.assertIs(
            result.state,
            BiochemicalFoundationsProcessState.FAILED,
        )

        self.assertEqual(process.compounds, {})

    def test_invalid_canonical_material_creates_cronenberg(
        self
    ):
        universe, _, materials = self._materialized_chain()

        materials.available_materials["water"] = {
            "name": "legacy_water",
        }

        process = BiochemicalFoundations(universe)
        result = process.form_biochemical_foundations()

        self.assertEqual(
            result.type,
            "quantum_error",
        )

        self.assertIn(
            "AvailablePlanetaryMaterial",
            result.cronenberg.origin.error_message,
        )

        self.assertEqual(
            result.cronenberg.origin.source_component,
            "biochemical_foundations",
        )

        self.assertEqual(
            result.cronenberg.origin.source_operation,
            "form_biochemical_foundations",
        )

    def test_no_public_material_reads_during_biochemistry(
        self
    ):
        class GuardedWorld(dict):

            def get(self, key, default=None):
                if key == "available_planetary_materials":
                    raise AssertionError(
                        "Biochemistry read public materials"
                    )

                return super().get(key, default)

            def __getitem__(self, key):
                if key == "available_planetary_materials":
                    raise AssertionError(
                        "Biochemistry indexed public materials"
                    )

                return super().__getitem__(key)

        universe, planets, materials = (
            self._materialized_chain()
        )

        universe.world = GuardedWorld(
            universe.world
        )

        process = BiochemicalFoundations(universe)
        result = process.form_biochemical_foundations()

        self.assertIs(
            result.state,
            BiochemicalFoundationsProcessState.FORMED,
        )

        self.assertIs(
            universe.planetary_materials_layer,
            materials,
        )

        self.assertIs(
            universe.planets_layer,
            planets,
        )

        self.assertIs(
            result.compounds["sugars"],
            process.compounds["sugars"],
        )

        self.assertIn(
            "fermentation_substrate",
            process.compounds,
        )


if __name__ == "__main__":
    unittest.main()
