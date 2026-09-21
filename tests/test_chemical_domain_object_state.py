import unittest

from universe.atoms import Atoms
from universe.chemical_objects import (
    ChemicalElement,
    Isotope,
    NeutralAtom,
)
from universe.isotopes import Isotopes
from universe.periodic_table import PeriodicTable
from universe.universe import Universe


class ChemicalDomainObjectStateTests(unittest.TestCase):

    def _assert_object_only(self, value, key):
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

    def test_periodic_table_registry_contains_element_objects(self):
        universe = Universe()
        table = PeriodicTable(universe)
        table.build_known_table()

        hydrogen = table.elements[1]

        self.assertIsInstance(
            hydrogen,
            ChemicalElement,
        )
        self._assert_object_only(
            hydrogen,
            "atomic_number",
        )
        self.assertEqual(hydrogen.name, "hydrogen")
        self.assertEqual(hydrogen.symbol, "H")
        self.assertEqual(hydrogen.atomic_number, 1)
        self.assertEqual(hydrogen.protons, 1)
        self.assertTrue(hydrogen.official)
        self.assertTrue(hydrogen.discovered)
        self.assertIs(
            universe.world["elements_by_atomic_number"][1],
            hydrogen,
        )
        self.assertIs(
            universe.world["chemical_elements"]["hydrogen"],
            hydrogen,
        )

    def test_future_element_is_object_and_cached(self):
        universe = Universe()
        table = PeriodicTable(universe)

        element = table.create_future_element(119)

        self.assertIsInstance(
            element,
            ChemicalElement,
        )
        self._assert_object_only(
            element,
            "temporary_systematic_name",
        )
        self.assertEqual(element.atomic_number, 119)
        self.assertFalse(element.official)
        self.assertFalse(element.discovered)
        self.assertTrue(
            element.temporary_systematic_name
        )
        self.assertIs(
            table.create_future_element(119),
            element,
        )

    def test_isotope_composes_element_object(self):
        universe = Universe()
        process = Isotopes(universe)
        process.form_reference_isotopes()

        isotope = process.isotopes["carbon_14"]
        element = process.periodic_table.elements[6]

        self.assertIsInstance(isotope, Isotope)
        self._assert_object_only(isotope, "mass_number")
        self.assertIs(isotope.element, element)
        self.assertEqual(isotope.element_name, "carbon")
        self.assertEqual(isotope.symbol, "C")
        self.assertEqual(isotope.protons, 6)
        self.assertEqual(isotope.neutrons, 8)
        self.assertEqual(
            isotope.electrons_if_neutral_atom,
            6,
        )

    def test_neutral_atom_composes_element_object(self):
        universe = Universe()
        process = Atoms(universe)
        process.form_reference_atoms()

        atom = process.atoms["hydrogen_atom"]
        element = process.periodic_table.elements[1]

        self.assertIsInstance(atom, NeutralAtom)
        self._assert_object_only(atom, "electrons")
        self.assertIs(atom.element, element)
        self.assertEqual(atom.protons, 1)
        self.assertEqual(atom.electrons, 1)
        self.assertEqual(atom.net_charge, 0)

    def test_isotope_and_atom_reject_legacy_element_dict(self):
        legacy_element = {
            "name": "hydrogen",
            "symbol": "H",
            "atomic_number": 1,
        }

        with self.assertRaises(TypeError):
            Isotope(
                element=legacy_element,
                mass_number=1,
                stability="stable",
            )

        with self.assertRaises(TypeError):
            NeutralAtom(element=legacy_element)

    def test_to_dict_snapshots_are_detached(self):
        element = ChemicalElement(
            name="hydrogen",
            symbol="H",
            atomic_number=1,
            official=True,
            discovered=True,
            state="recognized",
            future_use=("atoms", "isotopes"),
        )
        isotope = Isotope(
            element=element,
            mass_number=2,
            stability="stable",
            future_use=("heavy_water",),
        )
        atom = NeutralAtom(element=element)

        element_snapshot = element.to_dict()
        isotope_snapshot = isotope.to_dict()
        atom_snapshot = atom.to_dict()

        element_snapshot["future_use"].append("changed")
        isotope_snapshot["future_use"].append("changed")
        atom_snapshot["future_use"].append("changed")

        self.assertEqual(
            element.future_use,
            ("atoms", "isotopes"),
        )
        self.assertEqual(
            isotope.future_use,
            ("heavy_water",),
        )
        self.assertEqual(
            atom.future_use,
            ("isotopes", "molecules", "materials"),
        )

    def test_public_boundaries_serialize_domain_objects(self):
        universe = Universe()

        isotope_process = Isotopes(universe)
        isotope_result = (
            isotope_process.form_reference_isotopes()
        )

        atom_process = Atoms(universe)
        atom_result = atom_process.form_reference_atoms()

        self.assertIsInstance(
            isotope_result["isotopes"]["carbon_14"],
            dict,
        )
        self.assertIsInstance(
            atom_result["atoms"]["hydrogen_atom"],
            dict,
        )

        isotope_result["isotopes"]["carbon_14"][
            "state"
        ] = "changed"
        atom_result["atoms"]["hydrogen_atom"][
            "state"
        ] = "changed"

        self.assertEqual(
            isotope_process.isotopes["carbon_14"].state,
            "formed",
        )
        self.assertEqual(
            atom_process.atoms["hydrogen_atom"].state,
            "formed",
        )


if __name__ == "__main__":
    unittest.main()
