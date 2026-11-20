"""A44 signed checkpoint backend-source integration contract.

EXPECTED RED: signed_backend_source module absent.

Proposed public API:

    SignedCheckpointRootFloorSource.from_backend(
        backend=backend,
        expected_backend_id=str,
        expected_backend_public_key=bytes,
        expected_root_id=str,
        expected_root_public_key=bytes,
        minimum_revision=int,
    )

    source.hold() -> context manager yielding:
        (root_id, root_public_key, revision)

    source.advance(
        expected_revision=int,
        next_revision=int,
    ) -> resulting three-element root snapshot

Required external backend API:

    backend.hold(challenge=bytes32) ->
        context manager yielding (message, signature)

    backend.advance_if_current(
        expected_revision=int,
        next_revision=int,
        challenge=bytes32,
    ) -> (message, signature)

All replies must pass the existing Ed25519 evidence verifier.

A successful CAS acknowledgement MUST be followed by a
separate freshly challenged signed readback.

The source is duck-type compatible with the existing
checkpoint witness rotation coordinator.

SECURITY LIMITATIONS:

- Both backend and root keys remain caller-supplied pins.
- A valid signature cannot prove genuine backend execution.
- Signed readback cannot prove durable persistence.
- No independent trusted revision floor is introduced.
- No durable rollback resistance is established.
- Cross-backend atomicity is not provided.
- No checkpoint restore or republication authority exists.

All backends below are volatile TEST DOUBLES.
"""

import importlib
import json
import os
import sys
import unittest

from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_root_floor_cas as cas_contract
import test_a44_checkpoint_rotation_coordinator as rotation_contract


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_signed_backend_source"
)

DOMAIN = "AdamShell/A44/checkpoint-backend-evidence/v1"

BACKEND_ID = "signed_checkpoint_backend_test_v1"
ROOT = cas_contract.ROOT

OLD = cas_contract.REVISION - 1
NEXT = cas_contract.REVISION

_BACKEND_UNSET = object()


