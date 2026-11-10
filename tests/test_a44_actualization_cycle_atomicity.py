import unittest

from core.actualization.actualizer import Actualizer
from core.actualization.cycle import ActualizationCycle
from core.actualization.cycle_state import ActualizationCycleState
from core.actualization.directed_actualizer import DirectedActualizer
from core.actualization.possibility import Possibility
from core.actualization.potential import Potential
from core.actualization.potential_state import PotentialState


class A44ActualizationCycleAtomicityTests(unittest.TestCase):

    @staticmethod
    def potential(cycle, name, action=None, mandatory=True):
        return Potential(
            possibility=Possibility(
                name=name,
                probability=1.0,
                action=action,
                mandatory=mandatory,
            ),
            cycle_id=cycle.cycle_id,
        )

    def failing_cycle(self):
        cycle = ActualizationCycle("a44_failure")
        calls = []

        def first_action():
            calls.append("first")
            return "first_event"

        def second_action():
            calls.append("second")
            raise RuntimeError("A44 injected action failure")

        first = self.potential(
            cycle, "first", first_action
        )
        second = self.potential(
            cycle, "second", second_action
        )

        self.assertTrue(cycle.add_potential(first))
        self.assertTrue(cycle.add_potential(second))

        return cycle, first, second, calls

    def assert_restored(self, cycle, first, second):
        self.assertIs(
            cycle.state,
            ActualizationCycleState.OPEN,
        )
        self.assertIs(
            first.state,
            PotentialState.OPEN,
        )
        self.assertIs(
            second.state,
            PotentialState.OPEN,
        )

    def test_default_actualizer_failure_restores_states(self):
        cycle, first, second, calls = self.failing_cycle()

        with self.assertRaisesRegex(
            RuntimeError, "A44 injected action failure"
        ):
            cycle.resolve(actualizer=Actualizer())

        self.assertEqual(calls, ["first", "second"])
        self.assert_restored(cycle, first, second)

    def test_directed_actualizer_failure_restores_states(self):
        cycle, first, second, calls = self.failing_cycle()

        with self.assertRaisesRegex(
            RuntimeError, "A44 injected action failure"
        ):
            cycle.resolve(
                actualizer=DirectedActualizer(
                    selected_names={"first", "second"}
                )
            )

        self.assertEqual(calls, ["first", "second"])
        self.assert_restored(cycle, first, second)

    def test_selection_failure_restores_changed_state(self):
        cycle = ActualizationCycle("a44_selection")
        first = self.potential(cycle, "first")

        self.assertTrue(cycle.add_potential(first))

        class FailingSelector:
            def select(self, potentials):
                potentials[0].mark_actualized()
                raise RuntimeError("A44 injected selection failure")

        with self.assertRaisesRegex(
            RuntimeError, "A44 injected selection failure"
        ):
            cycle.resolve(actualizer=FailingSelector())

        self.assertIs(
            cycle.state,
            ActualizationCycleState.OPEN,
        )
        self.assertIs(
            first.state,
            PotentialState.OPEN,
        )

    def test_success_preserves_existing_resolution_behavior(self):
        cycle = ActualizationCycle("a44_success")

        selected = self.potential(
            cycle, "selected", mandatory=False
        )
        unselected = self.potential(
            cycle, "unselected", mandatory=False
        )

        self.assertTrue(cycle.add_potential(selected))
        self.assertTrue(cycle.add_potential(unselected))

        events = cycle.resolve(
            actualizer=DirectedActualizer(
                selected_names={"selected"}
            )
        )

        self.assertEqual(
            [event.name for event in events],
            ["selected"],
        )

        self.assertIs(
            cycle.state,
            ActualizationCycleState.RESOLVED,
        )
        self.assertIs(
            selected.state,
            PotentialState.ACTUALIZED,
        )
        self.assertIs(
            unselected.state,
            PotentialState.UNREALIZED,
        )

        self.assertEqual(cycle.resolve(), [])


if __name__ == "__main__":
    unittest.main()
