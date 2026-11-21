"""A44 / 66.23B external high-water anchor read-gate contract.

EXPECTED RED:
    core.existence.history_receipt_trust_checkpoint_external_anchor_gate
    does not yet exist.

PROPOSED API:
    CheckpointExternalAnchorReadGate.from_sources(
        signed_source=canonical_signed_source,
        anchor_source=external_anchor,
    )

    gate.hold() -> context manager yielding:
        (root_id, root_public_key, enrollment_epoch,
         revision, generation, fence_token)

Anchor held snapshot:
    (authority_id, authority_public_key,
     root_id, root_public_key, enrollment_epoch,
     revision, generation, fence_token)

REQUIRED:
- Verify canonical signed SQLite authority source.
- Retain the external anchor lease during caller verification.
- Require exact identity, keys, epoch and counter agreement.
- Reject rollback, partial publication and inconsistent state.
- Reject missing or malformed anchor observations.
- Reject signer mismatch and failed lease termination.
- Provide no CAS, restore or republish capability.

SECURITY LIMITATIONS:
- The test anchor is VOLATILE and UNTRUSTED.
- Passing these tests cannot establish independent provenance.
- Real authentication and rollback-resistant storage remain external.
- No cross-store atomicity, remote lease or durability proof.
- These tests must not authorize checkpoint restoration.

All test databases and signing keys are disposable.
"""

import importlib
import shutil
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

import test_a44_checkpoint_sqlite_signed_authority as contract


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_external_anchor_gate"
)


class VolatileAnchor:
    """Test double only. No trusted external provenance."""

    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.active = False
        self.enter_error = None
        self.exit_error = None

    @contextmanager
    def hold(self):
        if self.enter_error is not None:
            raise self.enter_error

        self.active = True

        try:
            yield self.snapshot
        finally:
            self.active = False

            if self.exit_error is not None:
                raise self.exit_error


class A44ExternalAnchorGateContractTests(unittest.TestCase):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.gate_type = (
            module.CheckpointExternalAnchorReadGate
        )

        self.fixture = (
            contract.A44CheckpointSQLiteSignedAuthorityContractTests(
                "test_canonical_signed_held_read"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.backend = self.fixture.bootstrap()
        self.source = self.fixture.client(self.backend)

        self.anchor = VolatileAnchor(
            self.anchor_snapshot()
        )

    def anchor_snapshot(self, counters=None):
        if counters is None:
            counters = (
                contract.OLD,
                contract.GENERATION,
                contract.FENCE,
            )

        return (
            self.source.expected_authority_id,
            self.source.expected_authority_public_key,
            self.source.expected_root_id,
            self.source.expected_root_public_key,
            self.source.expected_enrollment_epoch,
            *counters,
        )

    def gate(self, *, source=None, anchor=None):
        return self.gate_type.from_sources(
            signed_source=(
                self.source if source is None else source
            ),
            anchor_source=(
                self.anchor if anchor is None else anchor
            ),
        )

    @staticmethod
    def read(gate):
        with gate.hold() as snapshot:
            return snapshot

    def test_equal_signed_and_anchor_states_are_accepted(self):
        gate = self.gate()

        with gate.hold() as snapshot:
            self.assertEqual(
                snapshot,
                self.fixture.expected(),
            )

            self.assertTrue(self.anchor.active)

        self.assertFalse(self.anchor.active)

    def test_complete_sqlite_rollback_is_rejected(self):
        old_copy = (
            Path(self.fixture.folder.name)
            / "older-valid.sqlite3"
        )

        shutil.copyfile(
            self.fixture.path,
            old_copy,
        )

        published = self.fixture.advance(self.source)

        self.anchor.snapshot = self.anchor_snapshot(
            published[3:]
        )

        shutil.copyfile(
            old_copy,
            self.fixture.path,
        )

        reopened = self.fixture.client(
            self.fixture.reopen()
        )

        # Existing signed client still accepts stale floors.
        self.assertEqual(
            self.fixture.read(reopened),
            self.fixture.expected(),
        )

        # New anchor gate must reject divergence.
        with self.assertRaises(ValueError):
            self.read(
                self.gate(source=reopened)
            )

        self.assertFalse(self.anchor.active)

    def test_database_ahead_of_anchor_is_rejected(self):
        published = self.fixture.advance(self.source)

        self.assertEqual(
            published[3:],
            (
                contract.NEXT,
                contract.GENERATION + 1,
                contract.FENCE + 1,
            ),
        )

        # Anchor remains at the earlier state.
        with self.assertRaises(ValueError):
            self.read(self.gate())

        self.assertFalse(self.anchor.active)

    def test_anchor_identity_and_counter_tampering(self):
        original = self.anchor_snapshot()

        attacks = (
            (0, "wrong-authority"),
            (1, b"\x42" * 32),
            (2, "wrong-root"),
            (3, b"\x43" * 32),
            (4, original[4] + 1),
            (5, True),
            (6, False),
            (7, -1),
        )

        for index, value in attacks:
            with self.subTest(index=index):
                altered = list(original)
                altered[index] = value

                self.anchor.snapshot = tuple(altered)

                with self.assertRaises(ValueError):
                    self.read(self.gate())

                self.assertFalse(self.anchor.active)

        self.anchor.snapshot = original

    def test_missing_anchor_fails_closed(self):
        self.anchor.enter_error = ValueError(
            "Simulated unavailable external anchor."
        )

        with self.assertRaises(ValueError):
            self.read(self.gate())

        self.assertFalse(self.anchor.active)

        # Failure must not corrupt the local database.
        self.assertEqual(
            self.fixture.read(self.source),
            self.fixture.expected(),
        )

    def test_anchor_lease_exit_failure_is_rejected(self):
        self.anchor.exit_error = ValueError(
            "Simulated anchor lease release failure."
        )

        with self.assertRaises(ValueError):
            self.read(self.gate())

        self.assertFalse(self.anchor.active)

    def test_wrong_sqlite_signer_cannot_be_hidden(self):
        rogue = Ed25519PrivateKey.generate()

        object.__setattr__(
            self.backend,
            "signer",
            rogue,
        )

        with self.assertRaises(ValueError):
            self.read(self.gate())

        self.assertFalse(self.anchor.active)

    def test_gate_has_no_publication_capability(self):
        gate = self.gate()

        for method in (
            "advance_if_current",
            "bootstrap",
            "restore",
            "republish",
        ):
            with self.subTest(method=method):
                self.assertFalse(
                    callable(getattr(gate, method, None))
                )


if __name__ == "__main__":
    unittest.main()
