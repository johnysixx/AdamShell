"""A44 / 66.25D signed CAS adversarial recovery tests.

All providers are volatile test doubles.

Covered:
- timeouts before and after a commit
- signed operation lookup and ambiguous outcomes
- malformed, forged and replayed responses
- conflicting operation IDs and stale CAS requests
- explicit limits of dishonest signed providers
- caller-held floors against simulated state rollback

Security limits:
- This suite cannot prove crash durability or true remote CAS.
- A valid signature does not prove an honest backend.
- Unknown lookup never authorizes automatic retry.
- Caller-supplied trust pins are not trusted enrollment.
- No cross-store atomicity, restoration or republication.
"""

import sys
import unittest

from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_anchor_durable_cas_contract as contract

from core.existence import (
    history_receipt_trust_checkpoint_pinned_anchor_client
    as signed_read
)


class A44AnchorCASAdversarialRecoveryTests(unittest.TestCase):

    def setUp(self):
        self.fixture = (
            contract.A44AnchorDurableCASProtocolContractTests(
                "test_01_successful_cas_and_independent_signed_read"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.provider = self.fixture.provider
        self.baseline = self.fixture.baseline
        self.advanced = self.fixture.advanced
        self.operation_id = contract.OPERATION_ID

    def advance(self, **changes):
        return self.fixture.advance(**changes)

    def lookup(self, operation_id=None):
        if operation_id is None:
            operation_id = self.operation_id

        return self.fixture.lookup(
            operation_id=operation_id
        )

    def test_01_timeout_before_commit_never_auto_retries(self):
        self.provider.fail_before_commit = True

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(self.provider.cas_calls, 1)
        self.assertEqual(self.provider.commits, 0)

        status, snapshot = self.lookup()

        self.assertEqual(status, "unknown")
        self.assertEqual(snapshot, self.baseline)
        self.assertEqual(self.provider.cas_calls, 1)

    def test_02_lost_ack_recovered_by_signed_lookup(self):
        self.provider.fail_after_commit = True

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(self.provider.cas_calls, 1)
        self.assertEqual(self.provider.commits, 1)

        status, snapshot = self.lookup()

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.advanced)
        self.assertEqual(self.provider.cas_calls, 1)

    def test_03_lookup_timeout_preserves_ambiguous_state(self):
        self.provider.fail_after_commit = True

        with self.assertRaises(ValueError):
            self.advance()

        with patch.object(
            self.provider,
            "lookup_operation",
            side_effect=TimeoutError("Simulated lookup timeout."),
        ):
            with self.assertRaises(ValueError):
                self.lookup()

        self.assertEqual(self.provider.cas_calls, 1)
        self.assertEqual(self.provider.commits, 1)

        status, snapshot = self.lookup()

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.advanced)

    def test_04_new_client_can_lookup_existing_operation(self):
        self.provider.fail_after_commit = True

        with self.assertRaises(ValueError):
            self.advance()

        new_client = self.fixture.client()

        status, snapshot = new_client.lookup_operation(
            operation_id=self.operation_id
        )

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.advanced)
        self.assertEqual(self.provider.cas_calls, 1)

    def test_05_invalid_lookup_signature_after_lost_ack(self):
        self.provider.fail_after_commit = True

        with self.assertRaises(ValueError):
            self.advance()

        self.provider.corrupt_lookup_signature = True

        with self.assertRaises(ValueError):
            self.lookup()

        self.provider.corrupt_lookup_signature = False

        status, snapshot = self.lookup()

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.advanced)
        self.assertEqual(self.provider.commits, 1)

    def test_06_repeated_unknown_lookup_never_calls_cas(self):
        missing_id = "b" * 32

        for _ in range(2):
            status, snapshot = self.lookup(
                operation_id=missing_id
            )

            self.assertEqual(status, "unknown")
            self.assertEqual(snapshot, self.baseline)

        self.assertEqual(self.provider.lookup_calls, 2)
        self.assertEqual(self.provider.cas_calls, 0)
        self.assertEqual(self.provider.commits, 0)

    def test_07_signed_lookup_wrong_operation_id_rejected(self):
        self.provider.lookup_overrides = {
            "operation_id": "b" * 32
        }

        with self.assertRaises(ValueError):
            self.lookup()

        self.assertEqual(self.provider.cas_calls, 0)

    def test_08_signed_lookup_wrong_challenge_rejected(self):
        self.provider.lookup_overrides = {
            "challenge_hex": "0" * 64
        }

        with patch.object(
            signed_read.os,
            "urandom",
            return_value=b"\x01" * 32,
        ):
            with self.assertRaises(ValueError):
                self.lookup()

        self.assertEqual(self.provider.cas_calls, 0)

    def test_09_signed_lookup_wrong_root_identity_rejected(self):
        self.provider.lookup_overrides = {
            "root_id": "forged-root"
        }

        with self.assertRaises(ValueError):
            self.lookup()

        self.assertEqual(self.provider.cas_calls, 0)

    def test_10_signed_lookup_extra_json_field_rejected(self):
        self.provider.lookup_overrides = {
            "unexpected_field": True
        }

        with self.assertRaises(ValueError):
            self.lookup()

        self.assertEqual(self.provider.cas_calls, 0)

    def test_11_dishonest_signed_commit_lookup_is_accepted(self):
        """KNOWN LIMIT: signer can lie about a missing record."""

        self.provider.lookup_overrides = {
            "status": "committed"
        }

        status, snapshot = self.lookup()

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.baseline)

        self.assertNotIn(
            self.operation_id,
            self.provider.records,
        )

        self.assertEqual(self.provider.commits, 0)
        self.assertEqual(self.provider.cas_calls, 0)

    def test_12_dishonest_signed_unknown_lookup_is_accepted(self):
        """KNOWN LIMIT: signer can deny a committed record."""

        self.assertEqual(
            self.advance(),
            self.advanced,
        )

        self.provider.lookup_overrides = {
            "status": "unknown"
        }

        status, snapshot = self.lookup()

        self.assertEqual(status, "unknown")
        self.assertEqual(snapshot, self.advanced)

        self.assertIn(
            self.operation_id,
            self.provider.records,
        )

        self.assertEqual(self.provider.commits, 1)

    def test_13_false_signed_cas_rejection_after_commit(self):
        self.provider.cas_overrides = {
            "status": "rejected"
        }

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(self.provider.commits, 1)
        self.assertEqual(self.provider.cas_calls, 1)

        status, snapshot = self.lookup()

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.advanced)

    def test_14_signed_cas_wrong_operation_id_rejected(self):
        self.provider.cas_overrides = {
            "operation_id": "b" * 32
        }

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(self.provider.commits, 1)

        status, snapshot = self.lookup()

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.advanced)

    def test_15_signed_cas_request_binding_tampered(self):
        self.provider.cas_overrides = {
            "expected_generation": self.baseline[6] + 3
        }

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(self.provider.commits, 1)

        status, snapshot = self.lookup()

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.advanced)

    def test_16_cached_signed_cas_ack_replay_rejected(self):
        self.provider.cache_cas_reply = True

        first = self.advance()

        self.assertEqual(first, self.advanced)

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(self.provider.cas_calls, 2)
        self.assertEqual(self.provider.commits, 1)

    def test_17_same_operation_id_different_request_rejected(self):
        self.assertEqual(
            self.advance(),
            self.advanced,
        )

        with self.assertRaises(ValueError):
            self.advance(
                next_revision=self.fixture.next_revision + 1
            )

        self.assertEqual(self.provider.cas_calls, 2)
        self.assertEqual(self.provider.commits, 1)

        self.assertEqual(
            self.provider.snapshot,
            self.advanced,
        )

    def test_18_competing_operation_with_stale_state_rejected(self):
        self.assertEqual(
            self.advance(),
            self.advanced,
        )

        other_id = "b" * 32

        with self.assertRaises(ValueError):
            self.advance(
                operation_id=other_id
            )

        self.assertEqual(self.provider.cas_calls, 2)
        self.assertEqual(self.provider.commits, 1)

        status, snapshot = self.lookup(
            operation_id=other_id
        )

        self.assertEqual(status, "unknown")
        self.assertEqual(snapshot, self.advanced)

    def test_19_resigned_noncanonical_cas_ack_rejected(self):
        original_signed = self.provider._signed
        signer = self.fixture.fixture.anchor_signer

        def noncanonical(operation, challenge, extra):
            response = original_signed(
                operation,
                challenge,
                extra,
            )

            if operation != "cas":
                return response

            message, _ = response

            modified = message + b" "

            return (
                modified,
                signer.sign(modified),
            )

        with patch.object(
            self.provider,
            "_signed",
            side_effect=noncanonical,
        ):
            with self.assertRaises(ValueError):
                self.advance()

        self.assertEqual(self.provider.commits, 1)
        self.assertEqual(self.provider.cas_calls, 1)

        status, snapshot = self.lookup()

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.advanced)

    def test_20_pinned_high_water_rejects_rolled_back_lookup(self):
        self.assertEqual(
            self.advance(),
            self.advanced,
        )

        # Simulate rollback of an unprotected backend.
        self.provider.snapshot = self.baseline
        self.provider.records.clear()

        pinned_client = self.fixture.client(
            minimum_revision=self.advanced[5],
            minimum_generation=self.advanced[6],
            minimum_fence_token=self.advanced[7],
        )

        with self.assertRaises(ValueError):
            pinned_client.lookup_operation(
                operation_id=self.operation_id
            )

        self.assertEqual(self.provider.cas_calls, 1)
        self.assertEqual(self.provider.commits, 1)


if __name__ == "__main__":
    unittest.main()
