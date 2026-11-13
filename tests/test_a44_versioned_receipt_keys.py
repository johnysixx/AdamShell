"""A44 regression tests for pinned receipt signing-key generations."""

import hashlib
import hmac
import json
import tempfile
import unittest

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

from core.existence.history import History
from core.existence.history_receipt_inventory import (
    ReceiptInventoryFinding,
    ReceiptRejectionReason,
    inventory_receipt_observations,
)
from core.existence.history_receipt_proof import (
    ProviderReceiptKeyRing,
    ReceiptKeyStatus,
    SignedEffectReceipt,
    TrustedReceiptKey,
    VersionedSignedEffectReceipt,
    verify_signed_receipt,
)
from core.existence.history_reconciliation_proposal import (
    EvidenceVerdict,
    ExternalEvidence,
    ProposalDecision,
    propose_reconciliation,
)


SOURCE = "a44-key-rotation-test-provider"
CYCLE = "rotation-cycle"
EFFECT = "payment-effect"
OLD_KEY = b"A44-OLD-TEST-ONLY-" + b"x" * 32
NEW_KEY = b"A44-NEW-TEST-ONLY-" + b"y" * 32
OTHER_KEY = b"A44-OTHER-TEST-ONLY-" + b"z" * 32


def issue(*, version=2, key_id="k2", secret=NEW_KEY,
          source=SOURCE, cycle=CYCLE, branch="root",
          effect=EFFECT, nonce="nonce-001"):
    payload = {
        "version": version,
        "cycle_id": cycle,
        "branch_id": branch,
        "effect_id": effect,
        "source_id": source,
        "nonce": nonce,
    }

    if version == 2:
        payload["key_id"] = key_id

    wire = (
        f"adam-shell/a44/effect-receipt/v{version}\x00".encode("ascii")
        + json.dumps(
            payload, sort_keys=True, ensure_ascii=True,
            separators=(",", ":"),
        ).encode("ascii")
    )

    common = dict(
        cycle_id=cycle,
        branch_id=branch,
        effect_id=effect,
        source_id=source,
        nonce=nonce,
        receipt_id=f"r{version}-" + hashlib.sha256(wire).hexdigest(),
        mac_sha256=hmac.new(secret, wire, hashlib.sha256).hexdigest(),
    )

    if version == 1:
        return SignedEffectReceipt(**common)

    return VersionedSignedEffectReceipt(**common, key_id=key_id)


def ring(*, old=ReceiptKeyStatus.VERIFY_ONLY,
         new=ReceiptKeyStatus.ACTIVE, legacy="k1"):
    return ProviderReceiptKeyRing(
        keys=(
            TrustedReceiptKey("k1", OLD_KEY, old),
            TrustedReceiptKey("k2", NEW_KEY, new),
        ),
        legacy_key_id=legacy,
    )


def valid(receipt, keyring=None):
    keys = {SOURCE: ring() if keyring is None else keyring}
    return verify_signed_receipt(
        receipt,
        cycle_id=CYCLE,
        branch_id="root",
        effect_id=EFFECT,
        expected_source_id=SOURCE,
        receipt_id=receipt.receipt_id,
        trusted_provider_keys=keys,
    )


def evidence(receipt):
    return ExternalEvidence(
        cycle_id=receipt.cycle_id,
        branch_id=receipt.branch_id,
        effect_id=receipt.effect_id,
        source_id=receipt.source_id,
        verdict=EvidenceVerdict.CONFIRMED,
        receipt_id=receipt.receipt_id,
        signed_receipt=receipt,
    )


class StaticVerifier:
    def __init__(self, item):
        self.item = item

    def verify(self, **kwargs):
        return self.item


