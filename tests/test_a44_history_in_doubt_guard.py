import unittest
from threading import Lock

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

    def __init__(self, mode="good"):
        self.mode = mode
        self.calls = 0

    def action(self):
        self.calls += 1

        if self.mode == "throws":
            raise ValueError("A44 external action failure")

        if (
            self.mode == "noncopyable"
            or (
                self.mode == "noncopyable_after_first"
                and self.calls > 1
            )
        ):
            return {
                "name": "noncopyable",
                "lock": Lock(),
            }

        return PossibilityActualizedEvent(
            name="a44_ok",
        )

    def generate_potentials(self, cycle_id):
        return [
            Potential(
                possibility=Possibility(
                    name="a44",
                    probability=1.0,
                    mandatory=True,
                    action=self.action,
                ),
                cycle_id=cycle_id,
            )
        ]


class A44HistoryInDoubtTests(unittest.TestCase):

    def make_runner(self, mode="good"):
        process = CountingProcess(mode)
        reality = Reality()
        history = History()

        self.assertTrue(
            reality.add_natural_process(process)
        )

        return (
            ExistenceCycleRunner(
                reality=reality,
                history=history,
            ),
            process,
            history,
        )

    def test_root_snapshot_failure_blocks_retry(self):
        runner, process, history = self.make_runner(
            "noncopyable"
        )

        with self.assertRaises(TypeError):
            runner.run("a44_failed_root")

        with self.assertRaisesRegex(
            RuntimeError, "in doubt"
        ):
            runner.run("a44_failed_root")

        self.assertEqual(process.calls, 1)
        self.assertEqual(len(history.records), 0)

        attempts = history.unresolved_attempts

        self.assertEqual(len(attempts), 1)
        self.assertEqual(
            attempts[0].cycle_id,
            "a44_failed_root",
        )
        self.assertEqual(
            attempts[0].branch_id,
            "root",
        )
        self.assertEqual(
            attempts[0].status.value,
            "in_doubt",
        )

    def test_branch_snapshot_failure_blocks_retry(self):
        runner, process, history = self.make_runner(
            "noncopyable_after_first"
        )

        root = runner.run("a44_branch")

        retro = RetrospectiveActualization(
            history=history
        )

        def fork():
            return retro.create_branch(
                cycle_id="a44_branch",
                source_branch_id="root",
                new_branch_id="fork_a",
                selected_names={"a44"},
            )

        with self.assertRaises(TypeError):
            fork()

        with self.assertRaisesRegex(
            RuntimeError, "in doubt"
        ):
            fork()

        self.assertEqual(process.calls, 2)
        self.assertEqual(len(history.records), 1)
        self.assertIs(history.latest, root)

        attempts = history.unresolved_attempts

        self.assertEqual(len(attempts), 1)
        self.assertEqual(
            attempts[0].branch_id,
            "fork_a",
        )
        self.assertEqual(
            attempts[0].status.value,
            "in_doubt",
        )

    def test_action_failure_blocks_unsafe_retry(self):
        runner, process, history = self.make_runner(
            "throws"
        )

        with self.assertRaisesRegex(
            ValueError,
            "A44 external action failure",
        ):
            runner.run("a44_external_failure")

        with self.assertRaisesRegex(
            RuntimeError,
            "in doubt",
        ):
            runner.run("a44_external_failure")

        self.assertEqual(process.calls, 1)
        self.assertEqual(len(history.records), 0)

    def test_success_clears_attempt_reservation(self):
        runner, process, history = self.make_runner()

        root = runner.run("a44_success")

        retro = RetrospectiveActualization(
            history=history
        )

        fork = retro.create_branch(
            cycle_id="a44_success",
            source_branch_id="root",
            new_branch_id="fork_a",
            selected_names={"a44"},
        )

        self.assertEqual(process.calls, 2)
        self.assertEqual(len(history.records), 2)
        self.assertIs(history.records[0], root)
        self.assertIs(history.records[1], fork)
        self.assertEqual(
            history.unresolved_attempts,
            (),
        )

    def test_distinct_cycle_ids_remain_allowed(self):
        runner, process, history = self.make_runner()

        runner.run("a44_first")
        runner.run("a44_second")

        self.assertEqual(process.calls, 2)
        self.assertEqual(len(history.records), 2)

    def test_recorded_cycle_still_rejects_duplicate(self):
        runner, process, history = self.make_runner()

        runner.run("a44_recorded")

        with self.assertRaisesRegex(
            ValueError,
            "already recorded",
        ):
            runner.run("a44_recorded")

        self.assertEqual(process.calls, 1)
        self.assertEqual(len(history.records), 1)


if __name__ == "__main__":
    unittest.main()
