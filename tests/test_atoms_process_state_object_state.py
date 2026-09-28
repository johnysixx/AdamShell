import unittest

from universe.atoms import Atoms
from universe.atoms_process_state import (
    AtomsProcessState,
)
from universe.universe import Universe


class AtomsProcessStateObjectStateTests(
    unittest.TestCase
):

    def test_process_starts_ready_as_enum(self):
        process = Atoms(Universe())

        self.assertIs(
            process.state,
            AtomsProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_formation_sets_formed_enum(self):
        process = Atoms(Universe())

        result = process.form_reference_atoms()

        self.assertIs(
            process.state,
            AtomsProcessState.FORMED,
        )
        self.assertEqual(
            result["state"],
            "formed",
        )

    def test_string_state_is_rejected(self):
        process = Atoms(Universe())

        with self.assertRaises(TypeError):
            process.state = "formed"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in AtomsProcessState
            },
            {
                "ready",
                "formed",
            },
        )


if __name__ == "__main__":
    unittest.main()
