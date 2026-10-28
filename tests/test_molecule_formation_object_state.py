import unittest

from universe.chemical_objects import ChemicalMolecule
from universe.molecule_state import MoleculeFormationState
from universe.molecules import Molecules
from universe.physical_formation_result_state import (
    MoleculeFormationResult,
)
from universe.universe import Universe


class MoleculeFormationObjectStateTests(
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
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def _formed_molecules(self):
        universe = Universe()
        process = Molecules(universe)
        result = process.form_reference_molecules()

        return universe, process, result

    def test_molecule_state_is_object_only(self):
        state = MoleculeFormationState()

        self._assert_object_only(
            state,
            "molecule_count",
        )

    def test_initial_values_are_preserved(self):
        state = MoleculeFormationState()

        self.assertFalse(
            state.periodic_table_available
        )
        self.assertFalse(
            state.simple_molecules_available
        )
        self.assertFalse(
            state.organic_molecules_available
        )
        self.assertFalse(state.alcohols_available)
        self.assertEqual(state.molecule_count, 0)

    def test_formation_mutates_same_state_object(
        self
    ):
        universe = Universe()
        process = Molecules(universe)
        state = process.molecule_state

        process.form_reference_molecules()

        self.assertIs(process.molecule_state, state)
        self.assertTrue(
            state.periodic_table_available
        )
        self.assertTrue(
            state.simple_molecules_available
        )
        self.assertTrue(
            state.organic_molecules_available
        )
        self.assertTrue(state.alcohols_available)
        self.assertEqual(state.molecule_count, 6)

    def test_world_keeps_snapshot_without_live_molecule_registries(
        self
    ):
        universe, process, _ = (
            self._formed_molecules()
        )

        state = process.molecule_state

        self.assertNotIn(
            "molecule_state",
            universe.world,
        )
        self.assertIsInstance(
            state,
            MoleculeFormationState,
        )
        self.assertIs(
            process.result.molecule_state,
            state,
        )
        self.assertIsInstance(
            universe.world["molecules"],
            dict,
        )
        self.assertIsInstance(
            universe.world["molecules"][
                "molecule_state"
            ],
            dict,
        )
        self.assertEqual(
            universe.world["molecules"][
                "molecule_state"
            ]["molecule_count"],
            len(process.molecules),
        )
        self.assertEqual(
            set(
                universe.world["molecules"][
                    "molecules"
                ]
            ),
            set(process.molecules),
        )
        self.assertNotIn(
            "known_molecules",
            universe.world,
        )
        self.assertIsInstance(universe.world, dict)

        universe.world["molecules"][
            "molecule_state"
        ]["molecule_count"] = 99

        self.assertEqual(
            state.molecule_count,
            6,
        )

    def test_runtime_result_is_object_and_snapshot_is_dict(
        self
    ):
        universe, process, result = self._formed_molecules()

        self.assertIsInstance(
            result,
            MoleculeFormationResult,
        )
        self._assert_object_only(
            result,
            "state",
        )
        self.assertIs(
            result.molecule_state,
            process.molecule_state,
        )
        expected = {
            "water": {
                "hydrogen": 2,
                "oxygen": 1,
            },
            "carbon_dioxide": {
                "carbon": 1,
                "oxygen": 2,
            },
            "methane": {
                "carbon": 1,
                "hydrogen": 4,
            },
            "ammonia": {
                "nitrogen": 1,
                "hydrogen": 3,
            },
            "methanol": {
                "carbon": 1,
                "hydrogen": 4,
                "oxygen": 1,
            },
            "ethanol": {
                "carbon": 2,
                "hydrogen": 6,
                "oxygen": 1,
            },
        }

        self.assertEqual(
            set(process.molecules),
            set(expected),
        )
        self.assertEqual(
            set(result.molecules),
            set(expected),
        )

        public_molecules = universe.world[
            "molecules"
        ]["molecules"]

        self.assertEqual(
            set(public_molecules),
            set(expected),
        )

        for name, components in expected.items():
            with self.subTest(molecule=name):
                molecule = process.molecules[name]

                self.assertIsInstance(
                    molecule,
                    ChemicalMolecule,
                )
                self.assertIs(
                    result.molecules[name],
                    molecule,
                )

                self.assertEqual(
                    {
                        element.name: count
                        for element, count
                        in molecule.components.items()
                    },
                    components,
                )

                for element in molecule.components:
                    self.assertIs(
                        element,
                        process.periodic_table.elements[
                            element.atomic_number
                        ],
                    )

                self.assertIsInstance(
                    public_molecules[name],
                    dict,
                )
                self.assertEqual(
                    public_molecules[name],
                    molecule.to_dict(),
                )

        # The public world snapshot must not mutate
        # the canonical ChemicalMolecule objects.

        public_molecules["water"]["components"][
            "hydrogen"
        ] = 99

        self.assertEqual(
            process.molecules[
                "water"
            ].component_count("hydrogen"),
            2,
        )

        self.assertEqual(
            result.to_dict()["molecules"][
                "water"
            ]["components"]["hydrogen"],
            2,
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot["molecule_state"],
            dict,
        )
        self.assertIsInstance(
            snapshot["molecules"],
            dict,
        )
        self.assertEqual(
            snapshot["molecule_state"][
                "molecule_count"
            ],
            6,
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = (
            self._formed_molecules()
        )

        snapshot = result.to_dict()

        snapshot["molecule_state"][
            "molecule_count"
        ] = 99
        snapshot["molecules"]["water"][
            "components"
        ]["hydrogen"] = 99

        self.assertEqual(
            process.molecule_state.molecule_count,
            6,
        )
        self.assertEqual(
            process.molecules["water"].component_count(
                "hydrogen"
            ),
            2,
        )

    def test_formation_error_creates_cronenberg(
        self
    ):
        universe = Universe()
        process = Molecules(universe)

        def broken_molecule(*args, **kwargs):
            raise RuntimeError(
                "molecule formation exploded"
            )

        process.create_molecule = broken_molecule

        result = process.form_reference_molecules()
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
            "molecules",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "form_reference_molecules",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "molecule formation exploded",
        )

    def test_to_dict_is_detached_boundary(self):
        state = MoleculeFormationState()
        state.molecule_count = 6

        snapshot = state.to_dict()
        snapshot["molecule_count"] = 99

        self.assertEqual(state.molecule_count, 6)


if __name__ == "__main__":
    unittest.main()
