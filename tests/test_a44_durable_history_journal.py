import sqlite3
from contextlib import closing
import tempfile
import unittest

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, Lock

from core.actualization.possibility import (
    Possibility,
    PossibilityActualizedEvent,
)
from core.actualization.potential import Potential
from core.existence.history_attempt_state import (
    HistoryAttemptStatus,
)
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
        self.generations = 0

    def action(self):
        self.calls += 1

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
            name="a44_event",
        )

    def generate_potentials(self, cycle_id):
        self.generations += 1

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


class A44DurableHistoryJournalTests(unittest.TestCase):

    @staticmethod
    def runner(process, history):
        reality = Reality()
        assert reality.add_natural_process(process)

        return ExistenceCycleRunner(
            reality=reality,
            history=history,
        )

    def test_failed_root_is_blocked_after_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "attempts.sqlite3"
            process = CountingProcess("noncopyable")

            original = History(journal_path=db)

            with self.assertRaises(TypeError):
                self.runner(process, original).run("failed")

            restored = History(journal_path=db)

            self.assertEqual(
                restored.unresolved_attempts[0].status,
                HistoryAttemptStatus.IN_DOUBT,
            )

            with self.assertRaisesRegex(
                RuntimeError,
                "in doubt",
            ):
                self.runner(process, restored).run("failed")

            self.assertEqual(process.calls, 1)
            self.assertEqual(len(restored.records), 0)

    def test_completed_cycle_stays_reserved(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "attempts.sqlite3"
            process = CountingProcess()

            original = History(journal_path=db)
            self.runner(process, original).run("completed")

            restored = History(journal_path=db)

            with self.assertRaisesRegex(
                ValueError,
                "already recorded",
            ):
                self.runner(process, restored).run("completed")

            self.assertEqual(process.calls, 1)
            self.assertEqual(restored.unresolved_attempts, ())

            with closing(sqlite3.connect(db)) as connection:
                status = connection.execute(
                    "SELECT status FROM history_attempts "
                    "WHERE cycle_id = ? AND branch_id = ?",
                    ("completed", "root"),
                ).fetchone()[0]

            self.assertEqual(status, "completed")

    def test_running_reservation_survives_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "attempts.sqlite3"

            original = History(journal_path=db)
            original.begin_attempt("interrupted")

            restored = History(journal_path=db)

            self.assertEqual(
                restored.unresolved_attempts[0].status,
                HistoryAttemptStatus.RUNNING,
            )

            process = CountingProcess()

            with self.assertRaisesRegex(
                RuntimeError,
                "in doubt",
            ):
                self.runner(process, restored).run(
                    "interrupted"
                )

            self.assertEqual(process.generations, 0)
            self.assertEqual(process.calls, 0)

    def test_failed_branch_stays_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "attempts.sqlite3"
            process = CountingProcess(
                "noncopyable_after_first"
            )

            original = History(journal_path=db)
            self.runner(process, original).run("branching")

            retrospective = RetrospectiveActualization(
                history=original
            )

            def create_fork(history):
                return RetrospectiveActualization(
                    history=history
                ).create_branch(
                    cycle_id="branching",
                    source_branch_id="root",
                    new_branch_id="fork_a",
                    selected_names={"a44"},
                )

            with self.assertRaises(TypeError):
                create_fork(original)

            self.assertEqual(process.calls, 2)

            restored = History(journal_path=db)

            # The HistoryRecord store is not durable yet.
            # Simulate restoring the original source records.
            restored.records = list(original.records)

            with self.assertRaisesRegex(
                RuntimeError,
                "in doubt",
            ):
                create_fork(restored)

            self.assertEqual(process.calls, 2)
            self.assertEqual(len(restored.records), 1)

    def test_parallel_reservations_are_exclusive(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "attempts.sqlite3"

            first = History(journal_path=db)
            second = History(journal_path=db)
            barrier = Barrier(2)

            def reserve(history):
                barrier.wait(timeout=10)

                try:
                    history.begin_attempt("parallel")
                    return "reserved"
                except RuntimeError:
                    return "blocked"

            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [
                    pool.submit(reserve, first),
                    pool.submit(reserve, second),
                ]
                results = [
                    future.result(timeout=20)
                    for future in futures
                ]

            self.assertEqual(
                sorted(results),
                ["blocked", "reserved"],
            )

    def test_distinct_cycles_and_branches_succeed(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "attempts.sqlite3"
            process = CountingProcess()
            history = History(journal_path=db)
            runner = self.runner(process, history)

            runner.run("first")
            runner.run("second")

            RetrospectiveActualization(
                history=history
            ).create_branch(
                cycle_id="first",
                source_branch_id="root",
                new_branch_id="fork_a",
                selected_names={"a44"},
            )

            self.assertEqual(process.calls, 3)
            self.assertEqual(len(history.records), 3)
            self.assertEqual(history.unresolved_attempts, ())

            with closing(sqlite3.connect(db)) as connection:
                count = connection.execute(
                    "SELECT COUNT(*) FROM history_attempts "
                    "WHERE status = 'completed'"
                ).fetchone()[0]

            self.assertEqual(count, 3)

    def test_invalid_identifiers_fail_before_action(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "attempts.sqlite3"
            process = CountingProcess()

            history = History(journal_path=db)

            with self.assertRaises(TypeError):
                self.runner(process, history).run(123)

            self.assertEqual(process.generations, 0)
            self.assertEqual(process.calls, 0)

        with self.assertRaises(ValueError):
            History(journal_path="relative.sqlite3")

    def test_legacy_memory_mode_stays_compatible(self):
        process = CountingProcess()
        history = History()
        runner = self.runner(process, history)

        runner.run("legacy")

        with self.assertRaisesRegex(
            ValueError,
            "already recorded",
        ):
            runner.run("legacy")

        self.assertEqual(process.calls, 1)
        self.assertEqual(len(history.records), 1)


if __name__ == "__main__":
    unittest.main()
