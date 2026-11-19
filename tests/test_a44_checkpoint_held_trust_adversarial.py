"""Adversarial tests for held checkpoint trust verification.

The supplied trust source is not authenticated by this adapter.
These tests examine lifecycle, key changes, concurrency and
fail-closed handling of misbehaving context managers.

Two tests intentionally expose suppressed-error handling.
No private keys are persisted; no Universe restoration occurs.
"""

import hashlib
import json
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from threading import Event, RLock
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

import test_a44_checkpoint_held_trust as contract

from core.existence.history_receipt_trust_checkpoint_attestation import (
    PinnedCronenbergCheckpointAttestationVerifier,
)
from core.existence.history_receipt_trust_cronenberg_checkpoint import (
    CanonicalCronenbergStateCheckpoint,
)


AUTHORITY = contract.AUTHORITY
GENERATION = contract.GENERATION


def raw_public(key):
    return key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def rehash_checkpoint(payload):
    body = {
        key: value
        for key, value in payload.items()
        if key != "checkpoint_sha256"
    }

    canonical = json.dumps(
        body,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")

    payload["checkpoint_sha256"] = hashlib.sha256(
        canonical
    ).hexdigest()

    return payload


class LockedSource:
    """Volatile test fixture with a genuine in-process lock.

    This lock serializes a test rotation but is not a
    durable or independently authenticated trust root.
    """

    def __init__(self, snapshot):
        self.lock = RLock()
        self.snapshot = snapshot
        self.active = False
        self.events = []

    @contextmanager
    def hold(self):
        with self.lock:
            self.active = True
            self.events.append("enter")

            try:
                yield self.snapshot
            finally:
                self.events.append("exit")
                self.active = False

    def replace(self, snapshot):
        with self.lock:
            self.snapshot = snapshot
            self.events.append("rotate")


class A44CheckpointHeldTrustAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        # Reuse the exact canonical incident/checkpoint
        # fixture exercised by the existing 12-test contract.
        self.harness = (
            contract.A44CheckpointHeldTrustContractTests(
                "test_valid_held_snapshot_verifies_data_only"
            )
        )

        self.harness.setUp()
        self.addCleanup(self.harness.doCleanups)

    def test_regular_held_verification_remains_non_authoritative(self):
        result = self.harness.verify()

        self.assertTrue(result.signature_verified)
        self.assertFalse(result.is_authoritative)
        self.assertFalse(result.is_restorable)
        self.assertFalse(result.can_republish)

        self.assertEqual(
            self.harness.source.events,
            ["enter", "exit"],
        )
        self.assertFalse(self.harness.source.active)

    def test_provider_enter_failure_rejected(self):
        class EnterFailure:
            def hold(self):
                raise OSError("Injected trust-source enter failure")

        with self.assertRaises(ValueError):
            self.harness.verify(EnterFailure())

    def test_provider_property_access_failure_rejected(self):
        class HostileProvider:
            @property
            def hold(self):
                raise OSError("Injected hold property failure")

        with self.assertRaises(ValueError):
            self.harness.verify(HostileProvider())

    def test_rotated_public_key_rejects_old_signature(self):
        message, original_signature = self.harness.signed()

        replacement = Ed25519PrivateKey.generate()

        source = contract.MemoryHeldTrustSource(
            (AUTHORITY, raw_public(replacement), GENERATION - 1)
        )

        with self.assertRaises(ValueError):
            self.harness.verify(
                source,
                message=message,
                signature=original_signature,
            )

        accepted_source = contract.MemoryHeldTrustSource(
            (AUTHORITY, raw_public(replacement), GENERATION - 1)
        )

        result = self.harness.verify(
            accepted_source,
            message=message,
            signature=replacement.sign(message),
        )

        self.assertTrue(result.signature_verified)
        self.assertFalse(result.is_authoritative)
        self.assertEqual(
            accepted_source.events,
            ["enter", "exit"],
        )

    def test_advanced_generation_floor_rejects_replay(self):
        stale_source = contract.MemoryHeldTrustSource(
            (AUTHORITY, self.harness.public, GENERATION)
        )

        with self.assertRaises(ValueError):
            self.harness.verify(stale_source)

        self.assertEqual(
            stale_source.events,
            ["enter", "exit"],
        )

        previous_source = contract.MemoryHeldTrustSource(
            (AUTHORITY, self.harness.public, GENERATION - 1)
        )

        result = self.harness.verify(previous_source)

        self.assertEqual(result.generation, GENERATION)
        self.assertFalse(result.is_authoritative)

    def test_exit_failure_after_valid_verification_rejected(self):
        class ExitFailure:
            def __init__(self, snapshot):
                self.snapshot = snapshot
                self.events = []

            @contextmanager
            def hold(self):
                self.events.append("enter")
                try:
                    yield self.snapshot
                finally:
                    self.events.append("exit")
                    raise OSError("Injected trust-source exit failure")

        source = ExitFailure(
            (AUTHORITY, self.harness.public, GENERATION - 1)
        )

        with self.assertRaises(ValueError):
            self.harness.verify(source)

        self.assertEqual(
            source.events,
            ["enter", "exit"],
        )

    def test_tuple_subclass_snapshot_is_rejected(self):
        class MisleadingTuple(tuple):
            pass

        source = contract.MemoryHeldTrustSource(
            MisleadingTuple(
                (AUTHORITY, self.harness.public, GENERATION - 1)
            )
        )

        with self.assertRaises(ValueError):
            self.harness.verify(source)

        self.assertEqual(
            source.events,
            ["enter", "exit"],
        )

    def test_injected_verifier_failure_releases_lease(self):
        source = contract.MemoryHeldTrustSource(
            (AUTHORITY, self.harness.public, GENERATION - 1)
        )

        def injected_failure(verifier, **kwargs):
            self.assertTrue(source.active)
            raise ValueError("Injected Ed25519 verification failure")

        with patch.object(
            PinnedCronenbergCheckpointAttestationVerifier,
            "verify",
            new=injected_failure,
        ):
            with self.assertRaises(ValueError):
                self.harness.verify(source)

        self.assertEqual(
            source.events,
            ["enter", "exit"],
        )
        self.assertFalse(source.active)

    def test_rehashed_checkpoint_forgery_rejected(self):
        payload = self.harness.checkpoint.to_dict()
        payload["entity_state"]["energy"] += 3.0

        forged = CanonicalCronenbergStateCheckpoint.parse_untrusted(
            rehash_checkpoint(payload)
        )

        with self.assertRaises(ValueError):
            self.harness.verify(checkpoint=forged)

        self.assertFalse(forged.is_authoritative)
        self.assertFalse(forged.is_restorable)

    def test_concurrent_rotation_waits_for_held_verification(self):
        source = LockedSource(
            (AUTHORITY, self.harness.public, GENERATION - 1)
        )

        new_key = Ed25519PrivateKey.generate()
        new_snapshot = (
            AUTHORITY,
            raw_public(new_key),
            GENERATION,
        )

        entered_verifier = Event()
        release_verifier = Event()
        rotation_started = Event()

        original = (
            PinnedCronenbergCheckpointAttestationVerifier.verify
        )

        def paused_verification(verifier, **kwargs):
            self.assertTrue(source.active)
            entered_verifier.set()

            if not release_verifier.wait(timeout=10):
                raise ValueError("Injected verifier timeout")

            return original(verifier, **kwargs)

        def rotate():
            rotation_started.set()
            source.replace(new_snapshot)

        with patch.object(
            PinnedCronenbergCheckpointAttestationVerifier,
            "verify",
            new=paused_verification,
        ):
            with ThreadPoolExecutor(max_workers=2) as pool:
                verified_future = pool.submit(
                    self.harness.verify,
                    source,
                )

                try:
                    self.assertTrue(
                        entered_verifier.wait(timeout=10)
                    )

                    rotation_future = pool.submit(rotate)

                    self.assertTrue(
                        rotation_started.wait(timeout=10)
                    )

                    self.assertFalse(rotation_future.done())

                    # The lock is owned by the verification
                    # worker and cannot be acquired here.
                    acquired = source.lock.acquire(blocking=False)

                    if acquired:
                        source.lock.release()

                    self.assertFalse(acquired)

                finally:
                    release_verifier.set()

                result = verified_future.result(timeout=10)
                rotation_future.result(timeout=10)

        self.assertTrue(result.signature_verified)
        self.assertFalse(result.is_authoritative)

        self.assertEqual(
            source.events,
            ["enter", "exit", "rotate"],
        )

        self.assertEqual(source.snapshot, new_snapshot)

        # The rotated key and higher generation now reject
        # replay of the previous signed attestation.
        with self.assertRaises(ValueError):
            self.harness.verify(source)

    def test_suppressed_signature_failure_must_raise(self):
        class SuppressingSource:
            @contextmanager
            def hold(self):
                try:
                    yield (
                        AUTHORITY,
                        self_public,
                        GENERATION - 1,
                    )
                except ValueError:
                    # Hostile provider suppresses the
                    # failed Ed25519 verification.
                    pass

        self_public = self.harness.public

        attacker = Ed25519PrivateKey.generate()
        message, _ = self.harness.signed()
        bad_signature = attacker.sign(message)

        # SECURITY REQUIREMENT:
        # Suppressing __exit__ must not make a failed
        # verification return None as if it completed.
        with self.assertRaises(ValueError):
            self.harness.verify(
                SuppressingSource(),
                message=message,
                signature=bad_signature,
            )

    def test_suppressed_snapshot_failure_must_raise(self):
        class SuppressingMalformedSource:
            @contextmanager
            def hold(self):
                try:
                    # A malformed 3-byte public key
                    # must fail before verifier creation.
                    yield (
                        AUTHORITY,
                        b"bad",
                        GENERATION - 1,
                    )
                except ValueError:
                    # Suppress the snapshot validation error.
                    pass

        # SECURITY REQUIREMENT:
        # Provider exception suppression must not turn
        # invalid trust state into an implicit None result.
        with self.assertRaises(ValueError):
            self.harness.verify(
                SuppressingMalformedSource()
            )


if __name__ == "__main__":
    unittest.main()
