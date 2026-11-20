"""A44 external checkpoint backend trust-gate contract.

EXPECTED RED: checkpoint_backend_trust_gate module absent.

Proposed API:

    CheckpointBackendTrustHeldReadGate.from_sources(
        backend=backend,
        enrollment_source=enrollment_source,
        revision_floor_source=revision_floor_source,
        expected_root_id=str,
    )

    gate.hold() -> context manager yielding:
        (root_id, root_public_key, signed_revision)

Enrollment source:

    enrollment_source.hold() -> (
        backend_id,
        backend_public_key,
        root_id,
        root_public_key,
        enrollment_epoch,
    )

Revision-floor source:

    revision_floor_source.hold() -> (
        root_id,
        root_public_key,
        enrollment_epoch,
        minimum_revision,
    )

The gate must:

- Acquire both held trust snapshots.
- Validate strict snapshot types and matching identities.
- Bind signed backend verification to enrolled keys.
- Reject signed revisions below the held floor.
- Retain both trust leases during backend verification
  and throughout the caller's held verification scope.
- Reject suppressed caller exceptions.
- Generate fresh signed-backend read challenges.
- Provide no CAS, restore or republication API.

Security limitations:

The injected enrollment and floor sources are NOT proven
independent, authenticated, durable or rollback-resistant.

An attacker controlling both sources can substitute an
attacker-generated signing key and lower the floor.

Passing this contract cannot establish actual trust-anchor
provenance or secure storage.

All sources below are volatile TEST DOUBLES.
"""

import importlib
import sys
import unittest

from contextlib import contextmanager
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_signed_backend_source as signed_contract


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_backend_trust_gate"
)

BACKEND_ID = signed_contract.BACKEND_ID
ROOT = signed_contract.ROOT

OLD = signed_contract.OLD
NEXT = signed_contract.NEXT

ENROLLMENT_EPOCH = 2


class MemoryHeldTrustSource:
    """Untrusted volatile source; no genuine trust provenance."""

    def __init__(
        self,
        snapshot,
        *,
        enter_error=None,
        exit_error=None,
        suppress_errors=False,
    ):
        self.snapshot = snapshot
        self.enter_error = enter_error
        self.exit_error = exit_error
        self.suppress_errors = suppress_errors

        self.active = False
        self.events = []

    @contextmanager
    def hold(self):
        self.events.append("enter")

        if self.enter_error is not None:
            raise self.enter_error

        self.active = True

        try:
            try:
                yield self.snapshot

            except ValueError:
                if not self.suppress_errors:
                    raise

        finally:
            self.active = False
            self.events.append("exit")

            if self.exit_error is not None:
                raise self.exit_error


