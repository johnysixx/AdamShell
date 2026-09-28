import unittest

from universe.isotopes import Isotopes
from universe.isotopes_process_state import (
    IsotopesProcessState,
)
from universe.universe import Universe


class IsotopesProcessStateObjectStateTests(
    unittest.TestCase
):

    def test_process_starts_ready_as_enum(self):
        process = Isotopes(Universe())

        self.assertIs(
            process.state,
            IsotopesProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_formation_sets_formed_enum(self):
        process = Isotopes(Universe())

        result = process.form_reference_isotopes()

        self.assertIs(
            process.state,
            IsotopesProcessState.FORMED,
        )
        self.assertEqual(
            result["state"],
            "formed",
        )

    def test_string_state_is_rejected(self):
        process = Isotopes(Universe())

        with self.assertRaises(TypeError):
            process.state = "formed"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in IsotopesProcessState
            },
            {
                "ready",
                "formed",
            },
        )


if __name__ == "__main__":
    unittest.main()
