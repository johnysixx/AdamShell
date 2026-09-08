import unittest

from universe.molecule_state import MoleculeFormationState
from universe.molecules import Molecules
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

    def test_world_registry_stores_state_object(
        self
    ):
        universe, process, _ = (
            self._formed_molecules()
        )

        state = universe.world["molecule_state"]
        self.assertIsInstance(
            state,
            MoleculeFormationState,
        )
        self.assertIs(state, process.molecule_state)
        self.assertIsInstance(
            universe.world["known_molecules"],
            dict,
        )
        self.assertIsInstance(universe.world, dict)

    def test_public_result_remains_dict_boundary(
        self
    ):
        _, _, result = self._formed_molecules()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["molecule_state"],
            dict,
        )
        self.assertIsInstance(
            result["molecules"],
            dict,
        )
        self.assertEqual(
            result["molecule_state"][
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

        result["molecule_state"][
            "molecule_count"
        ] = 99
        result["molecules"]["water"][
            "components"
        ]["hydrogen"] = 99

        self.assertEqual(
            process.molecule_state.molecule_count,
            6,
        )
        self.assertEqual(
            process.molecules["water"][
                "components"
            ]["hydrogen"],
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
