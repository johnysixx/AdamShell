import unittest

from universe.big_bang import BigBang
from universe.big_bang_process_state import (
    BigBangProcessState,
)
from universe.universe import Universe


class BigBangProcessStateObjectStateTests(
    unittest.TestCase
):

    def test_process_starts_ready_as_enum(self):
        process = BigBang(Universe())

        self.assertIs(
            process.state,
            BigBangProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_begin_sets_in_progress_enum(self):
        process = BigBang(Universe())

        process.begin()

        self.assertIs(
            process.state,
            BigBangProcessState.IN_PROGRESS,
        )
        self.assertEqual(
            process.public_state["state"],
            "in_progress",
        )

    def test_complete_sets_completed_enum(self):
        process = BigBang(Universe())

        process.complete()

        self.assertIs(
            process.state,
            BigBangProcessState.COMPLETED,
        )
        self.assertEqual(
            process.public_state["state"],
            "completed",
        )

    def test_string_state_is_rejected(self):
        process = BigBang(Universe())

        with self.assertRaises(TypeError):
            process.state = "completed"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in BigBangProcessState
            },
            {
                "ready",
                "in_progress",
                "completed",
            },
        )


if __name__ == "__main__":
    unittest.main()
