"""A44 adversarial checkpoint backend trust gate tests.

Targets:

- malformed enrollment and revision-floor snapshots;
- mutated frozen fields;
- mismatched root, key and epoch values;
- forged backend read evidence;
- challenge replay;
- suppression of caller verification failures;
- failures entering or releasing held sources;
- full attacker control of enrollment and floor;
- rollback of both signed backend and trust floor;
- absence of publication authority.

All backends and trust sources are volatile test doubles.

Passing these tests does NOT establish external trust-anchor
independence, secure enrollment, durable monotonic storage,
linearizable CAS or rollback resistance.

No restoration or republication is authorized.
"""

import sys
import unittest

from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_backend_trust_gate as contract
import test_a44_checkpoint_signed_backend_source as signed_contract

from core.existence.history_receipt_trust_checkpoint_backend_evidence import (
    CheckpointRootBackendEvidenceVerifier,
)


ROOT = contract.ROOT
OLD = contract.OLD
NEXT = contract.NEXT
EPOCH = contract.ENROLLMENT_EPOCH


class BytesSubclass(bytes):
    pass


class StringSubclass(str):
    pass


class IntegerSubclass(int):
    pass


class TupleSubclass(tuple):
    pass


class A44CheckpointBackendTrustGateAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44CheckpointBackendTrustGateContractTests(
                "test_valid_nested_held_trust_and_signed_read"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.backend = self.fixture.backend
        self.gate = self.fixture.gate
        self.enrollment = self.fixture.enrollment
        self.floor = self.fixture.floor

    def read(self, gate=None):
        return self.fixture.read(gate)

    def assert_released(self):
        self.fixture.assert_released()

    def test_mutated_gate_dependencies_fail_before_backend_io(
        self
    ):
        attacks = (
            ("backend", None),
            ("backend", object()),
            ("enrollment_source", None),
            ("enrollment_source", object()),
            ("revision_floor_source", None),
            ("revision_floor_source", object()),
            ("expected_root_id", ""),
            ("expected_root_id", True),
            ("expected_root_id", " foreign_root"),
        )

        for field, replacement in attacks:
            with self.subTest(field=field, value=repr(replacement)):
                gate = self.fixture.make_gate()

                object.__setattr__(
                    gate,
                    field,
                    replacement,
                )

                with self.assertRaises(ValueError):
                    self.read(gate)

                self.assertEqual(self.backend.read_calls, 0)
                self.assertEqual(self.backend.cas_calls, 0)
                self.assert_released()

    def test_enrollment_subclass_and_type_smuggling_rejected(
        self
    ):
        valid = self.fixture.enrollment_snapshot()

        invalid = (
            TupleSubclass(valid),
            list(valid),
            self.fixture.enrollment_snapshot(
                backend_id=StringSubclass(contract.BACKEND_ID)
            ),
            self.fixture.enrollment_snapshot(
                backend_id=True
            ),
            self.fixture.enrollment_snapshot(
                backend_public_key=BytesSubclass(
                    self.fixture.fixture.backend_public
                )
            ),
            self.fixture.enrollment_snapshot(
                backend_public_key=b"\x00" * 31
            ),
            self.fixture.enrollment_snapshot(
                root_id=StringSubclass(ROOT)
            ),
            self.fixture.enrollment_snapshot(
                root_public_key=BytesSubclass(
                    self.fixture.fixture.root_public
                )
            ),
            self.fixture.enrollment_snapshot(
                epoch=IntegerSubclass(EPOCH)
            ),
            self.fixture.enrollment_snapshot(
                epoch=True
            ),
            self.fixture.enrollment_snapshot(
                epoch=-1
            ),
        )

        for snapshot in invalid:
            with self.subTest(snapshot=repr(snapshot)[:90]):
                self.enrollment.snapshot = snapshot

                with self.assertRaises(ValueError):
                    self.read()

                self.assertEqual(self.backend.read_calls, 0)
                self.assert_released()

        self.enrollment.snapshot = valid

    def test_revision_floor_type_smuggling_rejected(
        self
    ):
        valid = self.fixture.floor_snapshot()

        invalid = (
            TupleSubclass(valid),
            list(valid),
            self.fixture.floor_snapshot(
                root_id=StringSubclass(ROOT)
            ),
            self.fixture.floor_snapshot(
                root_id=True
            ),
            self.fixture.floor_snapshot(
                root_public_key=BytesSubclass(
                    self.fixture.fixture.root_public
                )
            ),
            self.fixture.floor_snapshot(
                root_public_key=b"\x00" * 31
            ),
            self.fixture.floor_snapshot(
                epoch=IntegerSubclass(EPOCH)
            ),
            self.fixture.floor_snapshot(
                epoch=True
            ),
            self.fixture.floor_snapshot(
                minimum_revision=IntegerSubclass(OLD)
            ),
            self.fixture.floor_snapshot(
                minimum_revision=True
            ),
            self.fixture.floor_snapshot(
                minimum_revision=-1
            ),
        )

        for snapshot in invalid:
            with self.subTest(snapshot=repr(snapshot)[:90]):
                self.floor.snapshot = snapshot

                with self.assertRaises(ValueError):
                    self.read()

                self.assertEqual(self.backend.read_calls, 0)
                self.assertEqual(self.backend.cas_calls, 0)
                self.assert_released()

        self.floor.snapshot = valid

    def test_cross_source_identity_and_epoch_conflicts(
        self
    ):
        valid = self.fixture.floor_snapshot()

        conflicts = (
            self.fixture.floor_snapshot(
                root_id="substituted_root"
            ),
            self.fixture.floor_snapshot(
                root_public_key=b"\x42" * 32
            ),
            self.fixture.floor_snapshot(
                epoch=EPOCH + 1
            ),
            self.fixture.floor_snapshot(
                epoch=EPOCH - 1
            ),
        )

        for snapshot in conflicts:
            with self.subTest(snapshot=repr(snapshot)[:90]):
                self.floor.snapshot = snapshot

                with self.assertRaises(ValueError):
                    self.read()

                self.assertEqual(self.backend.read_calls, 0)
                self.assert_released()

        self.floor.snapshot = valid

        self.enrollment.snapshot = (
            self.fixture.enrollment_snapshot(
                root_id="substituted_root"
            )
        )

        with self.assertRaises(ValueError):
            self.read()

        self.assertEqual(self.backend.read_calls, 0)
        self.assert_released()

    def test_forged_signed_backend_reads_release_all_leases(
        self
    ):
        modes = (
            "legacy",
            "malformed_pair",
            "bad_signature",
            "noncanonical",
            "wrong_operation",
            "wrong_backend",
            "wrong_root",
            "wrong_root_key",
            "wrong_challenge",
        )

        for mode in modes:
            with self.subTest(mode=mode):
                backend = self.fixture.fixture.make_backend()
                backend.read_mode = mode

                gate = self.fixture.make_gate(
                    backend=backend
                )

                with self.assertRaises(ValueError):
                    self.read(gate)

                self.assertEqual(backend.read_calls, 1)
                self.assertEqual(backend.cas_calls, 0)

                self.assertFalse(backend.active)
                self.assertFalse(self.enrollment.active)
                self.assertFalse(self.floor.active)

    def test_crypto_verification_runs_inside_all_three_leases(
        self
    ):
        original = (
            CheckpointRootBackendEvidenceVerifier.verify_read
        )

        observations = []

        def guarded_verify(verifier, **kwargs):
            self.assertTrue(self.enrollment.active)
            self.assertTrue(self.floor.active)
            self.assertTrue(self.backend.active)

            observations.append(
                kwargs["expected_challenge"]
            )

            self.assertEqual(
                kwargs["minimum_revision"],
                OLD,
            )

            return original(verifier, **kwargs)

        with patch.object(
            CheckpointRootBackendEvidenceVerifier,
            "verify_read",
            new=guarded_verify,
        ):
            with self.gate.hold() as snapshot:
                self.assertEqual(snapshot[2], OLD)

                self.assertTrue(self.enrollment.active)
                self.assertTrue(self.floor.active)
                self.assertTrue(self.backend.active)

        self.assertEqual(len(observations), 1)
        self.assertIs(type(observations[0]), bytes)
        self.assertEqual(len(observations[0]), 32)

        self.assertEqual(self.backend.read_calls, 1)
        self.assertEqual(self.backend.cas_calls, 0)

        self.assert_released()

    def test_replayed_backend_response_is_rejected(
        self
    ):
        with self.gate.hold() as snapshot:
            self.assertEqual(snapshot[2], OLD)

        self.backend.read_mode = "replay"

        with self.assertRaises(ValueError):
            self.read()

        self.assertEqual(self.backend.read_calls, 2)
        self.assertEqual(self.backend.cas_calls, 0)

        self.assertEqual(
            len(self.backend.read_challenges),
            2,
        )

        self.assertNotEqual(
            self.backend.read_challenges[0],
            self.backend.read_challenges[1],
        )

        self.assert_released()

    def test_suppressed_enrollment_caller_error_fails_closed(
        self
    ):
        suppressing = contract.MemoryHeldTrustSource(
            self.fixture.enrollment_snapshot(),
            suppress_errors=True,
        )

        gate = self.fixture.make_gate(
            enrollment_source=suppressing
        )

        with self.assertRaises(ValueError):
            with gate.hold() as snapshot:
                self.assertEqual(snapshot[2], OLD)
                raise ValueError(
                    "Injected caller verification failure."
                )

        self.assertEqual(self.backend.read_calls, 1)
        self.assertEqual(self.backend.cas_calls, 0)

        self.assertEqual(
            suppressing.events,
            ["enter", "exit"],
        )

        self.assertFalse(suppressing.active)
        self.assertFalse(self.floor.active)
        self.assertFalse(self.backend.active)

    def test_suppressed_revision_floor_caller_error_fails_closed(
        self
    ):
        suppressing = contract.MemoryHeldTrustSource(
            self.fixture.floor_snapshot(),
            suppress_errors=True,
        )

        gate = self.fixture.make_gate(
            revision_floor_source=suppressing
        )

        with self.assertRaises(ValueError):
            with gate.hold() as snapshot:
                self.assertEqual(snapshot[2], OLD)
                raise ValueError(
                    "Injected caller verification failure."
                )

        self.assertEqual(self.backend.read_calls, 1)
        self.assertEqual(self.backend.cas_calls, 0)

        self.assertEqual(
            suppressing.events,
            ["enter", "exit"],
        )

        self.assertFalse(suppressing.active)
        self.assertFalse(self.enrollment.active)
        self.assertFalse(self.backend.active)

    def test_provider_entry_exit_and_backend_failures(
        self
    ):
        unavailable_enrollment = (
            contract.MemoryHeldTrustSource(
                self.fixture.enrollment_snapshot(),
                enter_error=OSError(
                    "Enrollment source unavailable."
                ),
            )
        )

        with self.assertRaises(ValueError):
            self.read(
                self.fixture.make_gate(
                    enrollment_source=unavailable_enrollment
                )
            )

        self.assertFalse(unavailable_enrollment.active)
        self.assertEqual(self.backend.read_calls, 0)

        broken_floor = contract.MemoryHeldTrustSource(
            self.fixture.floor_snapshot(),
            exit_error=OSError(
                "Revision-floor release failure."
            ),
        )

        with self.assertRaises(ValueError):
            self.read(
                self.fixture.make_gate(
                    revision_floor_source=broken_floor
                )
            )

        self.assertEqual(self.backend.read_calls, 1)
        self.assertFalse(broken_floor.active)
        self.assertFalse(self.enrollment.active)
        self.assertFalse(self.backend.active)

        self.backend.fail_on_read_number = 2

        with self.assertRaises(ValueError):
            self.read()

        self.assertEqual(self.backend.read_calls, 2)
        self.assertEqual(self.backend.cas_calls, 0)
        self.assert_released()

    def test_attacker_controlling_both_sources_can_repin_keys(
        self
    ):
        rogue_backend_private = Ed25519PrivateKey.generate()
        rogue_root_private = Ed25519PrivateKey.generate()

        rogue_backend_public = signed_contract.public_bytes(
            rogue_backend_private
        )

        rogue_root_public = signed_contract.public_bytes(
            rogue_root_private
        )

        rogue_backend = signed_contract.SignedMemoryBackend(
            root_public=rogue_root_public,
            signer=rogue_backend_private,
            revision=OLD,
        )

        rogue_enrollment = contract.MemoryHeldTrustSource(
            self.fixture.enrollment_snapshot(
                backend_public_key=rogue_backend_public,
                root_public_key=rogue_root_public,
            )
        )

        rogue_floor = contract.MemoryHeldTrustSource(
            self.fixture.floor_snapshot(
                root_public_key=rogue_root_public,
                minimum_revision=OLD,
            )
        )

        gate = self.fixture.make_gate(
            backend=rogue_backend,
            enrollment_source=rogue_enrollment,
            revision_floor_source=rogue_floor,
        )

        with gate.hold() as snapshot:
            self.assertEqual(
                snapshot,
                (ROOT, rogue_root_public, OLD),
            )

            self.assertTrue(rogue_enrollment.active)
            self.assertTrue(rogue_floor.active)
            self.assertTrue(rogue_backend.active)

        # EXPECTED LIMITATION:
        # Both supplied trust sources were attacker-controlled.
        # Matching their snapshots is not independent enrollment.

        self.assertEqual(rogue_backend.read_calls, 1)
        self.assertEqual(rogue_backend.cas_calls, 0)

        self.assertFalse(rogue_enrollment.active)
        self.assertFalse(rogue_floor.active)
        self.assertFalse(rogue_backend.active)

    def test_joint_floor_rollback_and_read_only_boundary(
        self
    ):
        # Advance the signed volatile backend using its
        # existing integration source, NOT through the gate.
        result = self.fixture.fixture.source.advance(
            expected_revision=OLD,
            next_revision=NEXT,
        )

        self.assertEqual(result[2], NEXT)
        self.assertEqual(self.backend.revision, NEXT)

        self.floor.snapshot = self.fixture.floor_snapshot(
            minimum_revision=NEXT
        )

        with self.gate.hold() as snapshot:
            self.assertEqual(snapshot[2], NEXT)

        # Simulate rollback in the volatile backend.
        self.backend.revision = OLD

        with self.assertRaises(ValueError):
            self.read()

        # Now also roll back the injected trust-floor source.
        # No trusted independent historical floor remains.
        self.floor.snapshot = self.fixture.floor_snapshot(
            minimum_revision=OLD
        )

        with self.gate.hold() as snapshot:
            self.assertEqual(snapshot[2], OLD)

        # The trust gate does not expose write authority.
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

        # Only the earlier explicit source.advance() wrote.
        self.assertEqual(self.backend.cas_calls, 1)
        self.assert_released()


if __name__ == "__main__":
    unittest.main()
