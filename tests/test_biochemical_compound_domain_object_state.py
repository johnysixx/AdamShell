import unittest

from universe.biochemical_foundations import BiochemicalFoundations
from universe.biochemical_objects import BiochemicalCompound
from universe.planetary_material_objects import PlanetaryMaterial
from universe.universe import Universe


class BiochemicalCompoundDomainObjectStateTests(unittest.TestCase):

    def _formed_process(self):
        universe = Universe()
        water = PlanetaryMaterial(
            name="water",
            requires=("hydrogen", "oxygen"),
        )
        organic_molecules = PlanetaryMaterial(
            name="organic_molecules",
            requires=("carbon", "hydrogen", "oxygen", "nitrogen"),
        )
        universe.world["available_planetary_materials"] = {
            "water": water.make_available(origin="test"),
            "organic_molecules": organic_molecules.make_available(
                origin="test"
            ),
        }
        process = BiochemicalFoundations(universe)
        result = process.form_biochemical_foundations()
        return universe, process, result

    def test_registry_values_are_compound_objects(self):
        universe, process, _ = self._formed_process()

        self.assertIs(
            universe.world["biochemical_compounds"],
            process.compounds,
        )
        self.assertIsInstance(process.compounds, dict)
        self.assertTrue(
            all(
                isinstance(compound, BiochemicalCompound)
                for compound in process.compounds.values()
            )
        )

    def test_compound_is_object_only(self):
        _, process, _ = self._formed_process()
        sugars = process.compounds["sugars"]

        for mapping_method in ("get", "keys", "items", "values"):
            self.assertFalse(hasattr(sugars, mapping_method))

        with self.assertRaises(TypeError):
            _ = sugars["requires"]

    def test_compound_sequences_are_immutable_tuples(self):
        _, process, _ = self._formed_process()
        sugars = process.compounds["sugars"]

        self.assertEqual(
            sugars.requires,
            (
                "water",
                "organic_molecules",
                "carbon",
                "hydrogen",
                "oxygen",
            ),
        )
        self.assertIsInstance(sugars.requires, tuple)
        self.assertIsInstance(sugars.future_use, tuple)

        with self.assertRaises(AttributeError):
            sugars.requires.append("legacy")

    def test_compound_attributes_expose_domain_state(self):
        _, process, _ = self._formed_process()
        substrate = process.compounds["fermentation_substrate"]

        self.assertEqual(substrate.name, "fermentation_substrate")
        self.assertEqual(substrate.type, "biochemical_process_material")
        self.assertEqual(substrate.state, "possible")
        self.assertEqual(substrate.origin, "planetary_biochemistry")
        self.assertEqual(substrate.requires, ("sugars", "water", "time"))

    def test_public_snapshot_is_detached_dict_boundary(self):
        _, process, result = self._formed_process()

        snapshot = result["compounds"]["sugars"]
        self.assertIsInstance(snapshot, dict)
        self.assertIsInstance(snapshot["requires"], list)
        snapshot["requires"].append("fake_material")
        snapshot["name"] = "fake_sugars"

        sugars = process.compounds["sugars"]
        self.assertEqual(sugars.name, "sugars")
        self.assertNotIn("fake_material", sugars.requires)

    def test_constructor_rejects_invalid_requirement_entries(self):
        with self.assertRaises(TypeError):
            BiochemicalCompound(
                name="legacy",
                compound_type="biochemical_compound",
                requires=("water", {"legacy": True}),
            )


if __name__ == "__main__":
    unittest.main()
