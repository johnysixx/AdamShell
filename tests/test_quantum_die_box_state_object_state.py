import unittest

from core.entity.quantum_die_box_state import (
    QuantumDieBoxState,
)


class QuantumDieBoxStateObjectStateTests(
    unittest.TestCase
):

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state
                in QuantumDieBoxState
            },
            {
                "quantum_position_unresolved",
                "position_resolved",
            },
        )


if __name__ == "__main__":
    unittest.main()
