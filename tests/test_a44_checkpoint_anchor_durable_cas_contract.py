"""A44 / 66.25B signed monotonic CAS and recovery protocol.

EXPECTED RED: production CAS client does not exist.

Proposed client:
    PinnedSignedCheckpointAnchorCASClient.from_provider(
        provider=provider,
        expected_anchor_id=str,
        expected_anchor_public_key=bytes,
        expected_authority_id=str,
        expected_authority_public_key=bytes,
        expected_root_id=str,
        expected_root_public_key=bytes,
        expected_enrollment_epoch=int,
        minimum_revision=int,
        minimum_generation=int,
        minimum_fence_token=int,
    )

    client.advance_if_current(
        operation_id=32_lowercase_hex_characters,
        expected_revision=int,
        next_revision=int,
        expected_generation=int,
        expected_fence_token=int,
    ) -> eight-field anchor snapshot

    client.lookup_operation(
        operation_id=32_lowercase_hex_characters,
    ) -> (status, eight-field anchor snapshot)

Provider operations:
    advance_if_current(..., challenge=32_bytes)
    lookup_operation(operation_id=..., challenge=32_bytes)

Each response is (canonical_ASCII_JSON, Ed25519_signature).

Common signed document fields:
    domain, version, operation, anchor_id, authority_id,
    authority_public_key_hex, root_id, root_public_key_hex,
    enrollment_epoch, revision, generation, fence_token,
    challenge_hex

CAS adds:
    operation_id, expected_revision, next_revision,
    expected_generation, expected_fence_token, status

Lookup adds:
    operation_id, status

CAS status:
    committed | rejected

Lookup status:
    committed | unknown

Only a signed, validated committed response is an
acknowledgement. A missing response is ambiguous.

An unknown lookup is NOT proof that the CAS never committed.
It is NOT permission for an automatic retry.

The provider model below is volatile and untrusted.
Its tests cannot prove real durability, independent identity
enrollment, backend linearizability, or rollback resistance.

No checkpoint restore or republication is authorized.
"""

import importlib
import sys
import unittest

from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_pinned_anchor_client_contract as contract


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_anchor_cas_client"
)

OPERATION_ID = "a" * 32


class VolatileSignedCASProvider(
    contract.VolatileSignedAnchorProvider
):
    """An in-memory model; NOT durable or independent."""

    def __init__(self, signer, snapshot):
        super().__init__(signer, snapshot)

        self.records = {}
        self.cas_calls = 0
        self.commits = 0
        self.lookup_calls = 0

        self.fail_before_commit = False
        self.fail_after_commit = False

        self.cas_overrides = {}
        self.lookup_overrides = {}

        self.corrupt_cas_signature = False
        self.corrupt_lookup_signature = False
        self.malformed_cas_pair = False

        self.cache_cas_reply = False
        self.cached_cas_reply = None

    def _signed(self, operation, challenge, extra):
        (
            authority_id,
            authority_key,
            root_id,
            root_key,
            epoch,
            revision,
            generation,
            fence,
        ) = self.snapshot

        document = {
            "domain": contract.DOMAIN,
            "version": 1,
            "operation": operation,
            "anchor_id": contract.ANCHOR_ID,
            "authority_id": authority_id,
            "authority_public_key_hex": authority_key.hex(),
            "root_id": root_id,
            "root_public_key_hex": root_key.hex(),
            "enrollment_epoch": epoch,
            "revision": revision,
            "generation": generation,
            "fence_token": fence,
            "challenge_hex": challenge.hex(),
        }

        document.update(extra)

        if operation == "cas":
            document.update(self.cas_overrides)
        elif operation == "lookup":
            document.update(self.lookup_overrides)

        message = contract.canonical(document)
        signature = self.signer.sign(message)

        if (
            operation == "cas"
            and self.corrupt_cas_signature
        ):
            signature = (
                signature[:-1]
                + bytes((signature[-1] ^ 1,))
            )

        if (
            operation == "lookup"
            and self.corrupt_lookup_signature
        ):
            signature = (
                signature[:-1]
                + bytes((signature[-1] ^ 1,))
            )

        response = (message, signature)

        if operation == "cas":
            if (
                self.cache_cas_reply
                and self.cached_cas_reply is not None
            ):
                return self.cached_cas_reply

            if self.cache_cas_reply:
                self.cached_cas_reply = response

            if self.malformed_cas_pair:
                return [message, signature]

        return response

    def advance_if_current(
        self,
        *,
        operation_id,
        expected_revision,
        next_revision,
        expected_generation,
        expected_fence_token,
        challenge,
    ):
        self.cas_calls += 1

        request = (
            expected_revision,
            next_revision,
            expected_generation,
            expected_fence_token,
        )

        if operation_id in self.records:
            recorded_request, _ = self.records[operation_id]

            if recorded_request != request:
                raise ValueError(
                    "Operation ID reused with another request."
                )

            status = "committed"

        else:
            if self.fail_before_commit:
                raise TimeoutError(
                    "Simulated timeout before CAS."
                )

            valid = (
                self.snapshot[5] == expected_revision
                and self.snapshot[6] == expected_generation
                and self.snapshot[7] == expected_fence_token
                and next_revision > expected_revision
            )

            if valid:
                self.snapshot = self.snapshot[:5] + (
                    next_revision,
                    expected_generation + 1,
                    expected_fence_token + 1,
                )

                self.records[operation_id] = (
                    request,
                    self.snapshot,
                )

                self.commits += 1
                status = "committed"

                if self.fail_after_commit:
                    raise TimeoutError(
                        "Simulated lost CAS acknowledgement."
                    )

            else:
                status = "rejected"

        return self._signed(
            "cas",
            challenge,
            {
                "operation_id": operation_id,
                "expected_revision": expected_revision,
                "next_revision": next_revision,
                "expected_generation": expected_generation,
                "expected_fence_token": expected_fence_token,
                "status": status,
            },
        )

    def lookup_operation(
        self,
        *,
        operation_id,
        challenge,
    ):
        self.lookup_calls += 1

        status = (
            "committed"
            if operation_id in self.records
            else "unknown"
        )

        return self._signed(
            "lookup",
            challenge,
            {
                "operation_id": operation_id,
                "status": status,
            },
        )


