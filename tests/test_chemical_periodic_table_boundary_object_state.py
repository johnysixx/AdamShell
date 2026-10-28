import unittest

from unittest.mock import Mock

from universe.atoms import Atoms
from universe.isotopes import Isotopes
from universe.molecules import Molecules
from universe.chemical_objects import ChemicalElement
from universe.universe import Universe


class ChemicalPeriodicTableBoundaryObjectStateTests(
    unittest.TestCase
):

    def test_atoms_build_own_table_despite_world_decoy(
        self
    ):
        universe = Universe()

        universe.world["elements_by_atomic_number"] = {
            1: "legacy_hydrogen",
        }

        process = Atoms(universe)

        process.ensure_periodic_table()

        self.assertEqual(
            len(process.periodic_table.elements),
            118,
        )

        self.assertTrue(
            process.atom_state.periodic_table_available
        )

        self.assertIs(
            universe.world["elements_by_atomic_number"],
            process.periodic_table.elements,
        )

        hydrogen = process.create_neutral_atom(1)

        self.assertIs(
            hydrogen.element,
            process.periodic_table.elements[1],
        )

    def test_isotopes_build_own_table_despite_world_decoy(
        self
    ):
        universe = Universe()

        universe.world["elements_by_atomic_number"] = {
            6: "legacy_carbon",
        }

        process = Isotopes(universe)

        process.ensure_periodic_table()

        self.assertEqual(
            len(process.periodic_table.elements),
            118,
        )

        self.assertTrue(
            process.isotope_state.periodic_table_available
        )

        isotope = process.create_isotope(
            atomic_number=6,
            mass_number=14,
            stability="radioactive",
            future_use=("radiocarbon_dating",),
        )

        self.assertIs(
            isotope.element,
            process.periodic_table.elements[6],
        )

    def test_molecules_build_own_table_despite_world_decoy(
        self
    ):
        universe = Universe()

        universe.world["elements_by_atomic_number"] = {
            8: "legacy_oxygen",
        }

        process = Molecules(universe)

        process.ensure_periodic_table()

        self.assertEqual(
            len(process.periodic_table.elements),
            118,
        )

        self.assertTrue(
            process.molecule_state.periodic_table_available
        )

        self.assertIs(
            universe.world["elements_by_atomic_number"],
            process.periodic_table.elements,
        )

    def test_molecule_components_ignore_world_decoy(
        self
    ):
        universe = Universe()
        process = Molecules(universe)

        process.ensure_periodic_table()

        hydrogen = process.periodic_table.elements[1]
        oxygen = process.periodic_table.elements[8]

        hydrogen_decoy = object()
        oxygen_decoy = object()

        universe.world["chemical_elements"] = {
            "hydrogen": hydrogen_decoy,
            "oxygen": oxygen_decoy,
        }

        molecule = process.create_molecule(
            name="water_test",
            formula="H2O",
            components={
                "hydrogen": 2,
                "oxygen": 1,
            },
            category="simple_molecule",
            meaning="test water molecule",
            future_use=(),
        )

        self.assertIsInstance(
            hydrogen,
            ChemicalElement,
        )

        self.assertIsInstance(
            oxygen,
            ChemicalElement,
        )

        self.assertEqual(
            molecule.components[hydrogen],
            2,
        )

        self.assertEqual(
            molecule.components[oxygen],
            1,
        )

        self.assertEqual(
            molecule.component_count("hydrogen"),
            2,
        )

        self.assertIs(
            universe.world["chemical_elements"][
                "hydrogen"
            ],
            hydrogen_decoy,
        )
        self.assertIs(
            universe.world["chemical_elements"][
                "oxygen"
            ],
            oxygen_decoy,
        )

    def test_direct_molecule_creation_initializes_own_table(
        self
    ):
        universe = Universe()
        process = Molecules(universe)

        self.assertEqual(
            process.periodic_table.elements,
            {},
        )

        molecule = process.create_molecule(
            name="direct_water",
            formula="H2O",
            components={
                "hydrogen": 2,
                "oxygen": 1,
            },
            category="simple_molecule",
            meaning="direct formation test",
            future_use=(),
        )

        self.assertEqual(
            len(process.periodic_table.elements),
            118,
        )

        self.assertTrue(
            process.molecule_state.periodic_table_available
        )

        self.assertEqual(
            molecule.component_count("oxygen"),
            1,
        )

    def test_missing_element_still_raises_value_error(
        self
    ):
        process = Molecules(Universe())

        with self.assertRaisesRegex(
            ValueError,
            "Missing element for molecule: unknownium",
        ):
            process.resolve_elements({
                "unknownium": 1,
            })

    def test_local_table_is_not_rebuilt_when_ready(
        self
    ):
        universe = Universe()
        process = Atoms(universe)

        process.ensure_periodic_table()

        original = process.periodic_table.elements
        hydrogen = original[1]

        process.periodic_table.build_known_table = Mock(
            side_effect=AssertionError(
                "Already prepared table must not rebuild"
            )
        )

        universe.world["elements_by_atomic_number"] = {}

        process.ensure_periodic_table()

        self.assertIs(
            process.periodic_table.elements,
            original,
        )

        self.assertIs(
            process.periodic_table.elements[1],
            hydrogen,
        )

        process.periodic_table.build_known_table.assert_not_called()

    def test_readiness_and_resolution_do_not_read_world_get(
        self
    ):
        class GuardedWorld(dict):

            def get(self, key, default=None):
                if key in (
                    "elements_by_atomic_number",
                    "chemical_elements",
                ):
                    raise AssertionError(
                        "Chemical runtime cannot read "
                        "public element registries"
                    )

                return super().get(key, default)

        universe = Universe()
        universe.world = GuardedWorld(universe.world)

        process = Molecules(universe)

        process.ensure_periodic_table()

        molecule = process.create_molecule(
            name="guarded_water",
            formula="H2O",
            components={
                "hydrogen": 2,
                "oxygen": 1,
            },
            category="simple_molecule",
            meaning="guarded registry test",
            future_use=(),
        )

        self.assertEqual(
            molecule.component_count("hydrogen"),
            2,
        )

        self.assertEqual(
            molecule.component_count("oxygen"),
            1,
        )

        self.assertIs(
            universe.world["elements_by_atomic_number"],
            process.periodic_table.elements,
        )

        self.assertNotIn(
            "chemical_elements",
            universe.world,
        )

        hydrogen = next(
            element
            for element in molecule.components
            if element.name == "hydrogen"
        )

        oxygen = next(
            element
            for element in molecule.components
            if element.name == "oxygen"
        )

        self.assertIs(
            hydrogen,
            process.periodic_table.elements[1],
        )
        self.assertIs(
            oxygen,
            process.periodic_table.elements[8],
        )


if __name__ == "__main__":
    unittest.main()
