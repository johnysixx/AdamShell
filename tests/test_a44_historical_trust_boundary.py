"""A44 historical trust must not authorize new execution."""

import tempfile
import unittest

from dataclasses import replace
from pathlib import Path

from core.existence.history import History
from core.existence.history_receipt_inventory import (
    ReceiptRejectionReason,
    inventory_receipt_observations,
)
from core.existence.history_receipt_proof import (
    ProviderReceiptTrustLifecycle,
    ReceiptKeyStatus,
)
from core.existence.history_receipt_trust_floor import (
    DurableProviderReceiptTrustFloor,
)
from core.existence.history_reconciliation_proposal import (
    EvidenceVerdict,
    ExternalEvidence,
    ProposalDecision,
    propose_reconciliation,
)
from test_a44_versioned_receipt_keys import (
    SOURCE, CYCLE, EFFECT, OLD_KEY, issue, ring,
)


class StaticVerifier:
    def __init__(self, evidence):
        self.evidence = evidence

    def verify(self, **kwargs):
        return self.evidence


def lifecycles():
    initial = ProviderReceiptTrustLifecycle.start(
        {SOURCE: ring(old=ReceiptKeyStatus.ACTIVE)},
        expected_source_ids=(SOURCE,),
        revision=1,
    )
    revoked = initial.advance(
        {SOURCE: ring(old=ReceiptKeyStatus.REVOKED)},
        revision=2,
    )
    return initial, revoked


def evidence_for(receipt):
    return ExternalEvidence(
        cycle_id=CYCLE,
        branch_id="root",
        effect_id=EFFECT,
        source_id=SOURCE,
        verdict=EvidenceVerdict.CONFIRMED,
        receipt_id=receipt.receipt_id,
        signed_receipt=receipt,
    )


def proposal(path, evidence, registry):
    return propose_reconciliation(
        path,
        cycle_id=CYCLE,
        branch_id="root",
        effect_id=EFFECT,
        expected_source_id=SOURCE,
        verifier=StaticVerifier(evidence),
        trusted_provider_keys=registry,
    )


def current_verification(store, lifecycle, receipt):
    return store.verify_current_receipt(
        receipt,
        lifecycle=lifecycle,
        cycle_id=CYCLE,
        branch_id="root",
        effect_id=EFFECT,
        expected_source_id=SOURCE,
        receipt_id=receipt.receipt_id,
    )


class A44HistoricalTrustBoundaryTests(unittest.TestCase):

    def test_historical_v1_v2_remain_review_only(self):
        initial, revoked = lifecycles()

        receipts = (
            issue(version=1, secret=OLD_KEY),
            issue(key_id="k1", secret=OLD_KEY),
        )

        with tempfile.TemporaryDirectory() as folder:
            history_path = Path(folder) / "history.sqlite3"
            trust_path = Path(folder) / "trust.sqlite3"

            history = History(
                journal_path=history_path,
                durable_records=True,
            )
            history.begin_attempt(CYCLE)

            store = DurableProviderReceiptTrustFloor.bootstrap(
                trust_path, initial,
            )
            store.publish(revoked)

            before = history_path.read_bytes()

            for receipt in receipts:
                with self.subTest(
                    receipt_type=type(receipt).__name__
                ):
                    evidence = evidence_for(receipt)

                    report = inventory_receipt_observations(
                        (evidence,),
                        trusted_provider_keys=initial.registry,
                    )

                    self.assertEqual(
                        report.accepted_observations, 1
                    )
                    self.assertFalse(report.retry_allowed)
                    self.assertFalse(report.mutation_allowed)
                    self.assertFalse(
                        report.independent_executions_proven
                    )

                    recommendation = proposal(
                        history_path, evidence, initial.registry
                    )

                    self.assertIs(
                        recommendation.decision,
                        ProposalDecision.REVIEW_EFFECT_CONFIRMED,
                    )
                    self.assertFalse(
                        recommendation.retry_allowed
                    )
                    self.assertFalse(
                        recommendation.mutation_allowed
                    )

                    self.assertIs(
                        current_verification(
                            store, revoked, receipt,
                        ),
                        False,
                    )

                    with self.assertRaises(ValueError):
                        current_verification(
                            store, initial, receipt,
                        )

            self.assertEqual(
                history_path.read_bytes(), before
            )
            self.assertEqual(store.current_revision(), 2)

    def test_invalid_historical_v1_v2_are_rejected(self):
        initial, _ = lifecycles()

        receipts = (
            issue(version=1, secret=OLD_KEY),
            issue(key_id="k1", secret=OLD_KEY),
        )

        with tempfile.TemporaryDirectory() as folder:
            history_path = Path(folder) / "history.sqlite3"

            history = History(
                journal_path=history_path,
                durable_records=True,
            )
            history.begin_attempt(CYCLE)

            for receipt in receipts:
                with self.subTest(
                    receipt_type=type(receipt).__name__
                ):
                    forged = replace(
                        receipt,
                        mac_sha256="0" * 64,
                    )
                    evidence = evidence_for(forged)

                    report = inventory_receipt_observations(
                        (evidence,),
                        trusted_provider_keys=initial.registry,
                    )

                    self.assertEqual(
                        report.accepted_observations, 0
                    )
                    self.assertIs(
                        report.rejected[0].reason,
                        ReceiptRejectionReason.UNVERIFIED_RECEIPT,
                    )
                    self.assertFalse(report.retry_allowed)
                    self.assertFalse(report.mutation_allowed)

                    recommendation = proposal(
                        history_path, evidence, initial.registry
                    )

                    self.assertIs(
                        recommendation.decision,
                        ProposalDecision.HOLD_UNAUTHENTICATED_RECEIPT,
                    )
                    self.assertIsNone(recommendation.receipt_id)
                    self.assertFalse(
                        recommendation.retry_allowed
                    )
                    self.assertFalse(
                        recommendation.mutation_allowed
                    )

    def test_active_current_key_remains_valid(self):
        initial, revoked = lifecycles()

        with tempfile.TemporaryDirectory() as folder:
            trust_path = Path(folder) / "trust.sqlite3"

            store = DurableProviderReceiptTrustFloor.bootstrap(
                trust_path, initial,
            )
            store.publish(revoked)

            self.assertTrue(
                current_verification(
                    store, revoked, issue(),
                )
            )

            self.assertEqual(store.current_revision(), 2)


if __name__ == "__main__":
    unittest.main()
