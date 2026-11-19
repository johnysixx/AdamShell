"""A44 split checkpoint trust source contract.

EXPECTED RED: checkpoint_source_binding module is absent.

The adapter composes TWO externally supplied held sources:
    key_source.hold()        -> (authority_id, public_key)
    generation_source.hold() -> (authority_id, exclusive_floor)

Both leases must remain active throughout checkpoint
signature verification by the existing held-trust gate.

This contract does not establish independent provenance,
durable monotonic storage, authorization, or isolation
against arbitrary malicious code in the Python process.
"""

import importlib
import sys
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from threading import Event, RLock
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_a44_checkpoint_held_trust as contract

from core.existence.history_receipt_trust_checkpoint_attestation import (
    PinnedCronenbergCheckpointAttestationVerifier,
)


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_source_binding"
)

AUTHORITY = contract.AUTHORITY
GENERATION = contract.GENERATION


def public_key(private_key):
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


class HeldSource:
    """Test-only volatile provider with a held RLock."""

    def __init__(self, snapshot, *, fail_enter=None, fail_exit=None):
        self.snapshot = snapshot
        self.fail_enter = fail_enter
        self.fail_exit = fail_exit
        self.lock = RLock()
        self.active = False
        self.events = []

    @contextmanager
    def hold(self):
        with self.lock:
            self.events.append("enter")

            if self.fail_enter is not None:
                raise self.fail_enter

            self.active = True

            try:
                yield self.snapshot
            finally:
                self.active = False
                self.events.append("exit")

                if self.fail_exit is not None:
                    raise self.fail_exit

    def replace(self, snapshot):
        with self.lock:
            self.snapshot = snapshot
            self.events.append("replace")


class SuppressingSource(HeldSource):
    """Malicious __exit__ suppresses ValueError from its body."""

    @contextmanager
    def hold(self):
        with self.lock:
            self.events.append("enter")
            self.active = True

            try:
                yield self.snapshot
            except ValueError:
                self.events.append("suppressed")
            finally:
                self.active = False
                self.events.append("exit")


