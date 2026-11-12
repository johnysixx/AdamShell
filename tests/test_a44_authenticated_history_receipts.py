import hashlib
import hmac
import json
import tempfile
import unittest

from dataclasses import replace
from pathlib import Path

from core.actualization.possibility import (
    Possibility,
    PossibilityActualizedEvent,
)
from core.actualization.potential import Potential
from core.existence.cycle_runner import ExistenceCycleRunner
from core.existence.history import History
from core.existence.history_receipt_proof import (
    SignedEffectReceipt,
)
from core.existence.history_reconciliation_proposal import (
    EvidenceVerdict,
    ExternalEvidence,
    ProposalDecision as Decision,
    propose_reconciliation,
)
from core.existence.reality import Reality


SOURCE = "a44-trusted-test-provider"
EFFECT = "effect-A"
KEY = b"A44-TEST-ONLY-" + b"x" * 32
DOMAIN = b"adam-shell/a44/effect-receipt/v1\x00"


def sign_receipt(
    cycle="cycle",
    branch="root",
    effect=EFFECT,
    source=SOURCE,
    nonce="nonce-001",
    secret=KEY,
):
    payload = {
        "version": 1,
        "cycle_id": cycle,
        "branch_id": branch,
        "effect_id": effect,
        "source_id": source,
        "nonce": nonce,
    }

    wire = DOMAIN + json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")

    return SignedEffectReceipt(
        cycle_id=cycle,
        branch_id=branch,
        effect_id=effect,
        source_id=source,
        nonce=nonce,
        receipt_id="r1-" + hashlib.sha256(wire).hexdigest(),
        mac_sha256=hmac.new(
            secret,
            wire,
            hashlib.sha256,
        ).hexdigest(),
    )


def signed_evidence(receipt, **overrides):
    return ExternalEvidence(
        cycle_id=overrides.get("cycle", receipt.cycle_id),
        branch_id=overrides.get("branch", receipt.branch_id),
        effect_id=overrides.get("effect", receipt.effect_id),
        source_id=overrides.get("source", receipt.source_id),
        verdict=EvidenceVerdict.CONFIRMED,
        receipt_id=overrides.get(
            "receipt_id",
            receipt.receipt_id,
        ),
        signed_receipt=receipt,
    )


class StaticVerifier:
    def __init__(self, evidence):
        self.evidence = evidence

    def verify(self, **kwargs):
        return self.evidence


class Process:
    def generate_potentials(self, cycle_id):
        return [
            Potential(
                possibility=Possibility(
                    name="authenticated",
                    probability=1.0,
                    mandatory=True,
                    action=lambda: PossibilityActualizedEvent(
                        name="authenticated_event"
                    ),
                ),
                cycle_id=cycle_id,
            )
        ]


