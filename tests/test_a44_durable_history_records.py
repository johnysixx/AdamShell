import sqlite3
import tempfile
import unittest

from contextlib import closing
from pathlib import Path

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

        if self.mode == "unsupported":
            return {"not_json": {1, 2}}

        return PossibilityActualizedEvent(
            name="a44_event"
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


def runner(process, history):
    reality = Reality()
    assert reality.add_natural_process(process)

    return ExistenceCycleRunner(
        reality=reality,
        history=history,
    )


def database_status(db, cycle_id, branch_id="root"):
    with closing(sqlite3.connect(db)) as connection:
        row = connection.execute(
            "SELECT status FROM history_attempts "
            "WHERE cycle_id = ? AND branch_id = ?",
            (cycle_id, branch_id),
        ).fetchone()

    return row[0] if row else None


class A44DurableHistoryRecordsTests(unittest.TestCase):

    def test_completed_record_restores_without_reexecution(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "records.sqlite3"
            process = CountingProcess()

            original = History(
                journal_path=db,
                durable_records=True,
            )

            record = runner(
                process, original
            ).run("completed_25")

            restored = History(
                journal_path=db,
                durable_records=True,
            )

            self.assertEqual(len(restored.records), 1)
            self.assertEqual(
                restored.latest.public_state,
                record.public_state,
            )

            with self.assertRaisesRegex(
                ValueError, "already recorded"
            ):
                runner(process, restored).run(
                    "completed_25"
                )

            self.assertEqual(process.calls, 1)
            self.assertEqual(
                database_status(db, "completed_25"),
                "completed",
            )

    def test_restored_public_state_is_detached(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "records.sqlite3"
            process = CountingProcess()

            original = History(
                journal_path=db,
                durable_records=True,
            )

            runner(process, original).run("detached")

            restored = History(
                journal_path=db,
                durable_records=True,
            )

            snapshot = restored.latest.public_state
            snapshot["events"].clear()
            snapshot["actualized"].clear()

            self.assertEqual(
                len(restored.latest.public_state["events"]),
                1,
            )
            self.assertEqual(
                len(restored.latest.public_state["actualized"]),
                1,
            )

    def test_branches_restore_but_replay_is_unbound(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "records.sqlite3"
            process = CountingProcess()

            original = History(
                journal_path=db,
                durable_records=True,
            )

            runner(process, original).run("branch_25")

            RetrospectiveActualization(
                history=original
            ).create_branch(
                cycle_id="branch_25",
                source_branch_id="root",
                new_branch_id="fork_a",
                selected_names={"a44"},
            )

            restored = History(
                journal_path=db,
                durable_records=True,
            )

            self.assertEqual(len(restored.records), 2)
            self.assertEqual(
                restored.find_record(
                    "branch_25", "fork_a"
                ).parent_branch_id,
                "root",
            )

            with self.assertRaisesRegex(
                RuntimeError, "unbound"
            ):
                RetrospectiveActualization(
                    history=restored
                ).create_branch(
                    cycle_id="branch_25",
                    source_branch_id="root",
                    new_branch_id="fork_b",
                    selected_names={"a44"},
                )

            self.assertEqual(process.calls, 2)
            self.assertIsNone(
                database_status(
                    db, "branch_25", "fork_b"
                )
            )

    def test_interrupted_running_attempt_stays_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "records.sqlite3"

            original = History(
                journal_path=db,
                durable_records=True,
            )

            original.begin_attempt("interrupted_25")

            restored = History(
                journal_path=db,
                durable_records=True,
            )

            process = CountingProcess()

            with self.assertRaisesRegex(
                RuntimeError, "in doubt"
            ):
                runner(process, restored).run(
                    "interrupted_25"
                )

            self.assertEqual(process.calls, 0)
            self.assertEqual(len(restored.records), 0)

    def test_snapshot_and_completion_rollback_together(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "records.sqlite3"
            process = CountingProcess()

            original = History(
                journal_path=db,
                durable_records=True,
            )

            with closing(sqlite3.connect(db)) as connection:
                connection.execute(
                    "CREATE TRIGGER a44_injected_failure "
                    "BEFORE UPDATE OF status ON history_attempts "
                    "WHEN NEW.status = 'completed' "
                    "BEGIN SELECT RAISE("
                    "ABORT, 'A44 injected completion failure'"
                    "); END"
                )
                connection.commit()

            with self.assertRaises(sqlite3.IntegrityError):
                runner(process, original).run(
                    "atomic_25"
                )

            with closing(sqlite3.connect(db)) as connection:
                count = connection.execute(
                    "SELECT COUNT(*) "
                    "FROM history_record_snapshots"
                ).fetchone()[0]

            self.assertEqual(count, 0)
            self.assertEqual(
                database_status(db, "atomic_25"),
                "running",
            )

            restored = History(
                journal_path=db,
                durable_records=True,
            )

            self.assertEqual(len(restored.records), 0)

            with self.assertRaisesRegex(
                RuntimeError, "in doubt"
            ):
                runner(process, restored).run("atomic_25")

            self.assertEqual(process.calls, 1)

    def test_unsupported_event_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "records.sqlite3"
            process = CountingProcess("unsupported")

            original = History(
                journal_path=db,
                durable_records=True,
            )

            with self.assertRaisesRegex(
                TypeError, "Unsupported history"
            ):
                runner(process, original).run(
                    "unsupported_25"
                )

            restored = History(
                journal_path=db,
                durable_records=True,
            )

            with self.assertRaisesRegex(
                RuntimeError, "in doubt"
            ):
                runner(process, restored).run(
                    "unsupported_25"
                )

            self.assertEqual(process.calls, 1)
            self.assertEqual(
                database_status(db, "unsupported_25"),
                "running",
            )

    def test_old_completed_journal_requires_reconciliation(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "records.sqlite3"
            process = CountingProcess()

            legacy = History(journal_path=db)
            runner(process, legacy).run("old_completed")

            with self.assertRaisesRegex(
                RuntimeError, "lacks"
            ):
                History(
                    journal_path=db,
                    durable_records=True,
                )

            self.assertEqual(process.calls, 1)

    def test_corrupt_archive_refuses_restoration(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "records.sqlite3"
            process = CountingProcess()

            original = History(
                journal_path=db,
                durable_records=True,
            )

            runner(process, original).run("corrupt_25")

            with closing(sqlite3.connect(db)) as connection:
                connection.execute(
                    "UPDATE history_record_snapshots "
                    "SET snapshot_json = ?",
                    ("{}",),
                )
                connection.commit()

            with self.assertRaises(ValueError):
                History(
                    journal_path=db,
                    durable_records=True,
                )

    def test_opt_in_and_legacy_memory_mode(self):
        with self.assertRaises(ValueError):
            History(durable_records=True)

        process = CountingProcess()
        history = History()

        runner(process, history).run("legacy_25")

        self.assertEqual(process.calls, 1)
        self.assertEqual(len(history.records), 1)
        self.assertEqual(
            history.unresolved_attempts,
            (),
        )


if __name__ == "__main__":
    unittest.main()
