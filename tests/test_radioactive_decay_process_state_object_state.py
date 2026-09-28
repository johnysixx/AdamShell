import unittest

from universe.radioactive_decay import RadioactiveDecay
from universe.radioactive_decay_process_state import (
    RadioactiveDecayProcessState,
)
from universe.universe import Universe


class RadioactiveDecayProcessStateObjectStateTests(
    unittest.TestCase
):

    def test_process_starts_ready_as_enum(self):
        process = RadioactiveDecay(Universe())

        self.assertIs(
            process.state,
            RadioactiveDecayProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_definition_sets_defined_enum(self):
        process = RadioactiveDecay(Universe())

        result = process.define_reference_decay()

        self.assertIs(
            process.state,
            RadioactiveDecayProcessState.DEFINED,
        )
        self.assertEqual(
            result["state"],
            "defined",
        )

    def test_string_state_is_rejected(self):
        process = RadioactiveDecay(Universe())

        with self.assertRaises(TypeError):
            process.state = "defined"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state
                in RadioactiveDecayProcessState
            },
            {
                "ready",
                "defined",
            },
        )


if __name__ == "__main__":
    unittest.main()