class A44AuthenticatedReceiptTests(unittest.TestCase):

    @staticmethod
    def begin(db, *cycles):
        history = History(
            journal_path=db,
            durable_records=True,
        )

        for cycle in cycles:
            history.begin_attempt(cycle)

        return history

    @staticmethod
    def propose(db, cycle, evidence, keys=None):
        result = propose_reconciliation(
            db,
            cycle_id=cycle,
            branch_id="root",
            effect_id=EFFECT,
            expected_source_id=SOURCE,
            verifier=StaticVerifier(evidence),
            trusted_provider_keys=keys,
        )

        assert result.retry_allowed is False
        assert result.mutation_allowed is False
        return result

    def test_valid_signed_running_receipt_is_review_only(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.db"
            self.begin(db, "cycle")
            receipt = sign_receipt()

            result = self.propose(
                db,
                "cycle",
                signed_evidence(receipt),
                {SOURCE: KEY},
            )

            self.assertEqual(
                result.decision,
                Decision.REVIEW_EFFECT_CONFIRMED,
            )
            self.assertEqual(result.receipt_id, receipt.receipt_id)

    def test_valid_signed_completed_receipt_is_review_only(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.db"
            history = History(
                journal_path=db,
                durable_records=True,
            )

            reality = Reality()
            self.assertTrue(
                reality.add_natural_process(Process())
            )

            ExistenceCycleRunner(
                reality=reality,
                history=history,
            ).run("cycle")

            receipt = sign_receipt()

            result = self.propose(
                db,
                "cycle",
                signed_evidence(receipt),
                {SOURCE: KEY},
            )

            self.assertEqual(
                result.decision,
                Decision.REVIEW_ARCHIVED_COMPLETED,
            )

    def test_fabricated_unsigned_receipt_is_held(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.db"
            self.begin(db, "cycle")

            fabricated = ExternalEvidence(
                cycle_id="cycle",
                branch_id="root",
                effect_id=EFFECT,
                source_id=SOURCE,
                verdict=EvidenceVerdict.CONFIRMED,
                receipt_id="invented",
            )

            result = self.propose(
                db,
                "cycle",
                fabricated,
                {SOURCE: KEY},
            )

            self.assertEqual(
                result.decision,
                Decision.HOLD_UNAUTHENTICATED_RECEIPT,
            )
            self.assertIsNone(result.receipt_id)

    def test_bad_mac_is_held(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.db"
            self.begin(db, "cycle")

            receipt = replace(
                sign_receipt(),
                mac_sha256="0" * 64,
            )

            result = self.propose(
                db,
                "cycle",
                signed_evidence(receipt),
                {SOURCE: KEY},
            )

            self.assertEqual(
                result.decision,
                Decision.HOLD_UNAUTHENTICATED_RECEIPT,
            )

    def test_changed_nonce_breaks_authentication(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.db"
            self.begin(db, "cycle")

            receipt = replace(
                sign_receipt(),
                nonce="altered",
            )

            result = self.propose(
                db,
                "cycle",
                signed_evidence(receipt),
                {SOURCE: KEY},
            )

            self.assertEqual(
                result.decision,
                Decision.HOLD_UNAUTHENTICATED_RECEIPT,
            )

    def test_copied_receipt_cannot_confirm_another_cycle(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.db"
            self.begin(db, "cycle_a", "cycle_b")

            receipt = sign_receipt(cycle="cycle_a")
            copied = signed_evidence(
                receipt,
                cycle="cycle_b",
            )

            result = self.propose(
                db,
                "cycle_b",
                copied,
                {SOURCE: KEY},
            )

            self.assertEqual(
                result.decision,
                Decision.HOLD_UNAUTHENTICATED_RECEIPT,
            )

    def test_distinct_cycles_have_distinct_receipt_ids(self):
        first = sign_receipt(
            cycle="cycle_a",
            nonce="same-nonce",
        )
        second = sign_receipt(
            cycle="cycle_b",
            nonce="same-nonce",
        )

        self.assertNotEqual(
            first.receipt_id,
            second.receipt_id,
        )

    def test_wrong_effect_in_signed_claim_is_held(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.db"
            self.begin(db, "cycle")

            receipt = sign_receipt(effect="different")
            claimed = signed_evidence(
                receipt,
                effect=EFFECT,
            )

            result = self.propose(
                db,
                "cycle",
                claimed,
                {SOURCE: KEY},
            )

            self.assertEqual(
                result.decision,
                Decision.HOLD_UNAUTHENTICATED_RECEIPT,
            )

    def test_wrong_source_in_signed_claim_is_held(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.db"
            self.begin(db, "cycle")

            receipt = sign_receipt(
                source="untrusted-provider"
            )

            claimed = signed_evidence(
                receipt,
                source=SOURCE,
            )

            result = self.propose(
                db,
                "cycle",
                claimed,
                {SOURCE: KEY},
            )

            self.assertEqual(
                result.decision,
                Decision.HOLD_UNAUTHENTICATED_RECEIPT,
            )

    def test_missing_or_wrong_key_is_held(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.db"
            self.begin(db, "cycle")

            claim = signed_evidence(sign_receipt())

            for keys in (
                None,
                {},
                {SOURCE: b"short"},
                {SOURCE: b"Z" * 32},
            ):
                result = self.propose(
                    db,
                    "cycle",
                    claim,
                    keys,
                )

                self.assertEqual(
                    result.decision,
                    Decision.HOLD_UNAUTHENTICATED_RECEIPT,
                )

    def test_negative_evidence_cannot_carry_proof(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.db"
            self.begin(db, "cycle")

            evidence = ExternalEvidence(
                cycle_id="cycle",
                branch_id="root",
                effect_id=EFFECT,
                source_id=SOURCE,
                verdict=EvidenceVerdict.NOT_FOUND,
                signed_receipt=sign_receipt(),
            )

            result = self.propose(
                db,
                "cycle",
                evidence,
                {SOURCE: KEY},
            )

            self.assertEqual(
                result.decision,
                Decision.HOLD_INVALID_EVIDENCE,
            )

    def test_visible_receipt_id_mismatch_is_held(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.db"
            self.begin(db, "cycle")

            receipt = sign_receipt()

            claimed = signed_evidence(
                receipt,
                receipt_id="different-id",
            )

            result = self.propose(
                db,
                "cycle",
                claimed,
                {SOURCE: KEY},
            )

            self.assertEqual(
                result.decision,
                Decision.HOLD_UNAUTHENTICATED_RECEIPT,
            )

    def test_authenticated_proposal_does_not_modify_journal(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.db"
            self.begin(db, "cycle")

            before = db.read_bytes()

            result = self.propose(
                db,
                "cycle",
                signed_evidence(sign_receipt()),
                {SOURCE: KEY},
            )

            after = db.read_bytes()

            self.assertEqual(before, after)
            self.assertFalse(result.retry_allowed)
            self.assertFalse(result.mutation_allowed)


if __name__ == "__main__":
    unittest.main()
