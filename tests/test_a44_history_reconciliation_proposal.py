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
from core.existence.history_reconciliation_proposal import (
    EvidenceVerdict,
    ExternalEvidence,
    ProposalDecision as Decision,
    propose_reconciliation,
)
from core.existence.reality import Reality


SOURCE = "a44-test-provider"
EFFECT = "external-effect"


class ReceiptVerifier:
    """Test-only independent SQLite receipt provider."""

    def __init__(self, path):
        self.path = path

        with closing(sqlite3.connect(path)) as connection:
            connection.execute(
                "CREATE TABLE receipts ("
                "cycle_id TEXT NOT NULL, "
                "branch_id TEXT NOT NULL, "
                "effect_id TEXT NOT NULL, "
                "receipt_id TEXT NOT NULL, "
                "PRIMARY KEY (cycle_id, branch_id, effect_id))"
            )
            connection.commit()

    def record(self, cycle_id, branch_id, effect_id, receipt_id):
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute(
                "INSERT INTO receipts VALUES (?, ?, ?, ?)",
                (cycle_id, branch_id, effect_id, receipt_id),
            )
            connection.commit()

    def verify(self, *, cycle_id, branch_id, effect_id):
        with closing(sqlite3.connect(self.path)) as connection:
            row = connection.execute(
                "SELECT receipt_id FROM receipts "
                "WHERE cycle_id = ? AND branch_id = ? "
                "AND effect_id = ?",
                (cycle_id, branch_id, effect_id),
            ).fetchone()

        return ExternalEvidence(
            cycle_id=cycle_id,
            branch_id=branch_id,
            effect_id=effect_id,
            source_id=SOURCE,
            verdict=(
                EvidenceVerdict.CONFIRMED
                if row
                else EvidenceVerdict.NOT_FOUND
            ),
            receipt_id=row[0] if row else None,
        )


class StaticVerifier:
    def __init__(self, response):
        self.response = response

    def verify(self, **kwargs):
        return self.response


class FailingVerifier:
    def verify(self, **kwargs):
        raise RuntimeError("Provider unavailable.")


