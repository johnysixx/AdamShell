import unittest

from core.actualization.cycle import ActualizationCycle
from core.actualization.cycle_state import (
    ActualizationCycleState,
)
from core.actualization.possibility import Possibility
from core.actualization.potential import Potential
from core.existence.history import History


class ActualizationCycleStateObjectStateTests(
    unittest.TestCase
):

    def make_cycle(self):
        cycle = ActualizationCycle(
            "cycle_test"
        )

        cycle.add_potential(
            Potential(
                possibility=Possibility(
                    name="mandatory_test",
                    probability=1.0,
                    mandatory=True,
                ),
                cycle_id="cycle_test",
            )
        )

        return cycle

    def test_cycle_starts_open_as_enum(self):
        cycle = self.make_cycle()

        self.assertIs(
            cycle.state,
            ActualizationCycleState.OPEN,
        )

        self.assertEqual(
            cycle.public_state["state"],
            "open",
        )

    def test_resolve_sets_resolved_enum(self):
        cycle = self.make_cycle()

        cycle.resolve()

        self.assertIs(
            cycle.state,
            ActualizationCycleState.RESOLVED,
        )

        self.assertEqual(
            cycle.public_state["state"],
            "resolved",
        )

    def test_string_state_is_rejected(self):
        cycle = self.make_cycle()

        with self.assertRaises(TypeError):
            cycle.state = "resolved"

    def test_history_requires_resolved_enum_state(
        self
    ):
        history = History()
        cycle = self.make_cycle()

        with self.assertRaises(ValueError):
            history.record_cycle(
                cycle=cycle,
                events=[],
            )

        events = cycle.resolve()

        record = history.record_cycle(
            cycle=cycle,
            events=events,
        )

        self.assertEqual(
            record.cycle_id,
            "cycle_test",
        )

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state
                in ActualizationCycleState
            },
            {
                "open",
                "resolved",
            },
        )


if __name__ == "__main__":
    unittest.main()
