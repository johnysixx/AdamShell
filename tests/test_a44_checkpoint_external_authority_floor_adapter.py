"""A44 external monotonic authority held-floor adapter contract.

EXPECTED RED: production adapter is absent.

Proposed API:

    ExternalMonotonicAuthorityFloorAdapter.from_source(
        source=SignedCheckpointExternalMonotonicAuthoritySource,
    )

    adapter.hold() -> context manager yielding:
        (root_id, root_public_key, enrollment_epoch,
         minimum_revision)

The injected source must be an exact canonical signed
external authority client, not an arbitrary duck-typed
provider or a subclass overriding signed verification.

The enclosing six-field signed source context must
remain active throughout the projected four-field
snapshot's entire caller verification scope.

All six source fields must be validated before projection.
Revision, generation and fencing minima must remain
enforced. Each adapter hold must obtain a fresh signed read.

No cached floor, unsigned fallback, CAS forwarding,
checkpoint restoration or republication is permitted.

SECURITY LIMITATIONS:

- This adapter does not independently enroll authority keys.
- It does not establish an actual remote read lease.
- No external persistence or monotonic storage is provided.
- It cannot prevent rollback of the authority itself when
  the supplied minima are also stale.
- Python object type checks are not an in-process security
  boundary against malicious Python code.

All authority and signed checkpoint backend instances
below are volatile TEST DOUBLES.
"""

import importlib
import json
import shutil
import sys
import tempfile
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

import test_a44_checkpoint_external_monotonic_authority as authority_contract
import test_a44_checkpoint_backend_trust_gate as gate_contract

from core.existence.history_receipt_trust_checkpoint_external_monotonic_authority import (
    SignedCheckpointExternalMonotonicAuthoritySource,
)

from core.existence.history_receipt_trust_checkpoint_sqlite_floor import (
    SQLiteCheckpointRevisionFloorSource,
)


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_external_authority_floor_adapter"
)

ROOT = gate_contract.ROOT
EPOCH = gate_contract.ENROLLMENT_EPOCH

OLD = gate_contract.OLD
NEXT = OLD + 1

GENERATION = authority_contract.GENERATION
FENCE = authority_contract.FENCE


class GateCompatibleSignedAuthority(
    authority_contract.SignedMemoryMonotonicAuthority
):
    """Volatile signed authority using the gate fixture's root."""

    def __init__(self, signer, root_public_key):
        super().__init__(signer)

        self.root_public_key = root_public_key

        self.revision = OLD
        self.generation = GENERATION
        self.fence_token = FENCE

        self.fail_on_exit = False

    def _signed(self, **arguments):
        response = super()._signed(**arguments)

        if (
            type(response) is not tuple
            or len(response) != 2
        ):
            return response

        message, signature = response

        # Retain deliberately malformed signatures.
        if self.read_mode == "bad_signature":
            return message, signature

        document = json.loads(message)

        document["root_id"] = ROOT

        document["root_public_key_hex"] = (
            self.root_public_key.hex()
        )

        document["enrollment_epoch"] = EPOCH

        encoded = authority_contract.canonical(
            document
        )

        if self.read_mode == "noncanonical":
            encoded += b"\n"

        return encoded, self.signer.sign(encoded)

    @contextmanager
    def hold(self, *, challenge):
        with super().hold(
            challenge=challenge
        ) as response:
            yield response

        if self.fail_on_exit:
            raise OSError(
                "Injected signed authority release failure."
            )


class UnsignedFloorImpostor:
    """Correct looking snapshot without signed verification."""

    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.read_calls = 0

    @contextmanager
    def hold(self):
        self.read_calls += 1

        yield self.snapshot


class OverriddenSignedSource(
    SignedCheckpointExternalMonotonicAuthoritySource
):
    """A subclass can bypass inherited signed verification."""

    @contextmanager
    def hold(self):
        yield (
            self.expected_root_id,
            self.expected_root_public_key,
            self.expected_enrollment_epoch,
            self.minimum_revision,
            self.minimum_generation,
            self.minimum_fence_token,
        )