class A44CheckpointSourceBindingContractTests(unittest.TestCase):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.source_type = module.SplitCheckpointTrustSource

        self.fixture = (
            contract.A44CheckpointHeldTrustContractTests(
                "test_valid_held_snapshot_verifies_data_only"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.key_source = HeldSource(
            (AUTHORITY, self.fixture.public)
        )

        self.generation_source = HeldSource(
            (AUTHORITY, GENERATION - 1)
        )

    def make_source(self, key_source=None, generation_source=None):
        return self.source_type.from_sources(
            key_source=(
                self.key_source if key_source is None else key_source
            ),
            generation_source=(
                self.generation_source
                if generation_source is None
                else generation_source
            ),
            expected_authority_id=AUTHORITY,
        )

    def verify(self, source=None, **kwargs):
        if source is None:
            source = self.make_source()

        return self.fixture.verify(source, **kwargs)

    def assert_released(self, key_source, generation_source):
        self.assertFalse(key_source.active)
        self.assertFalse(generation_source.active)

    def test_matching_dual_lease_snapshot(self):
        source = self.make_source()

        with source.hold() as snapshot:
            self.assertEqual(
                snapshot,
                (AUTHORITY, self.fixture.public, GENERATION - 1),
            )
            self.assertIs(type(snapshot), tuple)
            self.assertTrue(self.key_source.active)
            self.assertTrue(self.generation_source.active)

        self.assert_released(
            self.key_source,
            self.generation_source,
        )

        self.assertEqual(
            self.key_source.events,
            ["enter", "exit"],
        )
        self.assertEqual(
            self.generation_source.events,
            ["enter", "exit"],
        )

    def test_both_leases_cover_signature_verification(self):
        source = self.make_source()

        original = (
            PinnedCronenbergCheckpointAttestationVerifier.verify
        )

        observations = []

        def guarded_verification(verifier, **kwargs):
            observations.append((
                self.key_source.active,
                self.generation_source.active,
                kwargs["minimum_generation"],
            ))

            self.assertTrue(self.key_source.active)
            self.assertTrue(self.generation_source.active)

            return original(verifier, **kwargs)

        with patch.object(
            PinnedCronenbergCheckpointAttestationVerifier,
            "verify",
            new=guarded_verification,
        ):
            result = self.verify(source)

        self.assertTrue(result.signature_verified)
        self.assertFalse(result.is_authoritative)
        self.assertFalse(result.is_restorable)
        self.assertFalse(result.can_republish)

        self.assertEqual(observations, [(True, True, 7)])

        self.assert_released(
            self.key_source,
            self.generation_source,
        )

    def test_missing_source_or_hold_rejected(self):
        class MissingHold:
            pass

        for key_source, generation_source in (
            (None, self.generation_source),
            (MissingHold(), self.generation_source),
            (object(), self.generation_source),
            (self.key_source, None),
            (self.key_source, MissingHold()),
            (self.key_source, object()),
        ):
            with self.subTest(
                key=type(key_source).__name__,
                generation=type(generation_source).__name__,
            ):
                with self.assertRaises(ValueError):
                    source = self.source_type.from_sources(
                        key_source=key_source,
                        generation_source=generation_source,
                        expected_authority_id=AUTHORITY,
                    )

                    with source.hold():
                        pass

    def test_malformed_key_snapshot_rejected(self):
        snapshots = (
            None,
            (),
            [],
            {},
            (AUTHORITY,),
            (AUTHORITY, self.fixture.public, "extra"),
            [AUTHORITY, self.fixture.public],
            "invalid",
        )

        for snapshot in snapshots:
            with self.subTest(snapshot=repr(snapshot)[:60]):
                key = HeldSource(snapshot)
                source = self.make_source(key_source=key)

                with self.assertRaises(ValueError):
                    with source.hold():
                        pass

                self.assert_released(
                    key,
                    self.generation_source,
                )

    def test_malformed_generation_snapshot_rejected(self):
        snapshots = (
            None,
            (),
            [],
            {},
            (AUTHORITY,),
            (AUTHORITY, 7, "extra"),
            [AUTHORITY, 7],
            "invalid",
        )

        for snapshot in snapshots:
            with self.subTest(snapshot=repr(snapshot)[:60]):
                generation = HeldSource(snapshot)
                source = self.make_source(
                    generation_source=generation
                )

                with self.assertRaises(ValueError):
                    with source.hold():
                        pass

                self.assert_released(
                    self.key_source,
                    generation,
                )

    def test_invalid_or_foreign_authority_rejected(self):
        invalid = (
            None,
            "",
            True,
            "foreign_authority",
            " checkpoint_authority_v1",
        )

        for authority in invalid:
            with self.subTest(authority=repr(authority)):
                key = HeldSource(
                    (authority, self.fixture.public)
                )

                source = self.make_source(key_source=key)

                with self.assertRaises(ValueError):
                    with source.hold():
                        pass

                generation = HeldSource(
                    (authority, 7)
                )

                source = self.make_source(
                    generation_source=generation
                )

                with self.assertRaises(ValueError):
                    with source.hold():
                        pass

    def test_invalid_public_key_rejected(self):
        for key_bytes in (
            None,
            "",
            bytearray(self.fixture.public),
            self.fixture.public[:-1],
            b"",
            True,
        ):
            with self.subTest(key=type(key_bytes).__name__):
                key = HeldSource((AUTHORITY, key_bytes))
                source = self.make_source(key_source=key)

                with self.assertRaises(ValueError):
                    self.verify(source)

                self.assert_released(
                    key,
                    self.generation_source,
                )

    def test_invalid_generation_floor_rejected(self):
        for floor in (
            None,
            -1,
            True,
            False,
            7.0,
            "7",
        ):
            with self.subTest(floor=repr(floor)):
                generation = HeldSource(
                    (AUTHORITY, floor)
                )

                source = self.make_source(
                    generation_source=generation
                )

                with self.assertRaises(ValueError):
                    self.verify(source)

                self.assert_released(
                    self.key_source,
                    generation,
                )

    def test_signature_and_exit_failure_release_both(self):
        attacker = Ed25519PrivateKey.generate()
        message, _ = self.fixture.signed()

        with self.assertRaises(ValueError):
            self.verify(
                message=message,
                signature=attacker.sign(message),
            )

        self.assert_released(
            self.key_source,
            self.generation_source,
        )

        failing_floor = HeldSource(
            (AUTHORITY, 7),
            fail_exit=OSError("Injected floor backend exit failure"),
        )

        with self.assertRaises(ValueError):
            self.verify(
                self.make_source(
                    generation_source=failing_floor
                )
            )

        self.assert_released(
            self.key_source,
            failing_floor,
        )

    def test_rotation_waits_for_both_held_leases(self):
        source = self.make_source()

        entered_verifier = Event()
        release_verifier = Event()
        rotation_started = Event()

        original = (
            PinnedCronenbergCheckpointAttestationVerifier.verify
        )

        def paused_verification(verifier, **kwargs):
            self.assertTrue(self.key_source.active)
            self.assertTrue(self.generation_source.active)
            entered_verifier.set()

            if not release_verifier.wait(timeout=10):
                raise ValueError("Test verifier timeout")

            return original(verifier, **kwargs)

        new_key = Ed25519PrivateKey.generate()

        def rotate_both():
            rotation_started.set()
            self.key_source.replace(
                (AUTHORITY, public_key(new_key))
            )
            self.generation_source.replace(
                (AUTHORITY, GENERATION)
            )

        with patch.object(
            PinnedCronenbergCheckpointAttestationVerifier,
            "verify",
            new=paused_verification,
        ):
            with ThreadPoolExecutor(max_workers=2) as pool:
                verification = pool.submit(self.verify, source)

                try:
                    self.assertTrue(
                        entered_verifier.wait(timeout=10)
                    )

                    rotation = pool.submit(rotate_both)

                    self.assertTrue(
                        rotation_started.wait(timeout=10)
                    )

                    self.assertFalse(rotation.done())

                    key_acquired = self.key_source.lock.acquire(
                        blocking=False
                    )

                    if key_acquired:
                        self.key_source.lock.release()

                    floor_acquired = (
                        self.generation_source.lock.acquire(
                            blocking=False
                        )
                    )

                    if floor_acquired:
                        self.generation_source.lock.release()

                    self.assertFalse(key_acquired)
                    self.assertFalse(floor_acquired)

                finally:
                    release_verifier.set()

                result = verification.result(timeout=10)
                rotation.result(timeout=10)

        self.assertTrue(result.signature_verified)
        self.assertFalse(result.is_authoritative)

        with self.assertRaises(ValueError):
            self.verify(source)

    def test_external_floor_rollback_is_not_protected_here(self):
        source = self.make_source()

        self.generation_source.replace(
            (AUTHORITY, GENERATION)
        )

        with self.assertRaises(ValueError):
            self.verify(source)

        # Deliberately simulate an untrusted provider rolling
        # its generation floor back to zero. A composition
        # adapter must NOT claim to prevent this.
        self.generation_source.replace(
            (AUTHORITY, 0)
        )

        result = self.verify(source)

        self.assertTrue(result.signature_verified)
        self.assertEqual(result.generation, GENERATION)
        self.assertFalse(result.is_authoritative)
        self.assertFalse(result.is_restorable)
        self.assertFalse(result.can_republish)

    def test_suppressed_source_errors_fail_closed(self):
        for source_kind in ("key", "generation"):
            with self.subTest(source_kind=source_kind):
                if source_kind == "key":
                    key = SuppressingSource(
                        (AUTHORITY, b"invalid")
                    )
                    generation = HeldSource(
                        (AUTHORITY, 7)
                    )
                else:
                    key = HeldSource(
                        (AUTHORITY, self.fixture.public)
                    )
                    generation = SuppressingSource(
                        (AUTHORITY, -1)
                    )

                source = self.source_type.from_sources(
                    key_source=key,
                    generation_source=generation,
                    expected_authority_id=AUTHORITY,
                )

                with self.assertRaises(ValueError):
                    self.verify(source)

                self.assert_released(key, generation)


if __name__ == "__main__":
    unittest.main()
