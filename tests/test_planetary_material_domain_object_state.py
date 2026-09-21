import unittest

from universe.planetary_material_objects import (
    AvailablePlanetaryMaterial,
    PlanetaryMaterial,
)
from universe.planetary_materials import PlanetaryMaterials
from universe.planet_state import PlanetFormationState
from universe.planets import Planets
from universe.universe import Universe


class PlanetaryMaterialDomainObjectStateTests(unittest.TestCase):

    def _assert_object_only(self, value, key):
        for mapping_method in ("get", "keys", "items", "values"):
            self.assertFalse(hasattr(value, mapping_method))

        with self.assertRaises(TypeError):
            _ = value[key]

    def test_planets_create_material_definition_objects(self):
        process = Planets(Universe())

        self.assertEqual(
            set(process.planetary_materials),
            {"water", "ice", "minerals", "organic_molecules"},
        )
        self.assertTrue(
            all(
                isinstance(material, PlanetaryMaterial)
                for material in process.planetary_materials.values()
            )
        )

        water = process.planetary_materials["water"]
        self._assert_object_only(water, "requires")
        self.assertEqual(water.state, "possible")
        self.assertEqual(water.requires, ("hydrogen", "oxygen"))

    def test_available_material_reuses_definition_object(self):
        definition = PlanetaryMaterial(
            name="water",
            requires=("hydrogen", "oxygen"),
        )

        available = definition.make_available(
            origin="earth_planetary_materialization"
        )

        self.assertIsInstance(available, AvailablePlanetaryMaterial)
        self.assertIs(available.material, definition)
        self.assertEqual(available.name, definition.name)
        self.assertEqual(available.type, definition.type)
        self.assertEqual(available.requires, definition.requires)
        self.assertEqual(available.state, "available")
        self._assert_object_only(available, "state")

    def test_materialization_preserves_definition_identity(self):
        universe = Universe()
        definitions = Planets(universe).planetary_materials
        universe.world["planetary_materials"] = definitions
        universe.world["planetary_state"] = PlanetFormationState(
            earth_formed=True,
            water_possible=True,
            ice_possible=True,
            minerals_possible=True,
            organic_molecules_possible=True,
        )

        process = PlanetaryMaterials(universe)
        process.materialize()

        for name, available in process.available_materials.items():
            self.assertIs(available.material, definitions[name])

    def test_legacy_definition_dict_is_rejected(self):
        universe = Universe()
        universe.world["planetary_state"] = PlanetFormationState(
            earth_formed=True,
            water_possible=True,
        )
        universe.world["planetary_materials"] = {
            "water": {
                "name": "water",
                "requires": ["hydrogen", "oxygen"],
            }
        }
        process = PlanetaryMaterials(universe)

        with self.assertRaises(TypeError):
            process._materialize_unprotected()

    def test_to_dict_snapshots_are_detached(self):
        definition = PlanetaryMaterial(
            name="water",
            requires=("hydrogen", "oxygen"),
        )
        available = definition.make_available(
            origin="earth_planetary_materialization"
        )

        definition_snapshot = definition.to_dict()
        available_snapshot = available.to_dict()
        definition_snapshot["requires"].append("fake")
        available_snapshot["requires"].append("fake")

        self.assertEqual(definition.requires, ("hydrogen", "oxygen"))
        self.assertEqual(available.requires, ("hydrogen", "oxygen"))


if __name__ == "__main__":
    unittest.main()
