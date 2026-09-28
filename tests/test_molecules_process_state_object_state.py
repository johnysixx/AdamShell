import unittest

from universe.molecules import Molecules
from universe.molecules_process_state import (
    MoleculesProcessState,
)
from universe.universe import Universe


class MoleculesProcessStateObjectStateTests(
    unittest.TestCase
):

    def test_process_starts_ready_as_enum(self):
        process = Molecules(Universe())

        self.assertIs(
            process.state,
            MoleculesProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_formation_sets_formed_enum(self):
        process = Molecules(Universe())

        result = process.form_reference_molecules()

        self.assertIs(
            process.state,
            MoleculesProcessState.FORMED,
        )
        self.assertEqual(
            result["state"],
            "formed",
        )

    def test_string_state_is_rejected(self):
        process = Molecules(Universe())

        with self.assertRaises(TypeError):
            process.state = "formed"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in MoleculesProcessState
            },
            {
                "ready",
                "formed",
            },
        )


if __name__ == "__main__":
    unittest.main()
