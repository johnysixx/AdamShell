import unittest

from universe.periodic_table import PeriodicTable
from universe.periodic_table_process_state import (
    PeriodicTableProcessState,
)
from universe.universe import Universe


class PeriodicTableProcessStateObjectStateTests(
    unittest.TestCase
):

    def test_process_starts_ready_as_enum(self):
        process = PeriodicTable(Universe())

        self.assertIs(
            process.state,
            PeriodicTableProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_build_sets_registered_enum(self):
        process = PeriodicTable(Universe())

        result = process.build_known_table()

        self.assertIs(
            process.state,
            PeriodicTableProcessState.REGISTERED,
        )
        self.assertEqual(
            result["state"],
            "registered",
        )

    def test_string_state_is_rejected(self):
        process = PeriodicTable(Universe())

        with self.assertRaises(TypeError):
            process.state = "registered"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in PeriodicTableProcessState
            },
            {
                "ready",
                "registered",
            },
        )


if __name__ == "__main__":
    unittest.main()