class A44AnchorDurableCASProtocolContractTests(
    unittest.TestCase
):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.client_type = (
            module.PinnedSignedCheckpointAnchorCASClient
        )

        self.fixture = (
            contract.A44PinnedSignedAnchorClientContractTests(
                "test_01_signed_read_matches_anchor_gate_contract"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.baseline = self.fixture.baseline

        self.provider = VolatileSignedCASProvider(
            self.fixture.anchor_signer,
            self.baseline,
        )

        self.next_revision = self.baseline[5] + 1

        self.advanced = self.baseline[:5] + (
            self.next_revision,
            self.baseline[6] + 1,
            self.baseline[7] + 1,
        )

    def client(self, **changes):
        arguments = {
            "provider": self.provider,
            "expected_anchor_id": contract.ANCHOR_ID,
            "expected_anchor_public_key": self.fixture.anchor_key,
            "expected_authority_id": self.baseline[0],
            "expected_authority_public_key": self.baseline[1],
            "expected_root_id": self.baseline[2],
            "expected_root_public_key": self.baseline[3],
            "expected_enrollment_epoch": self.baseline[4],
            "minimum_revision": self.baseline[5],
            "minimum_generation": self.baseline[6],
            "minimum_fence_token": self.baseline[7],
        }

        arguments.update(changes)

        return self.client_type.from_provider(
            **arguments
        )

    def advance(self, **changes):
        arguments = {
            "operation_id": OPERATION_ID,
            "expected_revision": self.baseline[5],
            "next_revision": self.next_revision,
            "expected_generation": self.baseline[6],
            "expected_fence_token": self.baseline[7],
        }

        arguments.update(changes)

        return self.client().advance_if_current(
            **arguments
        )

    def lookup(self, operation_id=OPERATION_ID):
        return self.client().lookup_operation(
            operation_id=operation_id
        )

    def test_01_successful_cas_and_independent_signed_read(self):
        accepted = self.advance()

        self.assertEqual(
            accepted,
            self.advanced,
        )

        self.assertEqual(self.provider.commits, 1)
        self.assertEqual(self.provider.cas_calls, 1)

        signed_read = self.fixture.source(
            provider=self.provider,
            minimum_revision=self.advanced[5],
            minimum_generation=self.advanced[6],
            minimum_fence_token=self.advanced[7],
        )

        self.assertEqual(
            self.fixture.read(signed_read),
            self.advanced,
        )

    def test_02_stale_cas_rejected_without_mutation(self):
        with self.assertRaises(ValueError):
            self.advance(
                expected_revision=self.baseline[5] + 10
            )

        self.assertEqual(self.provider.commits, 0)
        self.assertEqual(
            self.provider.snapshot,
            self.baseline,
        )

    def test_03_idempotent_duplicate_operation_id(self):
        first = self.advance()
        second = self.advance()

        self.assertEqual(first, second)
        self.assertEqual(first, self.advanced)

        self.assertEqual(self.provider.commits, 1)
        self.assertEqual(self.provider.cas_calls, 2)

    def test_04_same_id_different_request_rejected(self):
        self.advance()

        with self.assertRaises(ValueError):
            self.advance(
                next_revision=self.next_revision + 1
            )

        self.assertEqual(self.provider.commits, 1)
        self.assertEqual(
            self.provider.snapshot,
            self.advanced,
        )

    def test_05_lost_ack_reconciled_by_signed_lookup(self):
        self.provider.fail_after_commit = True

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(self.provider.commits, 1)
        self.assertEqual(self.provider.cas_calls, 1)

        status, snapshot = self.lookup()

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.advanced)

        self.assertEqual(self.provider.cas_calls, 1)

    def test_06_timeout_before_commit_not_auto_retried(self):
        self.provider.fail_before_commit = True

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(self.provider.commits, 0)
        self.assertEqual(self.provider.cas_calls, 1)

        status, snapshot = self.lookup()

        self.assertEqual(status, "unknown")
        self.assertEqual(snapshot, self.baseline)

        self.assertEqual(self.provider.cas_calls, 1)

    def test_07_unknown_lookup_is_not_commit_evidence(self):
        status, snapshot = self.lookup()

        self.assertEqual(status, "unknown")
        self.assertEqual(snapshot, self.baseline)

        self.assertEqual(self.provider.cas_calls, 0)
        self.assertEqual(self.provider.commits, 0)

        # Unknown is not an automatic retry permit.

    def test_08_invalid_signed_cas_signature_rejected(self):
        self.provider.corrupt_cas_signature = True

        with self.assertRaises(ValueError):
            self.advance()

        # Invalid acknowledgement does not imply rollback.
        self.assertEqual(self.provider.commits, 1)

        self.provider.corrupt_cas_signature = False

        status, snapshot = self.lookup()

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.advanced)

        self.assertEqual(self.provider.cas_calls, 1)

    def test_09_signed_cas_request_binding_mismatch(self):
        self.provider.cas_overrides = {
            "expected_revision": self.baseline[5] + 5
        }

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(self.provider.commits, 1)
        self.assertEqual(self.provider.cas_calls, 1)

        status, snapshot = self.lookup()

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.advanced)

    def test_10_invalid_signed_lookup_rejected(self):
        self.provider.corrupt_lookup_signature = True

        with self.assertRaises(ValueError):
            self.lookup()

        self.provider.corrupt_lookup_signature = False

        for field, value in (
            ("status", "not_committed"),
            ("operation_id", "b" * 32),
            ("challenge_hex", "0" * 64),
        ):
            with self.subTest(field=field):
                self.provider.lookup_overrides = {
                    field: value
                }

                with self.assertRaises(ValueError):
                    self.lookup()

        self.assertEqual(self.provider.commits, 0)
        self.assertEqual(self.provider.cas_calls, 0)

    def test_11_invalid_requests_fail_before_provider(self):
        attacks = (
            {"operation_id": "invalid"},
            {"operation_id": "A" * 32},
            {"operation_id": "a" * 31},
            {"expected_revision": True},
            {"next_revision": self.baseline[5]},
            {"expected_generation": False},
            {"expected_fence_token": -1},
        )

        for changes in attacks:
            with self.subTest(changes=repr(changes)):
                with self.assertRaises(ValueError):
                    self.advance(**changes)

        self.assertEqual(self.provider.cas_calls, 0)
        self.assertEqual(self.provider.commits, 0)

    def test_12_malformed_signed_cas_pair_rejected(self):
        self.provider.malformed_cas_pair = True

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(self.provider.commits, 1)

        self.provider.malformed_cas_pair = False

        status, snapshot = self.lookup()

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.advanced)

    def test_13_wrong_anchor_pin_rejected(self):
        rogue = Ed25519PrivateKey.generate()

        rogue_public = contract.raw_public_key(
            rogue
        )

        client = self.client(
            expected_anchor_public_key=rogue_public
        )

        with self.assertRaises(ValueError):
            client.advance_if_current(
                operation_id=OPERATION_ID,
                expected_revision=self.baseline[5],
                next_revision=self.next_revision,
                expected_generation=self.baseline[6],
                expected_fence_token=self.baseline[7],
            )

        # The backend could already have committed.
        self.assertEqual(self.provider.commits, 1)

        status, snapshot = self.lookup()

        self.assertEqual(status, "committed")
        self.assertEqual(snapshot, self.advanced)

    def test_14_signed_cas_receipt_replay_rejected(self):
        self.provider.cache_cas_reply = True

        self.assertEqual(
            self.advance(),
            self.advanced,
        )

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(self.provider.commits, 1)
        self.assertEqual(self.provider.cas_calls, 2)

    def test_15_volatile_provider_cannot_prove_durability(self):
        """KNOWN LIMIT: signed volatile state can roll back."""

        self.advance()

        self.assertEqual(
            self.provider.snapshot,
            self.advanced,
        )

        self.provider.snapshot = self.baseline
        self.provider.records.clear()

        stale_signed_read = self.fixture.source(
            provider=self.provider
        )

        self.assertEqual(
            self.fixture.read(stale_signed_read),
            self.baseline,
        )

        # Caller-supplied high-water floors could reject this.
        # The volatile provider itself cannot protect them.


if __name__ == "__main__":
    unittest.main()
