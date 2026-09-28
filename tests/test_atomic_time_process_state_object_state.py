import unittest

from universe.atomic_time import AtomicTime
from universe.atomic_time_process_state import (
    AtomicTimeProcessState,
)
from universe.universe import Universe


class AtomicTimeProcessStateObjectStateTests(
    unittest.TestCase
):

    def test_process_starts_ready_as_enum(self):
        process = AtomicTime(Universe())

        self.assertIs(
            process.state,
            AtomicTimeProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_definition_sets_defined_enum(self):
        process = AtomicTime(Universe())

        result = process.define_si_second()

        self.assertIs(
            process.state,
            AtomicTimeProcessState.DEFINED,
        )
        self.assertEqual(
            result["state"],
            "defined",
        )

    def test_missing_caesium_sets_failed_enum(self):
        process = AtomicTime(Universe())
        process.ensure_isotopes = lambda: None

        result = process.define_si_second()

        self.assertIs(
            process.state,
            AtomicTimeProcessState.FAILED,
        )
        self.assertEqual(
            result["state"],
            "failed",
        )

    def test_string_state_is_rejected(self):
        process = AtomicTime(Universe())

        with self.assertRaises(TypeError):
            process.state = "defined"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in AtomicTimeProcessState
            },
            {
                "ready",
                "defined",
                "failed",
            },
        )


if __name__ == "__main__":
    unittest.main()
