import unittest

from universe.energy_gate import EnergyGate
from universe.energy_gate_process_state import (
    EnergyGateProcessState,
)
from universe.universe import Universe


class EnergyGateProcessStateObjectStateTests(
    unittest.TestCase
):

    def test_gate_starts_closed_as_enum(self):
        gate = EnergyGate(
            Universe(),
            threshold_j=10.0,
        )

        self.assertIs(
            gate.state,
            EnergyGateProcessState.CLOSED,
        )
        self.assertEqual(
            gate.public_state["state"],
            "closed",
        )

    def test_below_threshold_stays_closed_enum(self):
        gate = EnergyGate(
            Universe(),
            threshold_j=10.0,
        )

        result = gate.collect_energy(
            "idea",
            4.0,
        )

        self.assertIs(
            gate.state,
            EnergyGateProcessState.CLOSED,
        )
        self.assertEqual(
            result["state"],
            "closed",
        )

    def test_threshold_opens_gate_as_enum(self):
        gate = EnergyGate(
            Universe(),
            threshold_j=10.0,
        )

        result = gate.collect_energy(
            "idea",
            10.0,
        )

        self.assertIs(
            gate.state,
            EnergyGateProcessState.OPEN,
        )
        self.assertEqual(
            result["state"],
            "open",
        )

    def test_gate_can_close_again_below_threshold(self):
        gate = EnergyGate(
            Universe(),
            threshold_j=10.0,
        )
        gate.collect_energy("idea", 10.0)

        gate.idea_energy_j = 5.0
        gate.update_state()

        self.assertIs(
            gate.state,
            EnergyGateProcessState.CLOSED,
        )
        self.assertEqual(
            gate.public_state["state"],
            "closed",
        )

    def test_string_state_is_rejected(self):
        gate = EnergyGate(
            Universe(),
            threshold_j=10.0,
        )

        with self.assertRaises(TypeError):
            gate.state = "open"

    def test_state_values_define_boundary_names(self):
        self.assertEqual(
            {
                state.value
                for state in EnergyGateProcessState
            },
            {
                "closed",
                "open",
            },
        )


if __name__ == "__main__":
    unittest.main()
