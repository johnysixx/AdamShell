import unittest

from universe.atom_state import AtomFormationState
from universe.chemical_objects import NeutralAtom
from universe.atoms import Atoms
from universe.universe import Universe


class AtomFormationObjectStateTests(
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

    def _formed_atoms(self):
        universe = Universe()
        process = Atoms(universe)
        result = process.form_reference_atoms()

        return universe, process, result

    def test_atom_state_is_object_only(self):
        state = AtomFormationState()

        self._assert_object_only(
            state,
            "atom_count",
        )

    def test_initial_values_are_preserved(self):
        state = AtomFormationState()

        self.assertFalse(
            state.periodic_table_available
        )
        self.assertFalse(
            state.neutral_atoms_available
        )
        self.assertEqual(state.atom_count, 0)

    def test_formation_mutates_same_state_object(
        self
    ):
        universe = Universe()
        process = Atoms(universe)
        state = process.atom_state

        process.form_reference_atoms()

        self.assertIs(process.atom_state, state)
        self.assertTrue(
            state.periodic_table_available
        )
        self.assertTrue(
            state.neutral_atoms_available
        )
        self.assertEqual(state.atom_count, 4)

    def test_world_registry_stores_state_object(
        self
    ):
        universe, process, _ = self._formed_atoms()

        state = universe.world["atom_state"]
        self.assertIsInstance(
            state,
            AtomFormationState,
        )
        self.assertIs(state, process.atom_state)
        self.assertIsInstance(universe.world, dict)

    def test_public_result_remains_dict_boundary(
        self
    ):
        _, _, result = self._formed_atoms()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["atom_state"],
            dict,
        )
        self.assertIsInstance(result["atoms"], dict)
        self.assertEqual(
            result["atom_state"]["atom_count"],
            4,
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = self._formed_atoms()

        result["atom_state"]["atom_count"] = 99
        result["atoms"]["hydrogen_atom"][
            "state"
        ] = "changed"

        self.assertEqual(process.atom_state.atom_count, 4)
        self.assertEqual(
            process.atoms["hydrogen_atom"].state,
            "formed",
        )

    def test_formation_error_creates_cronenberg(
        self
    ):
        universe = Universe()
        process = Atoms(universe)

        def broken_atom(atomic_number):
            raise RuntimeError(
                "atom formation exploded"
            )

        process.create_neutral_atom = broken_atom

        result = process.form_reference_atoms()
        cronenberg = result["cronenberg"]

        self.assertEqual(
            result["type"],
            "quantum_error",
        )
        self.assertIn(
            cronenberg,
            universe.cronenbergs,
        )
        self.assertEqual(
            cronenberg.origin.source_component,
            "atoms",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "form_reference_atoms",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "atom formation exploded",
        )

    def test_to_dict_is_detached_boundary(self):
        state = AtomFormationState()
        state.atom_count = 4

        snapshot = state.to_dict()
        snapshot["atom_count"] = 99

        self.assertEqual(state.atom_count, 4)


if __name__ == "__main__":
    unittest.main()
