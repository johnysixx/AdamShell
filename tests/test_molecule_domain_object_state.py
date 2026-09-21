import unittest

from universe.chemical_objects import ChemicalElement, ChemicalMolecule
from universe.molecules import Molecules
from universe.universe import Universe


class MoleculeDomainObjectStateTests(unittest.TestCase):

    def _assert_object_only(self, value, key):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(hasattr(value, mapping_method))

        with self.assertRaises(TypeError):
            _ = value[key]

    def _formed_molecules(self):
        universe = Universe()
        process = Molecules(universe)
        result = process.form_reference_molecules()
        return universe, process, result

    def test_registry_contains_molecule_objects(self):
        universe, process, _ = self._formed_molecules()

        water = process.molecules["water"]

        self.assertIsInstance(water, ChemicalMolecule)
        self._assert_object_only(water, "formula")
        self.assertEqual(water.formula, "H2O")
        self.assertEqual(water.category, "simple_molecule")
        self.assertEqual(water.atom_count, 3)
        self.assertEqual(water.component_count("hydrogen"), 2)
        self.assertEqual(water.component_count("oxygen"), 1)
        self.assertIs(
            universe.world["known_molecules"]["water"],
            water,
        )

    def test_molecule_components_compose_element_objects(self):
        universe, process, _ = self._formed_molecules()

        water = process.molecules["water"]
        components = list(water.components.items())

        self.assertTrue(components)
        self.assertTrue(
            all(
                isinstance(element, ChemicalElement)
                for element, _ in components
            )
        )

        hydrogen = universe.world["chemical_elements"]["hydrogen"]
        oxygen = universe.world["chemical_elements"]["oxygen"]

        self.assertEqual(water.components[hydrogen], 2)
        self.assertEqual(water.components[oxygen], 1)

    def test_component_registry_is_read_only(self):
        _, process, _ = self._formed_molecules()
        water = process.molecules["water"]
        hydrogen = next(iter(water.components))

        with self.assertRaises(TypeError):
            water.components[hydrogen] = 99

    def test_alcohol_is_molecule_object_with_functional_group(self):
        _, process, _ = self._formed_molecules()

        ethanol = process.molecules["ethanol"]

        self.assertIsInstance(ethanol, ChemicalMolecule)
        self.assertEqual(ethanol.category, "alcohol")
        self.assertEqual(ethanol.functional_group, "hydroxyl")
        self.assertEqual(ethanol.functional_group_symbol, "-OH")
        self.assertEqual(ethanol.component_count("carbon"), 2)
        self.assertEqual(ethanol.component_count("hydrogen"), 6)
        self.assertEqual(ethanol.component_count("oxygen"), 1)

    def test_molecule_rejects_legacy_element_dict_components(self):
        with self.assertRaises(TypeError):
            ChemicalMolecule(
                name="water",
                formula="H2O",
                components={
                    "hydrogen": 2,
                    "oxygen": 1,
                },
                category="simple_molecule",
                meaning="water molecule",
            )

    def test_public_boundary_serializes_molecule_objects(self):
        _, process, result = self._formed_molecules()

        public_water = result["molecules"]["water"]
        live_water = process.molecules["water"]

        self.assertIsInstance(public_water, dict)
        self.assertIsInstance(public_water["components"], dict)
        self.assertEqual(public_water["components"]["hydrogen"], 2)

        public_water["components"]["hydrogen"] = 99
        public_water["future_use"].append("changed")

        self.assertEqual(live_water.component_count("hydrogen"), 2)
        self.assertNotIn("changed", live_water.future_use)

    def test_to_dict_is_detached_boundary(self):
        hydrogen = ChemicalElement(
            name="hydrogen",
            symbol="H",
            atomic_number=1,
            official=True,
            discovered=True,
            state="recognized",
        )
        oxygen = ChemicalElement(
            name="oxygen",
            symbol="O",
            atomic_number=8,
            official=True,
            discovered=True,
            state="recognized",
        )
        molecule = ChemicalMolecule(
            name="water",
            formula="H2O",
            components={hydrogen: 2, oxygen: 1},
            category="simple_molecule",
            meaning="water molecule",
            future_use=("oceans",),
        )

        snapshot = molecule.to_dict()
        snapshot["components"]["hydrogen"] = 99
        snapshot["future_use"].append("changed")

        self.assertEqual(molecule.component_count("hydrogen"), 2)
        self.assertEqual(molecule.future_use, ("oceans",))


if __name__ == "__main__":
    unittest.main()
