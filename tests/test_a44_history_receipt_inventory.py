import hashlib
import hmac
import json
import tempfile
import unittest

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

from core.existence.history import History
from core.existence.history_receipt_inventory import (
    ReceiptInventoryFinding as Finding,
    ReceiptRejectionReason as Rejection,
    inventory_receipt_observations,
)
from core.existence.history_receipt_proof import SignedEffectReceipt
from core.existence.history_reconciliation_proposal import (
    EvidenceVerdict,
    ExternalEvidence,
)


SOURCE = "a44-inventory-test-provider"
EFFECT = "effect-A"
KEY = b"A44-INVENTORY-TEST-ONLY-" + b"x" * 32
DOMAIN = b"adam-shell/a44/effect-receipt/v1\x00"


def signed_receipt(
    cycle="cycle",
    branch="root",
    effect=EFFECT,
    source=SOURCE,
    nonce="nonce-001",
    key=KEY,
):
    claims = {
        "version": 1,
        "cycle_id": cycle,
        "branch_id": branch,
        "effect_id": effect,
        "source_id": source,
        "nonce": nonce,
    }

    message = DOMAIN + json.dumps(
        claims,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")

    return SignedEffectReceipt(
        cycle_id=cycle,
        branch_id=branch,
        effect_id=effect,
        source_id=source,
        nonce=nonce,
        receipt_id=(
            "r1-" + hashlib.sha256(message).hexdigest()
        ),
        mac_sha256=hmac.new(
            key,
            message,
            hashlib.sha256,
        ).hexdigest(),
    )


def observation(receipt, **changes):
    return ExternalEvidence(
        cycle_id=changes.get(
            "cycle_id", receipt.cycle_id
        ),
        branch_id=changes.get(
            "branch_id", receipt.branch_id
        ),
        effect_id=changes.get(
            "effect_id", receipt.effect_id
        ),
        source_id=changes.get(
            "source_id", receipt.source_id
        ),
        verdict=changes.get(
            "verdict", EvidenceVerdict.CONFIRMED
        ),
        receipt_id=changes.get(
            "receipt_id", receipt.receipt_id
        ),
        signed_receipt=changes.get(
            "signed_receipt", receipt
        ),
    )


def inventory(*items, keys=None):
    return inventory_receipt_observations(
        items,
        trusted_provider_keys=(
            {SOURCE: KEY} if keys is None else keys
        ),
    )


class A44HistoryReceiptInventoryTests(unittest.TestCase):

    @staticmethod
    def assert_no_authority(report):
        assert report.retry_allowed is False
        assert report.mutation_allowed is False
        assert report.independent_executions_proven is False

    def test_one_valid_receipt(self):
        report = inventory(
            observation(signed_receipt())
        )

        self.assertEqual(len(report.groups), 1)
        self.assertEqual(
            report.groups[0].finding,
            Finding.SINGLE_RECEIPT,
        )
        self.assertEqual(
            report.groups[0].distinct_receipt_count, 1
        )
        self.assertEqual(report.accepted_observations, 1)
        self.assert_no_authority(report)

    def test_same_receipt_observed_twice(self):
        item = observation(signed_receipt())

        report = inventory(item, item)

        self.assertEqual(
            report.groups[0].finding,
            Finding.REOBSERVED_RECEIPT,
        )
        self.assertEqual(
            report.groups[0].observation_count, 2
        )
        self.assertEqual(
            report.groups[0].reobservation_count, 1
        )
        self.assertEqual(
            report.groups[0].distinct_receipt_count, 1
        )
        self.assert_no_authority(report)

    def test_two_different_nonces_same_effect(self):
        first = observation(
            signed_receipt(nonce="nonce-001")
        )
        second = observation(
            signed_receipt(nonce="nonce-002")
        )

        report = inventory(first, second)

        self.assertEqual(
            report.groups[0].finding,
            Finding.MULTIPLE_RECEIPTS,
        )
        self.assertEqual(
            report.groups[0].distinct_receipt_count, 2
        )
        self.assertEqual(
            report.groups[0].reobservation_count, 0
        )
        self.assert_no_authority(report)

    def test_multiple_receipts_with_reobservation(self):
        first = observation(
            signed_receipt(nonce="nonce-001")
        )
        second = observation(
            signed_receipt(nonce="nonce-002")
        )

        report = inventory(first, second, first)

        self.assertEqual(
            report.groups[0].finding,
            Finding.MULTIPLE_RECEIPTS,
        )
        self.assertEqual(
            report.groups[0].observation_count, 3
        )
        self.assertEqual(
            report.groups[0].distinct_receipt_count, 2
        )
        self.assertEqual(
            report.groups[0].reobservation_count, 1
        )

    def test_cross_cycle_reuse_is_rejected(self):
        receipt = signed_receipt(cycle="cycle-A")
        report = inventory(
            observation(receipt, cycle_id="cycle-B")
        )

        self.assertEqual(report.accepted_observations, 0)
        self.assertEqual(
            report.rejected[0].reason,
            Rejection.UNVERIFIED_RECEIPT,
        )

    def test_cross_effect_reuse_is_rejected(self):
        receipt = signed_receipt(effect="effect-A")
        report = inventory(
            observation(receipt, effect_id="effect-B")
        )

        self.assertEqual(
            report.rejected[0].reason,
            Rejection.UNVERIFIED_RECEIPT,
        )

    def test_cross_branch_reuse_is_rejected(self):
        receipt = signed_receipt(branch="root")
        report = inventory(
            observation(receipt, branch_id="fork")
        )

        self.assertEqual(
            report.rejected[0].reason,
            Rejection.UNVERIFIED_RECEIPT,
        )

    def test_wrong_provider_identity_is_rejected(self):
        receipt = signed_receipt()
        report = inventory(
            observation(receipt, source_id="other")
        )

        self.assertEqual(
            report.rejected[0].reason,
            Rejection.UNVERIFIED_RECEIPT,
        )

    def test_bad_mac_is_rejected(self):
        receipt = replace(
            signed_receipt(),
            mac_sha256="0" * 64,
        )

        report = inventory(observation(receipt))

        self.assertEqual(
            report.rejected[0].reason,
            Rejection.UNVERIFIED_RECEIPT,
        )

    def test_changed_nonce_is_rejected(self):
        receipt = replace(
            signed_receipt(),
            nonce="tampered-nonce",
        )

        report = inventory(observation(receipt))

        self.assertEqual(
            report.rejected[0].reason,
            Rejection.UNVERIFIED_RECEIPT,
        )

    def test_unsigned_confirmed_claim_is_rejected(self):
        receipt = signed_receipt()
        unsigned = observation(
            receipt,
            signed_receipt=None,
        )

        report = inventory(unsigned)

        self.assertEqual(report.accepted_observations, 0)
        self.assertEqual(
            report.rejected[0].reason,
            Rejection.UNVERIFIED_RECEIPT,
        )

    def test_negative_claim_does_not_count_as_proof(self):
        receipt = signed_receipt()
        negative = observation(
            receipt,
            verdict=EvidenceVerdict.NOT_FOUND,
        )

        report = inventory(negative)

        self.assertEqual(
            report.rejected[0].reason,
            Rejection.NOT_CONFIRMED,
        )

    def test_unknown_claim_does_not_count_as_proof(self):
        receipt = signed_receipt()
        unknown = observation(
            receipt,
            verdict=EvidenceVerdict.UNKNOWN,
        )

        report = inventory(unknown)

        self.assertEqual(
            report.rejected[0].reason,
            Rejection.NOT_CONFIRMED,
        )

    def test_missing_trusted_key_is_rejected(self):
        report = inventory(
            observation(signed_receipt()),
            keys={},
        )

        self.assertEqual(
            report.rejected[0].reason,
            Rejection.UNVERIFIED_RECEIPT,
        )

    def test_wrong_trusted_key_is_rejected(self):
        report = inventory(
            observation(signed_receipt()),
            keys={SOURCE: b"Z" * 32},
        )

        self.assertEqual(
            report.rejected[0].reason,
            Rejection.UNVERIFIED_RECEIPT,
        )

    def test_malformed_observation_is_rejected(self):
        report = inventory(
            {"receipt_id": "invented"}
        )

        self.assertEqual(
            report.rejected[0].reason,
            Rejection.MALFORMED_OBSERVATION,
        )
        self.assertEqual(report.accepted_observations, 0)

    def test_modified_visible_receipt_id_is_rejected(self):
        receipt = signed_receipt()
        report = inventory(
            observation(receipt, receipt_id="forged")
        )

        self.assertEqual(
            report.rejected[0].reason,
            Rejection.UNVERIFIED_RECEIPT,
        )

    def test_invalid_observation_does_not_poison_valid_group(self):
        good = observation(signed_receipt())
        bad = observation(
            replace(
                signed_receipt(),
                mac_sha256="0" * 64,
            )
        )

        report = inventory(good, bad)

        self.assertEqual(report.total_observations, 2)
        self.assertEqual(report.accepted_observations, 1)
        self.assertEqual(len(report.groups), 1)
        self.assertEqual(len(report.rejected), 1)
        self.assertEqual(
            report.rejected[0].observation_index, 1
        )

    def test_group_order_is_deterministic(self):
        first = observation(
            signed_receipt(cycle="cycle-B")
        )
        second = observation(
            signed_receipt(cycle="cycle-A")
        )

        forward = inventory(first, second)
        reverse = inventory(second, first)

        self.assertEqual(forward.groups, reverse.groups)
        self.assertEqual(
            [item.cycle_id for item in forward.groups],
            ["cycle-A", "cycle-B"],
        )

    def test_distinct_effects_have_separate_groups(self):
        first = observation(
            signed_receipt(effect="effect-A")
        )
        second = observation(
            signed_receipt(effect="effect-B")
        )

        report = inventory(first, second)

        self.assertEqual(len(report.groups), 2)
        self.assertTrue(
            all(
                item.finding is Finding.SINGLE_RECEIPT
                for item in report.groups
            )
        )

    def test_report_is_immutable(self):
        report = inventory(
            observation(signed_receipt())
        )

        with self.assertRaises(FrozenInstanceError):
            report.total_observations = 10

        with self.assertRaises(FrozenInstanceError):
            report.groups[0].observation_count = 10

        self.assertIsInstance(report.groups, tuple)
        self.assertIsInstance(report.rejected, tuple)
        self.assertIsInstance(
            report.groups[0].receipt_ids, tuple
        )

    def test_inventory_does_not_remember_previous_calls(self):
        item = observation(signed_receipt())

        first = inventory(item, item)
        second = inventory(item)

        self.assertEqual(
            first.groups[0].finding,
            Finding.REOBSERVED_RECEIPT,
        )
        self.assertEqual(
            second.groups[0].finding,
            Finding.SINGLE_RECEIPT,
        )
        self.assert_no_authority(first)
        self.assert_no_authority(second)

    def test_history_database_is_untouched(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "history.sqlite3"

            history = History(
                journal_path=db,
                durable_records=True,
            )
            history.begin_attempt("cycle")

            before = db.read_bytes()

            report = inventory(
                observation(signed_receipt())
            )

            after = db.read_bytes()

            self.assertEqual(before, after)
            self.assert_no_authority(report)


if __name__ == "__main__":
    unittest.main()
