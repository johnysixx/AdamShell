import unittest

from core.actualization.possibility import (
    Possibility,
    PossibilityActualizedEvent,
)
from core.actualization.potential import Potential
from core.existence.cycle_runner import ExistenceCycleRunner
from core.existence.history import History
from core.existence.reality import Reality
from core.existence.retrospective_actualization import (
    RetrospectiveActualization,
)


class CountingProcess:

    def __init__(self):
        self.generations = 0
        self.actions = 0

    def generate_potentials(self, cycle_id):
        self.generations += 1

        def action():
            self.actions += 1
            return PossibilityActualizedEvent(
                name="selected",
            )

        return [
            Potential(
                possibility=Possibility(
                    name="selected",
                    probability=1.0,
                    mandatory=True,
                    action=action,
                ),
                cycle_id=cycle_id,
            )
        ]


class A44HistoryDuplicatePreflightTests(unittest.TestCase):

    def make_runner(self):
        process = CountingProcess()
        reality = Reality()
        history = History()

        self.assertTrue(
            reality.add_natural_process(process)
        )

        runner = ExistenceCycleRunner(
            reality=reality,
            history=history,
        )

        return runner, process, history

    def test_duplicate_cycle_rejected_before_any_new_work(self):
        runner, process, history = self.make_runner()

        original = runner.run("a44_duplicate")

        self.assertEqual(process.generations, 1)
        self.assertEqual(process.actions, 1)

        with self.assertRaisesRegex(
            ValueError,
            "already recorded",
        ):
            runner.run("a44_duplicate")

        self.assertEqual(process.generations, 1)
        self.assertEqual(process.actions, 1)
        self.assertEqual(len(history.records), 1)
        self.assertIs(history.latest, original)

    def test_distinct_cycle_ids_remain_allowed(self):
        runner, process, history = self.make_runner()

        first = runner.run("a44_first")
        second = runner.run("a44_second")

        self.assertIsNot(first, second)
        self.assertEqual(process.generations, 2)
        self.assertEqual(process.actions, 2)
        self.assertEqual(len(history.records), 2)

    def test_duplicate_history_branch_rejected_before_action(self):
        runner, process, history = self.make_runner()
        runner.run("a44_branching")

        retrospective = RetrospectiveActualization(
            history=history
        )

        first_branch = retrospective.create_branch(
            cycle_id="a44_branching",
            source_branch_id="root",
            new_branch_id="fork_a",
            selected_names={"selected"},
        )

        self.assertEqual(process.actions, 2)
        self.assertEqual(len(history.records), 2)

        with self.assertRaisesRegex(
            ValueError,
            "already recorded",
        ):
            retrospective.create_branch(
                cycle_id="a44_branching",
                source_branch_id="root",
                new_branch_id="fork_a",
                selected_names={"selected"},
            )

        self.assertEqual(process.actions, 2)
        self.assertEqual(len(history.records), 2)
        self.assertIs(
            history.find_record(
                "a44_branching",
                "fork_a",
            ),
            first_branch,
        )

    def test_different_history_branches_remain_allowed(self):
        runner, process, history = self.make_runner()
        runner.run("a44_branching")

        retrospective = RetrospectiveActualization(
            history=history
        )

        first = retrospective.create_branch(
            cycle_id="a44_branching",
            source_branch_id="root",
            new_branch_id="fork_a",
            selected_names={"selected"},
        )

        second = retrospective.create_branch(
            cycle_id="a44_branching",
            source_branch_id="root",
            new_branch_id="fork_b",
            selected_names={"selected"},
        )

        self.assertIsNot(first, second)
        self.assertEqual(first.branch_id, "fork_a")
        self.assertEqual(second.branch_id, "fork_b")
        self.assertEqual(process.actions, 3)
        self.assertEqual(len(history.records), 3)


if __name__ == "__main__":
    unittest.main()