class A44CheckpointBackendTrustGateContractTests(
    unittest.TestCase
):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.gate_type = (
            module.CheckpointBackendTrustHeldReadGate
        )

        self.fixture = (
            signed_contract.A44CheckpointSignedBackendSourceContractTests(
                "test_signed_held_read_keeps_lease"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.backend = self.fixture.backend

        self.enrollment = MemoryHeldTrustSource(
            self.enrollment_snapshot()
        )

        self.floor = MemoryHeldTrustSource(
            self.floor_snapshot()
        )

        self.gate = self.make_gate()

    def enrollment_snapshot(
        self,
        *,
        backend_id=BACKEND_ID,
        backend_public_key=None,
        root_id=ROOT,
        root_public_key=None,
        epoch=ENROLLMENT_EPOCH,
    ):
        return (
            backend_id,
            (
                self.fixture.backend_public
                if backend_public_key is None
                else backend_public_key
            ),
            root_id,
            (
                self.fixture.root_public
                if root_public_key is None
                else root_public_key
            ),
            epoch,
        )

    def floor_snapshot(
        self,
        *,
        root_id=ROOT,
        root_public_key=None,
        epoch=ENROLLMENT_EPOCH,
        minimum_revision=OLD,
    ):
        return (
            root_id,
            (
                self.fixture.root_public
                if root_public_key is None
                else root_public_key
            ),
            epoch,
            minimum_revision,
        )

    def make_gate(self, **changes):
        arguments = {
            "backend": self.backend,
            "enrollment_source": self.enrollment,
            "revision_floor_source": self.floor,
            "expected_root_id": ROOT,
        }

        arguments.update(changes)

        return self.gate_type.from_sources(**arguments)

    def assert_released(
        self,
        *,
        enrollment=None,
        floor=None,
        backend=None,
    ):
        enrollment = (
            self.enrollment
            if enrollment is None
            else enrollment
        )

        floor = (
            self.floor
            if floor is None
            else floor
        )

        backend = (
            self.backend
            if backend is None
            else backend
        )

        self.assertFalse(enrollment.active)
        self.assertFalse(floor.active)
        self.assertFalse(backend.active)

    def read(self, gate=None):
        gate = self.gate if gate is None else gate

        with gate.hold() as snapshot:
            return snapshot

    def test_valid_nested_held_trust_and_signed_read(self):
        with self.gate.hold() as snapshot:
            self.assertEqual(
                snapshot,
                (ROOT, self.fixture.root_public, OLD),
            )

            self.assertTrue(self.enrollment.active)
            self.assertTrue(self.floor.active)
            self.assertTrue(self.backend.active)

        self.assertEqual(
            self.enrollment.events,
            ["enter", "exit"],
        )

        self.assertEqual(
            self.floor.events,
            ["enter", "exit"],
        )

        self.assertEqual(self.backend.read_calls, 1)
        self.assertEqual(self.backend.cas_calls, 0)

        self.assert_released()

    def test_missing_or_unusable_sources_rejected(self):
        class MissingHold:
            pass

        class NonCallableHold:
            hold = None

        class MissingBackend:
            def hold(self, *, challenge):
                raise AssertionError(
                    "Should not read backend."
                )

        invalid = (
            {"backend": None},
            {"backend": object()},
            {"backend": MissingBackend()},
            {"enrollment_source": None},
            {"enrollment_source": MissingHold()},
            {"enrollment_source": NonCallableHold()},
            {"revision_floor_source": None},
            {"revision_floor_source": MissingHold()},
            {"revision_floor_source": NonCallableHold()},
            {"expected_root_id": ""},
            {"expected_root_id": True},
            {"expected_root_id": " foreign"},
        )

        for changes in invalid:
            with self.subTest(changes=repr(changes)[:75]):
                with self.assertRaises(ValueError):
                    self.make_gate(**changes)

        self.assertEqual(self.backend.read_calls, 0)
        self.assertEqual(self.backend.cas_calls, 0)

    def test_malformed_enrollment_snapshots_rejected(self):
        valid = self.enrollment_snapshot()

        malformed = (
            None,
            [],
            {},
            (),
            valid[:-1],
            (*valid, "extra"),
            list(valid),
            self.enrollment_snapshot(backend_id=""),
            self.enrollment_snapshot(backend_id=True),
            self.enrollment_snapshot(
                backend_public_key=b"short"
            ),
            self.enrollment_snapshot(
                backend_public_key=bytearray(
                    self.fixture.backend_public
                )
            ),
            self.enrollment_snapshot(root_id="foreign_root"),
            self.enrollment_snapshot(
                root_public_key=b"short"
            ),
            self.enrollment_snapshot(epoch=True),
            self.enrollment_snapshot(epoch=-1),
            self.enrollment_snapshot(epoch="2"),
        )

        for snapshot in malformed:
            with self.subTest(snapshot=repr(snapshot)[:80]):
                self.enrollment.snapshot = snapshot

                with self.assertRaises(ValueError):
                    self.read()

                self.assertEqual(self.backend.read_calls, 0)
                self.assert_released()

        self.enrollment.snapshot = valid

    def test_malformed_revision_floor_snapshots_rejected(self):
        valid = self.floor_snapshot()

        malformed = (
            None,
            [],
            {},
            (),
            valid[:-1],
            (*valid, "extra"),
            list(valid),
            self.floor_snapshot(root_id=""),
            self.floor_snapshot(root_id=True),
            self.floor_snapshot(root_public_key=b"short"),
            self.floor_snapshot(
                root_public_key=bytearray(
                    self.fixture.root_public
                )
            ),
            self.floor_snapshot(epoch=True),
            self.floor_snapshot(epoch=-1),
            self.floor_snapshot(epoch="2"),
            self.floor_snapshot(minimum_revision=True),
            self.floor_snapshot(minimum_revision=-1),
            self.floor_snapshot(minimum_revision="12"),
        )

        for snapshot in malformed:
            with self.subTest(snapshot=repr(snapshot)[:80]):
                self.floor.snapshot = snapshot

                with self.assertRaises(ValueError):
                    self.read()

                self.assertEqual(self.backend.read_calls, 0)
                self.assert_released()

        self.floor.snapshot = valid

    def test_cross_source_root_and_epoch_mismatch_rejected(
        self
    ):
        invalid = (
            self.floor_snapshot(root_id="foreign_root"),
            self.floor_snapshot(
                root_public_key=b"\x07" * 32
            ),
            self.floor_snapshot(epoch=ENROLLMENT_EPOCH + 1),
            self.floor_snapshot(epoch=ENROLLMENT_EPOCH - 1),
        )

        for snapshot in invalid:
            with self.subTest(snapshot=repr(snapshot)[:80]):
                self.floor.snapshot = snapshot

                with self.assertRaises(ValueError):
                    self.read()

                self.assertEqual(self.backend.read_calls, 0)
                self.assert_released()

        self.floor.snapshot = self.floor_snapshot()

    def test_backend_signer_substitution_rejected(self):
        rogue_private = Ed25519PrivateKey.generate()

        rogue_backend = (
            signed_contract.SignedMemoryBackend(
                root_public=self.fixture.root_public,
                signer=rogue_private,
                revision=OLD,
            )
        )

        gate = self.make_gate(backend=rogue_backend)

        with self.assertRaises(ValueError):
            self.read(gate)

        self.assertEqual(rogue_backend.read_calls, 1)
        self.assertEqual(rogue_backend.cas_calls, 0)

        self.assert_released(backend=rogue_backend)

    def test_signed_read_below_held_floor_rejected(self):
        self.floor.snapshot = self.floor_snapshot(
            minimum_revision=NEXT
        )

        with self.assertRaises(ValueError):
            self.read()

        self.assertEqual(self.backend.revision, OLD)
        self.assertEqual(self.backend.read_calls, 1)
        self.assertEqual(self.backend.cas_calls, 0)

        self.assert_released()

    def test_held_floor_detects_backend_rollback(self):
        self.fixture.source.advance(
            expected_revision=OLD,
            next_revision=NEXT,
        )

        self.floor.snapshot = self.floor_snapshot(
            minimum_revision=NEXT
        )

        self.assertEqual(
            self.read()[2],
            NEXT,
        )

        # Volatile memory rollback, not an actual restart.
        self.backend.revision = OLD

        with self.assertRaises(ValueError):
            self.read()

        self.assert_released()

        self.floor.snapshot = self.floor_snapshot(
            minimum_revision=OLD
        )

        # If the external floor itself rolls back,
        # software cannot infer its former value.
        self.assertEqual(
            self.read()[2],
            OLD,
        )

        self.assert_released()

    def test_attacker_controlled_sources_remain_a_limitation(
        self
    ):
        rogue_private = Ed25519PrivateKey.generate()

        rogue_public = signed_contract.public_bytes(
            rogue_private
        )

        rogue_backend = (
            signed_contract.SignedMemoryBackend(
                root_public=self.fixture.root_public,
                signer=rogue_private,
                revision=OLD,
            )
        )

        rogue_enrollment = MemoryHeldTrustSource(
            self.enrollment_snapshot(
                backend_public_key=rogue_public
            )
        )

        gate = self.make_gate(
            backend=rogue_backend,
            enrollment_source=rogue_enrollment,
        )

        # The gate cannot tell that the injected
        # enrollment source was attacker-controlled.
        self.assertEqual(
            self.read(gate)[2],
            OLD,
        )

        self.assertFalse(rogue_enrollment.active)
        self.assert_released(backend=rogue_backend)

    def test_suppressed_caller_exception_fails_closed(self):
        suppressing_floor = MemoryHeldTrustSource(
            self.floor_snapshot(),
            suppress_errors=True,
        )

        gate = self.make_gate(
            revision_floor_source=suppressing_floor
        )

        with self.assertRaises(ValueError):
            with gate.hold():
                raise ValueError(
                    "Injected caller verification failure."
                )

        self.assertFalse(suppressing_floor.active)
        self.assertFalse(self.enrollment.active)
        self.assertFalse(self.backend.active)

    def test_provider_failures_release_held_sources(self):
        bad_enrollment = MemoryHeldTrustSource(
            self.enrollment_snapshot(),
            enter_error=OSError("Enrollment unavailable."),
        )

        with self.assertRaises(ValueError):
            self.read(
                self.make_gate(
                    enrollment_source=bad_enrollment
                )
            )

        self.assertFalse(bad_enrollment.active)
        self.assertEqual(self.backend.read_calls, 0)

        bad_floor = MemoryHeldTrustSource(
            self.floor_snapshot(),
            exit_error=OSError("Floor teardown failed."),
        )

        with self.assertRaises(ValueError):
            self.read(
                self.make_gate(
                    revision_floor_source=bad_floor
                )
            )

        self.assertFalse(bad_floor.active)
        self.assertFalse(self.enrollment.active)
        self.assertFalse(self.backend.active)

        self.backend.read_mode = "bad_signature"

        with self.assertRaises(ValueError):
            self.read()

        self.assert_released()

    def test_fresh_challenges_and_read_only_boundary(self):
        self.assertEqual(
            self.read()[2],
            OLD,
        )

        self.assertEqual(
            self.read()[2],
            OLD,
        )

        self.assertEqual(self.backend.read_calls, 2)
        self.assertEqual(self.backend.cas_calls, 0)

        first, second = self.backend.read_challenges

        self.assertIs(type(first), bytes)
        self.assertIs(type(second), bytes)

        self.assertEqual(len(first), 32)
        self.assertEqual(len(second), 32)

        self.assertNotEqual(first, second)

        for operation in (
            "advance",
            "publish",
            "restore",
            "republish",
            "authorize",
            "bootstrap",
        ):
            with self.subTest(operation=operation):
                self.assertFalse(
                    hasattr(self.gate, operation)
                )

        self.assert_released()


if __name__ == "__main__":
    unittest.main()