def public_bytes(private):
    return private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def canonical(document):
    return json.dumps(
        document,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


class SignedMemoryBackend:
    """Volatile signing test double, not a trusted backend."""

    def __init__(
        self,
        *,
        root_public,
        signer,
        revision=OLD,
    ):
        self.root_id = ROOT
        self.root_public = root_public
        self.signer = signer
        self.revision = revision

        self.lock = RLock()
        self.active = False

        self.read_calls = 0
        self.cas_calls = 0

        self.read_challenges = []
        self.cas_challenges = []
        self.events = []

        self.read_mode = None
        self.cas_mode = None
        self.read_mode_after_cas = None

        self.fake_ack = False
        self.commit_then_fail = False
        self.suppress_errors = False

        self.fail_on_read_number = None
        self.last_read_pair = None
        self.stale_revision = None

    def _signed(
        self,
        *,
        operation,
        challenge,
        revision,
        expected_revision=None,
        next_revision=None,
        mode=None,
    ):
        document = {
            "domain": DOMAIN,
            "version": 1,
            "operation": operation,
            "backend_id": BACKEND_ID,
            "root_id": self.root_id,
            "root_public_key_hex": self.root_public.hex(),
            "revision": revision,
            "challenge_hex": challenge.hex(),
        }

        if operation == "cas":
            document.update({
                "expected_revision": expected_revision,
                "next_revision": next_revision,
            })

        if mode == "legacy":
            return (
                self.root_id,
                self.root_public,
                revision,
            )

        if mode == "malformed_pair":
            return (b"incomplete",)

        if mode == "wrong_backend":
            document["backend_id"] = "foreign_backend"

        if mode == "wrong_root":
            document["root_id"] = "foreign_root"

        if mode == "wrong_root_key":
            document["root_public_key_hex"] = "00" * 32

        if mode == "wrong_challenge":
            document["challenge_hex"] = (
                bytes([challenge[0] ^ 1])
                + challenge[1:]
            ).hex()

        if mode == "wrong_operation":
            document["operation"] = (
                "cas" if operation == "read" else "read"
            )

        if mode == "wrong_predecessor":
            document["expected_revision"] = (
                expected_revision + 1
            )

        message = canonical(document)

        if mode == "noncanonical":
            message += b"\n"

        signature = self.signer.sign(message)

        if mode == "bad_signature":
            signature = (
                bytes([signature[0] ^ 1])
                + signature[1:]
            )

        return message, signature

    @contextmanager
    def hold(self, *, challenge):
        with self.lock:
            self.read_calls += 1
            self.read_challenges.append(challenge)
            self.events.append("read_enter")
            self.active = True

            try:
                if self.fail_on_read_number == self.read_calls:
                    raise OSError(
                        "Injected readback transport failure."
                    )

                if (
                    self.read_mode == "replay"
                    and self.last_read_pair is not None
                ):
                    reply = self.last_read_pair

                else:
                    revision = self.revision

                    if self.read_mode == "stale":
                        revision = self.stale_revision

                    reply = self._signed(
                        operation="read",
                        challenge=challenge,
                        revision=revision,
                        mode=self.read_mode,
                    )

                    self.last_read_pair = reply

                try:
                    yield reply

                except ValueError:
                    if not self.suppress_errors:
                        raise

            finally:
                self.active = False
                self.events.append("read_exit")

    def advance_if_current(
        self,
        *,
        expected_revision,
        next_revision,
        challenge,
    ):
        with self.lock:
            self.cas_calls += 1
            self.cas_challenges.append(challenge)
            self.events.append("cas")

            if (
                type(expected_revision) is not int
                or type(next_revision) is not int
                or self.revision != expected_revision
                or next_revision <= expected_revision
            ):
                raise ValueError(
                    "Test backend CAS predecessor mismatch."
                )

            self.stale_revision = self.revision

            if not self.fake_ack:
                self.revision = next_revision

            if self.commit_then_fail:
                raise OSError(
                    "Injected failure after CAS publication."
                )

            if self.read_mode_after_cas is not None:
                self.read_mode = self.read_mode_after_cas

            return self._signed(
                operation="cas",
                challenge=challenge,
                revision=next_revision,
                expected_revision=expected_revision,
                next_revision=next_revision,
                mode=self.cas_mode,
            )


class A44CheckpointSignedBackendSourceContractTests(
    unittest.TestCase
):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.source_type = (
            module.SignedCheckpointRootFloorSource
        )

        self.backend_private = Ed25519PrivateKey.generate()
        self.root_private = Ed25519PrivateKey.generate()

        self.backend_public = public_bytes(
            self.backend_private
        )

        self.root_public = public_bytes(
            self.root_private
        )

        self.backend = self.make_backend()
        self.source = self.make_source()

    def make_backend(self, *, root_public=None, revision=OLD):
        return SignedMemoryBackend(
            root_public=(
                self.root_public
                if root_public is None
                else root_public
            ),
            signer=self.backend_private,
            revision=revision,
        )

    def make_source(self, backend=_BACKEND_UNSET, **changes):
        arguments = {
            "backend": (
                self.backend if backend is _BACKEND_UNSET else backend
            ),
            "expected_backend_id": BACKEND_ID,
            "expected_backend_public_key":
                self.backend_public,
            "expected_root_id": ROOT,
            "expected_root_public_key":
                self.root_public,
            "minimum_revision": OLD,
        }

        arguments.update(changes)

        return self.source_type.from_backend(**arguments)

    def test_signed_held_read_keeps_lease(self):
        with self.source.hold() as snapshot:
            self.assertEqual(
                snapshot,
                (ROOT, self.root_public, OLD),
            )
            self.assertTrue(self.backend.active)

        self.assertFalse(self.backend.active)
        self.assertEqual(self.backend.read_calls, 1)
        self.assertEqual(self.backend.cas_calls, 0)

        self.assertIs(
            type(self.backend.read_challenges[0]),
            bytes,
        )

        self.assertEqual(
            len(self.backend.read_challenges[0]),
            32,
        )

    def test_signed_cas_and_distinct_readback_challenges(self):
        result = self.source.advance(
            expected_revision=OLD,
            next_revision=NEXT,
        )

        self.assertEqual(
            result,
            (ROOT, self.root_public, NEXT),
        )

        self.assertEqual(self.backend.revision, NEXT)
        self.assertEqual(self.backend.cas_calls, 1)
        self.assertGreaterEqual(self.backend.read_calls, 1)

        self.assertNotEqual(
            self.backend.cas_challenges[0],
            self.backend.read_challenges[0],
        )

        self.assertFalse(self.backend.active)

        with self.source.hold() as snapshot:
            self.assertEqual(snapshot[2], NEXT)

    def test_coordinator_accepts_signed_root_source(self):
        fixture = (
            rotation_contract.A44CheckpointRotationCoordinatorContractTests(
                "test_ready_observation_holds_sources_and_is_data_only"
            )
        )

        fixture.setUp()
        self.addCleanup(fixture.doCleanups)

        backend = self.make_backend(
            root_public=fixture.cas.public,
            revision=rotation_contract.OLD_FLOOR,
        )

        root = self.make_source(
            backend=backend,
            expected_root_public_key=fixture.cas.public,
            minimum_revision=rotation_contract.OLD_FLOOR,
        )

        coordinator = fixture.make_coordinator(
            root_source=root
        )

        result = fixture.rotate(coordinator)

        self.assertEqual(
            result.state,
            "observed_advanced",
        )

        fixture.assert_data_only(result)

        self.assertEqual(
            backend.revision,
            rotation_contract.NEXT_FLOOR,
        )

        self.assertEqual(
            fixture.store.snapshot,
            fixture.next_pair,
        )

        self.assertFalse(backend.active)
        self.assertFalse(fixture.store.active)

    def test_missing_backend_capability_or_pin_rejected(self):
        class ReadOnly:
            def hold(self, *, challenge):
                raise AssertionError(
                    "Should not enter read."
                )

        class WriteOnly:
            def advance_if_current(self, **kwargs):
                raise AssertionError(
                    "Should not execute CAS."
                )

        invalid = (
            {"backend": None},
            {"backend": object()},
            {"backend": ReadOnly()},
            {"backend": WriteOnly()},
            {"expected_backend_id": ""},
            {"expected_backend_id": True},
            {"expected_backend_public_key": b""},
            {"expected_backend_public_key":
                 bytearray(self.backend_public)},
            {"expected_root_id": ""},
            {"expected_root_public_key": b""},
            {"expected_root_public_key":
                 bytearray(self.root_public)},
            {"minimum_revision": -1},
            {"minimum_revision": True},
            {"minimum_revision": "12"},
        )

        for changes in invalid:
            with self.subTest(changes=repr(changes)[:70]):
                with self.assertRaises(ValueError):
                    self.make_source(**changes)

        self.assertEqual(self.backend.cas_calls, 0)

    def test_stale_floor_and_invalid_cas_preconditions(self):
        elevated = self.make_source(
            minimum_revision=NEXT
        )

        with self.assertRaises(ValueError):
            with elevated.hold():
                pass

        with self.assertRaises(ValueError):
            elevated.advance(
                expected_revision=OLD,
                next_revision=NEXT,
            )

        invalid = (
            (True, NEXT),
            (-1, NEXT),
            (OLD, False),
            (OLD, OLD),
            (OLD, OLD - 1),
            ("12", NEXT),
            (OLD, "13"),
            (OLD, 13.0),
        )

        for previous, target in invalid:
            with self.subTest(
                previous=repr(previous),
                target=repr(target),
            ):
                with self.assertRaises(ValueError):
                    self.source.advance(
                        expected_revision=previous,
                        next_revision=target,
                    )

        self.assertEqual(self.backend.cas_calls, 0)
        self.assertEqual(self.backend.revision, OLD)
        self.assertFalse(self.backend.active)

    def test_unsigned_or_malformed_held_read_rejected(self):
        modes = (
            "legacy",
            "malformed_pair",
            "bad_signature",
            "noncanonical",
            "wrong_operation",
        )

        for mode in modes:
            with self.subTest(mode=mode):
                backend = self.make_backend()
                backend.read_mode = mode

                source = self.make_source(
                    backend=backend
                )

                with self.assertRaises(ValueError):
                    with source.hold():
                        pass

                self.assertFalse(backend.active)
                self.assertEqual(backend.cas_calls, 0)

    def test_signed_read_identity_and_challenge_attacks_rejected(
        self
    ):
        modes = (
            "wrong_backend",
            "wrong_root",
            "wrong_root_key",
            "wrong_challenge",
        )

        for mode in modes:
            with self.subTest(mode=mode):
                backend = self.make_backend()
                backend.read_mode = mode

                source = self.make_source(
                    backend=backend
                )

                with self.assertRaises(ValueError):
                    with source.hold():
                        pass

                self.assertFalse(backend.active)
                self.assertEqual(backend.cas_calls, 0)

    def test_signed_cas_invalid_evidence_rejected(self):
        modes = (
            "legacy",
            "malformed_pair",
            "bad_signature",
            "wrong_challenge",
            "wrong_predecessor",
            "wrong_operation",
        )

        for mode in modes:
            with self.subTest(mode=mode):
                backend = self.make_backend()
                backend.cas_mode = mode

                source = self.make_source(
                    backend=backend
                )

                with self.assertRaises(ValueError):
                    source.advance(
                        expected_revision=OLD,
                        next_revision=NEXT,
                    )

                self.assertEqual(backend.cas_calls, 1)
                self.assertFalse(backend.active)

                # Backend may already have committed.
                # A failed signed reply is not rollback.

    def test_fake_signed_cas_acknowledgement_detected(self):
        backend = self.make_backend()
        backend.fake_ack = True

        source = self.make_source(
            backend=backend
        )

        with self.assertRaises(ValueError):
            source.advance(
                expected_revision=OLD,
                next_revision=NEXT,
            )

        self.assertEqual(backend.revision, OLD)
        self.assertEqual(backend.cas_calls, 1)
        self.assertGreaterEqual(backend.read_calls, 1)

        with source.hold() as snapshot:
            self.assertEqual(snapshot[2], OLD)

        self.assertFalse(backend.active)

    def test_commit_then_error_fails_closed(self):
        backend = self.make_backend()
        backend.commit_then_fail = True

        source = self.make_source(
            backend=backend
        )

        with self.assertRaises(ValueError):
            source.advance(
                expected_revision=OLD,
                next_revision=NEXT,
            )

        self.assertEqual(backend.cas_calls, 1)
        self.assertEqual(backend.revision, NEXT)

        with source.hold() as snapshot:
            self.assertEqual(snapshot[2], NEXT)

        self.assertFalse(backend.active)

    def test_signed_post_cas_readback_stale_or_corrupt_rejected(
        self
    ):
        for mode in ("stale", "bad_signature"):
            with self.subTest(mode=mode):
                backend = self.make_backend()
                backend.read_mode_after_cas = mode

                source = self.make_source(
                    backend=backend
                )

                with self.assertRaises(ValueError):
                    source.advance(
                        expected_revision=OLD,
                        next_revision=NEXT,
                    )

                self.assertEqual(backend.cas_calls, 1)
                self.assertGreaterEqual(backend.read_calls, 1)

                # A signed response can be stale or invalid
                # even after the backend has changed state.
                self.assertEqual(backend.revision, NEXT)
                self.assertFalse(backend.active)

        backend = self.make_backend()
        backend.fail_on_read_number = 1

        source = self.make_source(backend=backend)

        with self.assertRaises(ValueError):
            source.advance(
                expected_revision=OLD,
                next_revision=NEXT,
            )

        self.assertEqual(backend.revision, NEXT)
        self.assertFalse(backend.active)

    def test_challenge_replay_and_suppressed_errors_fail_closed(
        self
    ):
        backend = self.make_backend()
        source = self.make_source(backend=backend)

        with source.hold() as snapshot:
            self.assertEqual(snapshot[2], OLD)

        backend.read_mode = "replay"

        with self.assertRaises(ValueError):
            with source.hold():
                pass

        self.assertEqual(backend.read_calls, 2)

        self.assertNotEqual(
            backend.read_challenges[0],
            backend.read_challenges[1],
        )

        self.assertFalse(backend.active)

        suppressing = self.make_backend()
        suppressing.suppress_errors = True

        source = self.make_source(
            backend=suppressing
        )

        with self.assertRaises(ValueError):
            with source.hold():
                raise ValueError(
                    "Injected caller verification failure."
                )

        self.assertFalse(suppressing.active)
        self.assertEqual(suppressing.cas_calls, 0)


if __name__ == "__main__":
    unittest.main()