class A44VersionedReceiptKeyTests(unittest.TestCase):

    def test_v2_active_key_verifies(self):
        self.assertTrue(valid(issue()))

    def test_v2_verify_only_key_verifies_historical_proof(self):
        receipt = issue(key_id="k1", secret=OLD_KEY)
        self.assertTrue(valid(receipt))

    def test_v2_revoked_key_is_rejected(self):
        self.assertFalse(valid(issue(), ring(new=ReceiptKeyStatus.REVOKED)))

    def test_v2_unknown_key_id_is_rejected(self):
        self.assertFalse(valid(issue(key_id="unknown")))

    def test_v2_wrong_pinned_key_fails(self):
        changed = ProviderReceiptKeyRing(
            keys=(TrustedReceiptKey(
                "k2", OTHER_KEY, ReceiptKeyStatus.ACTIVE,
            ),),
        )
        self.assertFalse(valid(issue(), changed))

    def test_v2_key_id_tampering_fails(self):
        altered = replace(issue(), key_id="k1")
        self.assertFalse(valid(altered))

    def test_v2_key_identity_changes_receipt_hash(self):
        a = issue(key_id="k1", secret=OLD_KEY)
        b = issue(key_id="k2", secret=NEW_KEY)
        self.assertNotEqual(a.receipt_id, b.receipt_id)

    def test_v2_modified_nonce_fails(self):
        self.assertFalse(valid(replace(issue(), nonce="modified")))

    def test_v2_modified_mac_fails(self):
        self.assertFalse(valid(replace(issue(), mac_sha256="0" * 64)))

    def test_v2_raw_legacy_key_is_not_a_trust_registry(self):
        self.assertFalse(valid(issue(), NEW_KEY))

    def test_v2_cross_cycle_claim_fails(self):
        self.assertFalse(valid(issue(cycle="another-cycle")))

    def test_v2_cross_effect_claim_fails(self):
        self.assertFalse(valid(issue(effect="another-effect")))

    def test_v2_cross_branch_claim_fails(self):
        self.assertFalse(valid(issue(branch="fork")))

    def test_v2_cross_provider_claim_fails(self):
        self.assertFalse(valid(issue(source="other-provider")))

    def test_v2_wrong_visible_receipt_id_fails(self):
        receipt = issue()
        self.assertFalse(verify_signed_receipt(
            receipt,
            cycle_id=CYCLE,
            branch_id="root",
            effect_id=EFFECT,
            expected_source_id=SOURCE,
            receipt_id="forged",
            trusted_provider_keys={SOURCE: ring()},
        ))

    def test_v2_invalid_key_id_is_rejected(self):
        self.assertFalse(valid(issue(key_id="bad/key")))

    def test_v2_duplicate_key_id_fails_closed(self):
        duplicated = ProviderReceiptKeyRing(keys=(
            TrustedReceiptKey("k2", NEW_KEY, ReceiptKeyStatus.ACTIVE),
            TrustedReceiptKey("k2", OTHER_KEY, ReceiptKeyStatus.VERIFY_ONLY),
        ))
        self.assertFalse(valid(issue(), duplicated))

    def test_v2_invalid_key_status_fails_closed(self):
        malformed = ProviderReceiptKeyRing(keys=(
            TrustedReceiptKey("k2", NEW_KEY, "active"),
        ))
        self.assertFalse(valid(issue(), malformed))

    def test_v2_short_provider_secret_fails_closed(self):
        malformed = ProviderReceiptKeyRing(keys=(
            TrustedReceiptKey("k2", b"short", ReceiptKeyStatus.ACTIVE),
        ))
        self.assertFalse(valid(issue(), malformed))

    def test_v2_non_tuple_registry_fails_closed(self):
        malformed = ProviderReceiptKeyRing(keys=[
            TrustedReceiptKey("k2", NEW_KEY, ReceiptKeyStatus.ACTIVE),
        ])
        self.assertFalse(valid(issue(), malformed))

    def test_v1_raw_bytes_key_is_rejected(self):
        self.assertFalse(valid(
            issue(version=1, secret=OLD_KEY),
            OLD_KEY,
        ))

    def test_v1_raw_bytes_rejected_by_inventory(self):
        receipt = issue(version=1, secret=OLD_KEY)
        report = inventory_receipt_observations(
            [evidence(receipt)],
            trusted_provider_keys={SOURCE: OLD_KEY},
        )
        self.assertEqual(report.accepted_observations, 0)
        self.assertEqual(
            report.rejected[0].reason,
            ReceiptRejectionReason.UNVERIFIED_RECEIPT,
        )

    def test_v1_explicit_legacy_key_verifies(self):
        self.assertTrue(valid(
            issue(version=1, secret=OLD_KEY),
            ring(),
        ))

    def test_v1_missing_legacy_key_binding_fails(self):
        self.assertFalse(valid(
            issue(version=1, secret=OLD_KEY),
            ring(legacy=None),
        ))

    def test_v1_wrong_legacy_binding_fails(self):
        self.assertFalse(valid(
            issue(version=1, secret=OLD_KEY),
            ring(legacy="k2"),
        ))

    def test_v1_revoked_legacy_key_fails(self):
        self.assertFalse(valid(
            issue(version=1, secret=OLD_KEY),
            ring(old=ReceiptKeyStatus.REVOKED),
        ))

    def test_v1_unknown_legacy_key_fails(self):
        self.assertFalse(valid(
            issue(version=1, secret=OLD_KEY),
            ring(legacy="missing"),
        ))

    def test_new_and_old_receipts_are_domain_separated(self):
        old = issue(version=1, secret=OLD_KEY)
        new = issue(version=2, key_id="k1", secret=OLD_KEY)
        self.assertNotEqual(old.receipt_id, new.receipt_id)

    def test_trusted_registry_is_frozen(self):
        config = ring()
        with self.assertRaises(FrozenInstanceError):
            config.legacy_key_id = "k2"
        with self.assertRaises(FrozenInstanceError):
            config.keys[0].status = ReceiptKeyStatus.REVOKED
        self.assertIsInstance(config.keys, tuple)

    def test_v2_proposal_returns_review_without_write_authority(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.sqlite3"
            History(journal_path=db, durable_records=True).begin_attempt(CYCLE)
            before = db.read_bytes()
            receipt = issue()
            result = propose_reconciliation(
                db, cycle_id=CYCLE, branch_id="root",
                effect_id=EFFECT, expected_source_id=SOURCE,
                verifier=StaticVerifier(evidence(receipt)),
                trusted_provider_keys={SOURCE: ring()},
            )
            self.assertEqual(
                result.decision, ProposalDecision.REVIEW_EFFECT_CONFIRMED,
            )
            self.assertEqual(result.receipt_id, receipt.receipt_id)
            self.assertFalse(result.retry_allowed)
            self.assertFalse(result.mutation_allowed)
            self.assertEqual(before, db.read_bytes())

    def test_revoked_v2_proposal_is_held(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.sqlite3"
            History(journal_path=db, durable_records=True).begin_attempt(CYCLE)
            result = propose_reconciliation(
                db, cycle_id=CYCLE, branch_id="root",
                effect_id=EFFECT, expected_source_id=SOURCE,
                verifier=StaticVerifier(evidence(issue())),
                trusted_provider_keys={
                    SOURCE: ring(new=ReceiptKeyStatus.REVOKED),
                },
            )
            self.assertEqual(
                result.decision,
                ProposalDecision.HOLD_UNAUTHENTICATED_RECEIPT,
            )
            self.assertIsNone(result.receipt_id)
            self.assertFalse(result.retry_allowed)

    def test_versioned_inventory_groups_are_read_only(self):
        old = issue(version=1, secret=OLD_KEY)
        new = issue()
        report = inventory_receipt_observations(
            [evidence(old), evidence(new), evidence(old)],
            trusted_provider_keys={SOURCE: ring()},
        )
        self.assertEqual(report.accepted_observations, 3)
        self.assertEqual(report.groups[0].distinct_receipt_count, 2)
        self.assertEqual(report.groups[0].observation_count, 3)
        self.assertEqual(report.groups[0].reobservation_count, 1)
        self.assertEqual(
            report.groups[0].finding,
            ReceiptInventoryFinding.MULTIPLE_RECEIPTS,
        )
        self.assertFalse(report.independent_executions_proven)
        self.assertFalse(report.retry_allowed)
        self.assertFalse(report.mutation_allowed)

    def test_revoked_inventory_evidence_is_rejected(self):
        report = inventory_receipt_observations(
            [evidence(issue())],
            trusted_provider_keys={
                SOURCE: ring(new=ReceiptKeyStatus.REVOKED),
            },
        )
        self.assertEqual(report.accepted_observations, 0)
        self.assertEqual(len(report.rejected), 1)
        self.assertEqual(
            report.rejected[0].reason,
            ReceiptRejectionReason.UNVERIFIED_RECEIPT,
        )


if __name__ == "__main__":
    unittest.main()
