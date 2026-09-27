import unittest

from core.actualization.possibility import Possibility
from core.actualization.potential import Potential
from core.actualization.potential_state import (
    PotentialState,
)
from core.existence.history import HistoryRecord


class PotentialStateObjectStateTests(
    unittest.TestCase
):

    def make_potential(self):
        return Potential(
            possibility=Possibility(
                name="test_potential",
                probability=1.0,
                mandatory=True,
            ),
            cycle_id="cycle_test",
        )

    def test_potential_starts_open_as_enum(self):
        potential = self.make_potential()

        self.assertIs(
            potential.state,
            PotentialState.OPEN,
        )
        self.assertTrue(
            potential.is_open
        )
        self.assertEqual(
            potential.public_state["state"],
            "open",
        )

    def test_mark_actualized_sets_enum(self):
        potential = self.make_potential()

        self.assertTrue(
            potential.mark_actualized()
        )
        self.assertIs(
            potential.state,
            PotentialState.ACTUALIZED,
        )
        self.assertFalse(
            potential.is_open
        )
        self.assertEqual(
            potential.public_state["state"],
            "actualized",
        )

    def test_mark_unrealized_sets_enum(self):
        potential = self.make_potential()

        self.assertTrue(
            potential.mark_unrealized()
        )
        self.assertIs(
            potential.state,
            PotentialState.UNREALIZED,
        )
        self.assertFalse(
            potential.is_open
        )
        self.assertEqual(
            potential.public_state["state"],
            "unrealized",
        )

    def test_string_state_is_rejected(self):
        potential = self.make_potential()

        with self.assertRaises(TypeError):
            potential.state = "actualized"

    def test_history_record_classifies_enum_states(
        self
    ):
        actualized = self.make_potential()
        unrealized = self.make_potential()

        actualized.mark_actualized()
        unrealized.mark_unrealized()

        record = HistoryRecord(
            cycle_id="cycle_test",
            events=[],
            potentials=[
                actualized,
                unrealized,
            ],
        )

        self.assertEqual(
            [
                state["state"]
                for state in record.actualized
            ],
            [
                "actualized",
            ],
        )

        self.assertEqual(
            [
                state["state"]
                for state in record.unrealized
            ],
            [
                "unrealized",
            ],
        )

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in PotentialState
            },
            {
                "open",
                "actualized",
                "unrealized",
            },
        )


if __name__ == "__main__":
    unittest.main()