class A44CheckpointExternalAuthorityFloorAdapterContractTests(
    unittest.TestCase
):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.adapter_type = (
            module.ExternalMonotonicAuthorityFloorAdapter
        )

        self.fixture = (
            gate_contract.A44CheckpointBackendTrustGateContractTests(
                "test_valid_nested_held_trust_and_signed_read"
            )
        )

        self.fixture.setUp()

        self.addCleanup(
            self.fixture.doCleanups
        )

        self.root_key = (
            self.fixture.fixture.root_public
        )

        self.signer = (
            Ed25519PrivateKey.generate()
        )

        self.signer_public = (
            authority_contract.public_bytes(
                self.signer
            )
        )

        self.authority = self.make_authority()

        self.source = self.make_source()

        self.adapter = self.make_adapter()

    def make_authority(self, signer=None):
        return GateCompatibleSignedAuthority(
            self.signer if signer is None else signer,
            self.root_key,
        )

    def make_source(
        self,
        *,
        source_type=SignedCheckpointExternalMonotonicAuthoritySource,
        **changes,
    ):
        arguments = {
            "authority": self.authority,
            "expected_authority_id": (
                authority_contract.AUTHORITY_ID
            ),
            "expected_authority_public_key": (
                self.signer_public
            ),
            "expected_root_id": ROOT,
            "expected_root_public_key": self.root_key,
            "expected_enrollment_epoch": EPOCH,
            "minimum_revision": OLD,
            "minimum_generation": GENERATION,
            "minimum_fence_token": FENCE,
        }

        arguments.update(changes)

        return source_type.from_authority(
            **arguments
        )

    def make_adapter(self, source=None):
        selected = (
            self.source
            if source is None
            else source
        )

        return self.adapter_type.from_source(
            source=selected,
        )

    def make_gate(self, adapter=None):
        return self.fixture.make_gate(
            revision_floor_source=(
                self.adapter
                if adapter is None
                else adapter
            ),
        )

    @staticmethod
    def read(source):
        with source.hold() as snapshot:
            return snapshot

    def expected_floor(self, revision=OLD):
        return (
            ROOT,
            self.root_key,
            EPOCH,
            revision,
        )

    def expected_backend(self, revision=OLD):
        return (
            ROOT,
            self.root_key,
            revision,
        )

    def assert_released(self, authority=None):
        selected = (
            self.authority
            if authority is None
            else authority
        )

        self.assertFalse(selected.active)
        self.assertFalse(self.fixture.enrollment.active)
        self.assertFalse(self.fixture.backend.active)

    def assert_gate_rejected(self, gate=None):
        selected = (
            self.make_gate()
            if gate is None
            else gate
        )

        with self.assertRaises(ValueError):
            self.read(selected)

        self.assert_released()

    def advance_authority(self):
        return self.source.advance_if_current(
            expected_revision=OLD,
            next_revision=NEXT,
            expected_generation=GENERATION,
            expected_fence_token=FENCE,
        )

    def test_signed_six_field_to_four_field_held_projection(
        self
    ):
        with self.adapter.hold() as snapshot:
            self.assertEqual(
                snapshot,
                self.expected_floor(),
            )

            self.assertIs(type(snapshot), tuple)
            self.assertEqual(len(snapshot), 4)

            self.assertIs(type(snapshot[0]), str)
            self.assertIs(type(snapshot[1]), bytes)
            self.assertIs(type(snapshot[2]), int)
            self.assertIs(type(snapshot[3]), int)

            self.assertTrue(self.authority.active)

        self.assert_released()

        self.assertEqual(
            self.authority.read_calls,
            1,
        )

        self.assertEqual(
            self.authority.cas_calls,
            0,
        )

    def test_only_canonical_signed_source_is_accepted(self):
        impostor = UnsignedFloorImpostor(
            (
                ROOT,
                self.root_key,
                EPOCH,
                OLD,
                GENERATION,
                FENCE,
            )
        )

        overridden = self.make_source(
            source_type=OverriddenSignedSource,
        )

        for invalid in (
            None,
            object(),
            self.authority,
            impostor,
            overridden,
        ):
            with self.subTest(
                source_type=type(invalid).__name__
            ):
                with self.assertRaises(ValueError):
                    self.adapter_type.from_source(
                        source=invalid,
                    )

        self.assertEqual(impostor.read_calls, 0)
        self.assertEqual(self.authority.read_calls, 0)
        self.assertEqual(self.authority.cas_calls, 0)

    def test_mutated_adapter_source_is_revalidated(self):
        impostor = UnsignedFloorImpostor(
            (
                ROOT,
                self.root_key,
                EPOCH,
                OLD,
                GENERATION,
                FENCE,
            )
        )

        adapter = self.make_adapter()

        object.__setattr__(
            adapter,
            "source",
            impostor,
        )

        with self.assertRaises(ValueError):
            self.read(adapter)

        self.assertEqual(impostor.read_calls, 0)
        self.assertEqual(self.authority.read_calls, 0)

    def test_actual_trust_gate_retains_all_held_contexts(
        self
    ):
        gate = self.make_gate()

        with gate.hold() as snapshot:
            self.assertEqual(
                snapshot,
                self.expected_backend(),
            )

            self.assertTrue(self.authority.active)
            self.assertTrue(self.fixture.enrollment.active)
            self.assertTrue(self.fixture.backend.active)

        self.assert_released()

        self.assertEqual(
            self.authority.read_calls,
            1,
        )

        self.assertEqual(
            self.fixture.backend.read_calls,
            1,
        )

        self.assertEqual(
            self.authority.cas_calls,
            0,
        )

    def test_authority_advance_rejects_old_signed_backend(
        self
    ):
        gate = self.make_gate()

        self.advance_authority()

        self.assertEqual(
            self.read(self.adapter),
            self.expected_floor(NEXT),
        )

        self.assertEqual(
            self.fixture.backend.revision,
            OLD,
        )

        self.assert_gate_rejected(gate)

        self.fixture.backend.revision = NEXT

        self.assertEqual(
            self.read(gate),
            self.expected_backend(NEXT),
        )

        self.assert_released()

        self.assertEqual(
            self.authority.cas_calls,
            1,
        )

        self.assertEqual(
            self.fixture.backend.cas_calls,
            0,
        )

    def test_enrollment_epoch_mismatch_blocks_backend_read(
        self
    ):
        self.fixture.enrollment.snapshot = (
            self.fixture.enrollment_snapshot(
                epoch=EPOCH + 1,
            )
        )

        self.assert_gate_rejected()

        self.assertEqual(
            self.fixture.backend.read_calls,
            0,
        )

        self.assertEqual(
            self.authority.cas_calls,
            0,
        )

    def test_all_signed_counter_minima_are_retained(self):
        scenarios = (
            (
                "revision",
                {"minimum_revision": NEXT},
            ),
            (
                "generation",
                {"minimum_generation": GENERATION + 1},
            ),
            (
                "fence",
                {"minimum_fence_token": FENCE + 1},
            ),
        )

        for name, changes in scenarios:
            with self.subTest(counter=name):
                source = self.make_source(
                    **changes
                )

                adapter = self.make_adapter(source)

                self.assert_gate_rejected(
                    self.make_gate(adapter)
                )

                self.assertEqual(
                    self.fixture.backend.read_calls,
                    0,
                )

        self.assertEqual(
            self.authority.cas_calls,
            0,
        )

    def test_fresh_signed_read_required_on_each_hold(self):
        gate = self.make_gate()

        self.assertEqual(
            self.read(gate),
            self.expected_backend(),
        )

        first_challenge = (
            self.authority.read_challenges[0]
        )

        self.authority.read_mode = "replay"

        self.assert_gate_rejected(gate)

        self.assertEqual(
            self.authority.read_calls,
            2,
        )

        self.assertNotEqual(
            first_challenge,
            self.authority.read_challenges[1],
        )

        self.assertEqual(
            self.fixture.backend.read_calls,
            1,
        )

        # No stale successful floor may be cached.
        self.authority.read_mode = "valid"
        self.authority.read_failure = True

        self.assert_gate_rejected(gate)

        self.assertEqual(
            self.fixture.backend.read_calls,
            1,
        )

        self.authority.read_failure = False

        self.assertEqual(
            self.read(gate),
            self.expected_backend(),
        )

    def test_invalid_signer_rejected_before_backend_read(
        self
    ):
        rogue = self.make_authority(
            Ed25519PrivateKey.generate()
        )

        source = self.make_source(
            authority=rogue,
        )

        adapter = self.make_adapter(source)

        gate = self.make_gate(adapter)

        with self.assertRaises(ValueError):
            self.read(gate)

        self.assertEqual(rogue.read_calls, 1)
        self.assertEqual(rogue.cas_calls, 0)

        self.assertEqual(
            self.fixture.backend.read_calls,
            0,
        )

        self.assert_released(rogue)

    def test_caller_failure_and_authority_release_failure(
        self
    ):
        gate = self.make_gate()

        self.authority.suppress_caller_error = True

        with self.assertRaises(ValueError):
            with gate.hold() as snapshot:
                self.assertEqual(
                    snapshot,
                    self.expected_backend(),
                )

                self.assertTrue(
                    self.authority.active
                )

                raise ValueError(
                    "Injected caller verification failure."
                )

        self.assert_released()

        self.authority.suppress_caller_error = False
        self.authority.fail_on_exit = True

        with self.assertRaises(ValueError):
            with gate.hold() as snapshot:
                self.assertEqual(
                    snapshot,
                    self.expected_backend(),
                )

        self.assert_released()

        self.authority.fail_on_exit = False

        self.assertEqual(
            self.read(gate),
            self.expected_backend(),
        )

    def test_separate_authority_detects_local_sqlite_rollback(
        self
    ):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)

            database = folder / "local_floor.sqlite3"
            older_copy = folder / "older_valid.sqlite3"

            local = (
                SQLiteCheckpointRevisionFloorSource.bootstrap(
                    path=database,
                    root_id=ROOT,
                    root_public_key=self.root_key,
                    enrollment_epoch=EPOCH,
                    minimum_revision=OLD,
                )
            )

            shutil.copyfile(
                database,
                older_copy,
            )

            local.advance_if_current(
                expected_revision=OLD,
                next_revision=NEXT,
            )

            self.advance_authority()

            self.assertEqual(
                self.read(local),
                self.expected_floor(NEXT),
            )

            shutil.copyfile(
                older_copy,
                database,
            )

            reopened = (
                SQLiteCheckpointRevisionFloorSource.open(
                    path=database,
                    expected_root_id=ROOT,
                    expected_root_public_key=self.root_key,
                    expected_epoch=EPOCH,
                )
            )

            self.assertEqual(
                self.read(reopened),
                self.expected_floor(OLD),
            )

            local_gate = self.fixture.make_gate(
                revision_floor_source=reopened,
            )

            self.assertEqual(
                self.read(local_gate),
                self.expected_backend(OLD),
            )

            self.assertEqual(
                self.read(self.adapter),
                self.expected_floor(NEXT),
            )

            self.assert_gate_rejected()

        self.assert_released()

    def test_authority_rollback_limit_and_read_only_api(
        self
    ):
        self.advance_authority()

        self.assertEqual(
            self.read(self.adapter),
            self.expected_floor(NEXT),
        )

        # Demonstrate rollback of the authority TEST DOUBLE.
        self.authority.revision = OLD
        self.authority.generation = GENERATION
        self.authority.fence_token = FENCE

        # The original source has stale caller-controlled
        # minima. The adapter cannot invent new trusted floors.
        self.assertEqual(
            self.read(self.make_gate()),
            self.expected_backend(OLD),
        )

        strict = self.make_source(
            minimum_revision=NEXT,
            minimum_generation=GENERATION + 1,
            minimum_fence_token=FENCE + 1,
        )

        strict_gate = self.make_gate(
            self.make_adapter(strict)
        )

        backend_reads = (
            self.fixture.backend.read_calls
        )

        self.assert_gate_rejected(
            strict_gate
        )

        self.assertEqual(
            self.fixture.backend.read_calls,
            backend_reads,
        )

        for forbidden in (
            "advance",
            "advance_if_current",
            "restore",
            "republish",
            "authorize",
            "bootstrap",
            "publish",
        ):
            with self.subTest(operation=forbidden):
                self.assertFalse(
                    hasattr(self.adapter, forbidden)
                )


if __name__ == "__main__":
    unittest.main()