class Process:
    def __init__(self):
        self.calls = 0

    def action(self):
        self.calls += 1
        return PossibilityActualizedEvent(
            name="proposal_event"
        )

    def generate_potentials(self, cycle_id):
        return [
            Potential(
                possibility=Possibility(
                    name="proposal",
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


def evidence(
    cycle="cycle",
    branch="root",
    effect=EFFECT,
    source=SOURCE,
    verdict=EvidenceVerdict.CONFIRMED,
    receipt="receipt-1",
):
    return ExternalEvidence(
        cycle_id=cycle,
        branch_id=branch,
        effect_id=effect,
        source_id=source,
        verdict=verdict,
        receipt_id=receipt,
    )


def proposal(db, cycle="cycle", verifier=None):
    return propose_reconciliation(
        db,
        cycle_id=cycle,
        branch_id="root",
        effect_id=EFFECT,
        expected_source_id=SOURCE,
        verifier=verifier,
    )


class A44EvidenceProposalTests(unittest.TestCase):

    @staticmethod
    def database(folder):
        return Path(folder) / "history.sqlite3"

    @staticmethod
    def running(db, cycle="cycle"):
        history = History(
            journal_path=db,
            durable_records=True,
        )
        return history, history.begin_attempt(cycle)

    @staticmethod
    def assert_no_action_authority(item):
        assert item.retry_allowed is False
        assert item.mutation_allowed is False

    def test_running_confirmed_effect_requires_review(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            history, attempt = self.running(db)
            provider = ReceiptVerifier(
                Path(folder) / "external.sqlite3"
            )
            provider.record("cycle", "root", EFFECT, "receipt-1")

            result = proposal(db, verifier=provider)

            self.assertEqual(
                result.decision,
                Decision.REVIEW_EFFECT_CONFIRMED,
            )
            self.assertEqual(result.receipt_id, "receipt-1")
            self.assertEqual(result.journal_status, "running")
            self.assertEqual(
                history.find_attempt("cycle").status,
                attempt.status,
            )
            self.assert_no_action_authority(result)

    def test_in_doubt_missing_receipt_is_not_negative_proof(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            history, attempt = self.running(db)
            history.mark_attempt_in_doubt(attempt)
            provider = ReceiptVerifier(
                Path(folder) / "external.sqlite3"
            )

            result = proposal(db, verifier=provider)

            self.assertEqual(
                result.decision, Decision.HOLD_NO_RECEIPT
            )
            self.assertEqual(result.journal_status, "in_doubt")
            self.assert_no_action_authority(result)

    def test_wrong_branch_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            self.running(db)

            result = proposal(
                db,
                verifier=StaticVerifier(
                    evidence(branch="other")
                ),
            )

            self.assertEqual(
                result.decision,
                Decision.HOLD_IDENTITY_MISMATCH,
            )
            self.assert_no_action_authority(result)

    def test_wrong_effect_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            self.running(db)

            result = proposal(
                db,
                verifier=StaticVerifier(
                    evidence(effect="different")
                ),
            )

            self.assertEqual(
                result.decision,
                Decision.HOLD_IDENTITY_MISMATCH,
            )

    def test_wrong_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            self.running(db)

            result = proposal(
                db,
                verifier=StaticVerifier(
                    evidence(source="other-provider")
                ),
            )

            self.assertEqual(
                result.decision,
                Decision.HOLD_IDENTITY_MISMATCH,
            )

    def test_changed_journal_invalidates_old_audit(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            history, attempt = self.running(db)

            class ChangingVerifier:
                def verify(self, **kwargs):
                    history.mark_attempt_in_doubt(attempt)
                    return evidence()

            result = proposal(
                db,
                verifier=ChangingVerifier(),
            )

            self.assertEqual(
                result.decision, Decision.HOLD_STALE
            )
            self.assertEqual(result.journal_status, "in_doubt")
            self.assertIsNone(result.receipt_id)
            self.assert_no_action_authority(result)

    def test_completed_record_is_review_only(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            history = History(
                journal_path=db,
                durable_records=True,
            )
            process = Process()
            run_cycle(history, process, "cycle")

            result = proposal(
                db,
                verifier=StaticVerifier(evidence()),
            )

            self.assertEqual(
                result.decision,
                Decision.REVIEW_ARCHIVED_COMPLETED,
            )
            self.assertEqual(result.journal_status, "completed")
            self.assertEqual(len(result.snapshot_sha256), 64)
            self.assertEqual(process.calls, 1)
            self.assert_no_action_authority(result)

    def test_legacy_completed_without_snapshot_is_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            history = History(journal_path=db)
            run_cycle(history, Process(), "cycle")

            result = proposal(
                db,
                verifier=StaticVerifier(evidence()),
            )

            self.assertEqual(
                result.decision, Decision.HOLD_INVALID_HISTORY
            )
            self.assert_no_action_authority(result)

    def test_corrupt_snapshot_is_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            history = History(
                journal_path=db,
                durable_records=True,
            )
            run_cycle(history, Process(), "cycle")

            with closing(sqlite3.connect(db)) as connection:
                connection.execute(
                    "UPDATE history_record_snapshots "
                    "SET snapshot_json = '{}'"
                )
                connection.commit()

            result = proposal(
                db,
                verifier=StaticVerifier(evidence()),
            )

            self.assertEqual(
                result.decision, Decision.HOLD_INVALID_HISTORY
            )

    def test_missing_attempt_is_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            History(journal_path=db, durable_records=True)

            result = proposal(
                db, verifier=StaticVerifier(evidence())
            )

            self.assertEqual(
                result.decision,
                Decision.HOLD_MISSING_ATTEMPT,
            )
            self.assert_no_action_authority(result)

    def test_no_verifier_is_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            self.running(db)

            result = proposal(db)

            self.assertEqual(
                result.decision, Decision.HOLD_NO_VERIFIER
            )
            self.assert_no_action_authority(result)

    def test_malformed_provider_response_is_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            self.running(db)

            result = proposal(
                db,
                verifier=StaticVerifier({"confirmed": True}),
            )

            self.assertEqual(
                result.decision,
                Decision.HOLD_INVALID_EVIDENCE,
            )

    def test_provider_exception_is_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            self.running(db)

            result = proposal(
                db, verifier=FailingVerifier()
            )

            self.assertEqual(
                result.decision, Decision.HOLD_VERIFIER_ERROR
            )
            self.assert_no_action_authority(result)

    def test_proposal_does_not_modify_history_database(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            self.running(db)

            before = db.read_bytes()

            result = proposal(
                db,
                verifier=StaticVerifier(evidence()),
            )

            after = db.read_bytes()

            self.assertEqual(before, after)
            self.assert_no_action_authority(result)

    def test_invalid_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            History(journal_path=db, durable_records=True)

            for kwargs in (
                {"cycle_id": 123},
                {"branch_id": None},
                {"effect_id": ""},
                {"expected_source_id": None},
            ):
                options = dict(
                    cycle_id="cycle",
                    branch_id="root",
                    effect_id=EFFECT,
                    expected_source_id=SOURCE,
                )
                options.update(kwargs)

                with self.assertRaises(TypeError):
                    propose_reconciliation(db, **options)

    def test_unknown_evidence_does_not_confirm_effect(self):
        with tempfile.TemporaryDirectory() as folder:
            db = self.database(folder)
            self.running(db)

            result = proposal(
                db,
                verifier=StaticVerifier(
                    evidence(
                        verdict=EvidenceVerdict.UNKNOWN,
                        receipt=None,
                    )
                ),
            )

            self.assertEqual(
                result.decision, Decision.HOLD_UNCONFIRMED
            )
            self.assertIsNone(result.receipt_id)
            self.assert_no_action_authority(result)


if __name__ == "__main__":
    unittest.main()
