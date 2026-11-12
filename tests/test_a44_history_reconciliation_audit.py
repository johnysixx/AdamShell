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
from core.existence.history_record_snapshot import (
    encode_snapshot,
)
from core.existence.history_reconciliation_audit import (
    ReconciliationFinding as Finding,
    audit_history_database,
)
from core.existence.reality import Reality
from core.existence.retrospective_actualization import (
    RetrospectiveActualization,
)


class Process:
    def __init__(self):
        self.calls = 0

    def action(self):
        self.calls += 1
        return PossibilityActualizedEvent(name="audit_event")

    def generate_potentials(self, cycle_id):
        return [
            Potential(
                possibility=Possibility(
                    name="audit",
                    probability=1.0,
                    mandatory=True,
                    action=self.action,
                ),
                cycle_id=cycle_id,
            )
        ]


def run_cycle(history, process, cycle_id):
    reality = Reality()
    assert reality.add_natural_process(process)

    return ExistenceCycleRunner(
        reality=reality,
        history=history,
    ).run(cycle_id)


class A44ReconciliationAuditTests(unittest.TestCase):

    @staticmethod
    def path(folder):
        return Path(folder) / "history.sqlite3"

    @staticmethod
    def findings(db):
        return audit_history_database(db)

    def test_empty_journal_returns_no_findings(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.path(folder)
            History(journal_path=db, durable_records=True)

            self.assertEqual(self.findings(db), ())

    def test_running_attempt_requires_manual_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.path(folder)
            history = History(
                journal_path=db, durable_records=True
            )
            history.begin_attempt("running")

            result, = self.findings(db)

            self.assertEqual(result.journal_status, "running")
            self.assertEqual(
                result.finding, Finding.HOLD_UNKNOWN_OUTCOME
            )
            self.assertFalse(result.retry_allowed)

    def test_in_doubt_attempt_requires_manual_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.path(folder)
            history = History(
                journal_path=db, durable_records=True
            )
            attempt = history.begin_attempt("uncertain")
            history.mark_attempt_in_doubt(attempt)

            result, = self.findings(db)

            self.assertEqual(result.journal_status, "in_doubt")
            self.assertEqual(
                result.finding, Finding.HOLD_UNKNOWN_OUTCOME
            )
            self.assertFalse(result.retry_allowed)

    def test_completed_archive_has_valid_fingerprint(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.path(folder)
            process = Process()
            history = History(
                journal_path=db, durable_records=True
            )
            run_cycle(history, process, "completed")

            result, = self.findings(db)

            self.assertEqual(
                result.finding, Finding.ARCHIVED_COMPLETED
            )
            self.assertEqual(result.journal_status, "completed")
            self.assertEqual(len(result.snapshot_sha256), 64)
            self.assertFalse(result.retry_allowed)
            self.assertEqual(process.calls, 1)

    def test_legacy_completed_without_archive_is_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.path(folder)
            history = History(journal_path=db)
            process = Process()
            run_cycle(history, process, "legacy")

            result, = self.findings(db)

            self.assertEqual(
                result.finding, Finding.HOLD_MISSING_SNAPSHOT
            )
            self.assertIsNone(result.snapshot_sha256)
            self.assertFalse(result.retry_allowed)

            with closing(sqlite3.connect(db)) as connection:
                archive_table = connection.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE name = 'history_record_snapshots'"
                ).fetchone()

            # Audit must not create the table during inspection.
            self.assertIsNone(archive_table)

    def test_corrupted_completed_snapshot_is_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.path(folder)
            history = History(
                journal_path=db, durable_records=True
            )
            run_cycle(history, Process(), "corrupted")

            with closing(sqlite3.connect(db)) as connection:
                connection.execute(
                    "UPDATE history_record_snapshots "
                    "SET snapshot_json = ?",
                    ("{}",),
                )
                connection.commit()

            result, = self.findings(db)

            self.assertEqual(
                result.finding, Finding.HOLD_INVALID_SNAPSHOT
            )
            self.assertFalse(result.retry_allowed)

    def test_uncompleted_snapshot_is_inconsistent(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.path(folder)
            history = History(
                journal_path=db, durable_records=True
            )
            history.begin_attempt("inconsistent")

            with closing(sqlite3.connect(db)) as connection:
                connection.execute(
                    "INSERT INTO history_record_snapshots "
                    "(cycle_id, branch_id, snapshot_json) "
                    "VALUES (?, ?, ?)",
                    ("inconsistent", "root", "{}"),
                )
                connection.commit()

            result, = self.findings(db)

            self.assertEqual(
                result.finding,
                Finding.HOLD_UNCOMPLETED_SNAPSHOT,
            )
            self.assertFalse(result.retry_allowed)

    def test_orphan_archive_is_inconsistent(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.path(folder)
            History(journal_path=db, durable_records=True)

            with closing(sqlite3.connect(db)) as connection:
                connection.execute(
                    "INSERT INTO history_record_snapshots "
                    "(cycle_id, branch_id, snapshot_json) "
                    "VALUES (?, ?, ?)",
                    ("orphan", "root", "{}"),
                )
                connection.commit()

            result, = self.findings(db)

            self.assertEqual(
                result.finding, Finding.HOLD_ORPHAN_SNAPSHOT
            )
            self.assertEqual(result.journal_status, "missing")
            self.assertFalse(result.retry_allowed)

    def test_snapshot_identity_mismatch_is_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.path(folder)
            history = History(
                journal_path=db, durable_records=True
            )
            run_cycle(history, Process(), "original")

            forged = history.latest.public_state
            forged["cycle_id"] = "different"

            with closing(sqlite3.connect(db)) as connection:
                connection.execute(
                    "UPDATE history_record_snapshots "
                    "SET snapshot_json = ?",
                    (encode_snapshot(forged),),
                )
                connection.commit()

            result, = self.findings(db)

            self.assertEqual(
                result.finding, Finding.HOLD_INVALID_SNAPSHOT
            )
            self.assertFalse(result.retry_allowed)

    def test_missing_database_is_not_created(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.path(folder)

            with self.assertRaises(FileNotFoundError):
                self.findings(db)

            self.assertFalse(db.exists())

    def test_read_only_audit_preserves_database_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.path(folder)
            history = History(
                journal_path=db, durable_records=True
            )
            run_cycle(history, Process(), "read_only")

            before = db.read_bytes()
            self.findings(db)
            after = db.read_bytes()

            self.assertEqual(before, after)

    def test_root_and_fork_are_audited_separately(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.path(folder)
            process = Process()
            history = History(
                journal_path=db, durable_records=True
            )
            run_cycle(history, process, "branch")

            RetrospectiveActualization(
                history=history
            ).create_branch(
                cycle_id="branch",
                source_branch_id="root",
                new_branch_id="fork_a",
                selected_names={"audit"},
            )

            findings = self.findings(db)

            self.assertEqual(len(findings), 2)
            self.assertEqual(
                {item.branch_id for item in findings},
                {"root", "fork_a"},
            )
            self.assertTrue(
                all(
                    item.finding is Finding.ARCHIVED_COMPLETED
                    and not item.retry_allowed
                    for item in findings
                )
            )
            self.assertEqual(process.calls, 2)


if __name__ == "__main__":
    unittest.main()
