"""A44 / 66.23D adversarial external anchor gate audit.

This contract tests a read-only comparison gate.

SECURITY LIMITATIONS:
- Volatile and forged anchors are NOT trusted anchors.
- A matching anchor cannot prove independent provenance.
- A malicious provider may lie about its held lease.
- Simultaneous rollback of both sources may remain undetected.
- No genuine remote durability, fencing or atomicity is proven.
- No restore or republish capability is authorized.

Tests use only temporary SQLite databases and throwaway keys.
"""

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

import test_a44_checkpoint_external_anchor_gate_contract as contract


class TupleSubclass(tuple):
    pass


class BytesSubclass(bytes):
    pass


class SuppressingAnchor:
    """Malicious context manager suppressing caller ValueError."""

    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.active = False
        self.suppressed = False

    @contextmanager
    def hold(self):
        self.active = True

        try:
            try:
                yield self.snapshot
            except ValueError:
                self.suppressed = True
        finally:
            self.active = False


class ForgedAnchor:
    """Untrusted anchor returning attacker-selected snapshots."""

    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.active = False

    @contextmanager
    def hold(self):
        self.active = True

        try:
            yield self.snapshot
        finally:
            self.active = False


class MalformedContextAnchor:
    def hold(self):
        return 123


class A44ExternalAnchorGateAdversarialTests(unittest.TestCase):

    def setUp(self):
        self.fixture = (
            contract.A44ExternalAnchorGateContractTests(
                "test_equal_signed_and_anchor_states_are_accepted"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.anchor = self.fixture.anchor
        self.source = self.fixture.source
        self.backend = self.fixture.backend

    def gate(self, **changes):
        return self.fixture.gate(**changes)

    def read(self, gate=None):
        return self.fixture.read(
            self.gate() if gate is None else gate
        )

    def change_anchor(self, index, value):
        snapshot = list(
            self.fixture.anchor_snapshot()
        )

        snapshot[index] = value
        self.anchor.snapshot = tuple(snapshot)

    def assert_rejected(self):
        with self.assertRaises(ValueError):
            self.read()

        self.assertFalse(self.anchor.active)

    def test_noncanonical_anchor_containers_fail_closed(self):
        original = self.fixture.anchor_snapshot()

        attacks = (
            None,
            list(original),
            original[:7],
            original + (0,),
            TupleSubclass(original),
        )

        for value in attacks:
            with self.subTest(value=repr(value)[:80]):
                self.anchor.snapshot = value
                self.assert_rejected()

    def test_invalid_anchor_identifiers_fail_closed(self):
        attacks = (
            (0, ""),
            (0, True),
            (0, " wrong-authority"),
            (2, ""),
            (2, False),
            (2, "wrong-root"),
        )

        for index, value in attacks:
            with self.subTest(index=index, value=repr(value)):
                self.change_anchor(index, value)
                self.assert_rejected()

    def test_invalid_anchor_public_keys_fail_closed(self):
        original = self.fixture.anchor_snapshot()

        attacks = (
            (1, b"short"),
            (1, bytearray(original[1])),
            (1, BytesSubclass(original[1])),
            (1, b"\x42" * 32),
            (3, b"short"),
            (3, bytearray(original[3])),
            (3, BytesSubclass(original[3])),
            (3, b"\x43" * 32),
        )

        for index, value in attacks:
            with self.subTest(index=index, value=repr(value)[:60]):
                self.change_anchor(index, value)
                self.assert_rejected()

    def test_invalid_anchor_epochs_fail_closed(self):
        epoch = self.fixture.anchor_snapshot()[4]

        for value in (
            None,
            True,
            -1,
            "1",
            float(epoch),
            epoch + 1,
            1 << 63,
        ):
            with self.subTest(value=repr(value)):
                self.change_anchor(4, value)
                self.assert_rejected()

    def test_invalid_anchor_counters_fail_closed(self):
        for index in (5, 6, 7):
            for value in (
                None,
                True,
                -1,
                "10",
                1.5,
                1 << 63,
            ):
                with self.subTest(
                    index=index,
                    value=repr(value),
                ):
                    self.change_anchor(index, value)
                    self.assert_rejected()

    def test_noncanonical_signed_source_rejected(self):
        with self.assertRaises(ValueError):
            self.gate(source=object())

        with self.assertRaises(ValueError):
            self.fixture.gate_type.from_sources(
                signed_source=None,
                anchor_source=self.anchor,
            )

    def test_anchor_without_valid_hold_rejected(self):
        with self.assertRaises(ValueError):
            self.gate(anchor=object())

        with self.assertRaises(ValueError):
            self.fixture.gate_type.from_sources(
                signed_source=self.source,
                anchor_source=None,
            )

        malformed = MalformedContextAnchor()

        with self.assertRaises(ValueError):
            self.read(
                self.gate(anchor=malformed)
            )

    def test_unavailable_anchor_fails_closed(self):
        self.anchor.enter_error = RuntimeError(
            "Simulated unavailable anchor."
        )

        self.assert_rejected()

        self.assertEqual(
            self.fixture.fixture.read(self.source),
            self.fixture.fixture.expected(),
        )

    def test_anchor_exit_error_fails_closed(self):
        self.anchor.exit_error = RuntimeError(
            "Simulated anchor exit failure."
        )

        self.assert_rejected()

    def test_suppressed_caller_exception_fails_closed(self):
        malicious = SuppressingAnchor(
            self.fixture.anchor_snapshot()
        )

        gate = self.gate(anchor=malicious)

        with self.assertRaises(ValueError):
            with gate.hold() as snapshot:
                self.assertEqual(
                    snapshot,
                    self.fixture.fixture.expected(),
                )

                raise ValueError(
                    "Simulated caller verification failure."
                )

        self.assertTrue(malicious.suppressed)
        self.assertFalse(malicious.active)

    def test_signed_provider_failure_releases_anchor(self):
        object.__setattr__(
            self.backend,
            "signer",
            Ed25519PrivateKey.generate(),
        )

        self.assert_rejected()

    def test_anchor_behind_signed_database_rejected(self):
        published = self.fixture.fixture.advance(
            self.source
        )

        self.assertNotEqual(
            published[3:],
            self.fixture.anchor_snapshot()[5:],
        )

        self.assert_rejected()

    def test_signed_database_behind_anchor_rejected(self):
        older = (
            Path(self.fixture.fixture.folder.name)
            / "older-db.sqlite3"
        )

        shutil.copyfile(
            self.fixture.fixture.path,
            older,
        )

        published = self.fixture.fixture.advance(
            self.source
        )

        self.anchor.snapshot = (
            self.fixture.anchor_snapshot(
                published[3:]
            )
        )

        shutil.copyfile(
            older,
            self.fixture.fixture.path,
        )

        reopened = self.fixture.fixture.client(
            self.fixture.fixture.reopen()
        )

        with self.assertRaises(ValueError):
            self.read(
                self.gate(source=reopened)
            )

        self.assertFalse(self.anchor.active)

    def test_joint_rollback_not_detected_by_volatile_anchor(self):
        """KNOWN LIMIT: both untrusted sources can be rolled back."""

        older = (
            Path(self.fixture.fixture.folder.name)
            / "joint-older.sqlite3"
        )

        original = self.fixture.anchor_snapshot()

        shutil.copyfile(
            self.fixture.fixture.path,
            older,
        )

        published = self.fixture.fixture.advance(
            self.source
        )

        self.anchor.snapshot = (
            self.fixture.anchor_snapshot(
                published[3:]
            )
        )

        shutil.copyfile(
            older,
            self.fixture.fixture.path,
        )

        # Simulate rollback of an unprotected anchor too.
        self.anchor.snapshot = original

        reopened = self.fixture.fixture.client(
            self.fixture.fixture.reopen()
        )

        accepted = self.read(
            self.gate(source=reopened)
        )

        self.assertEqual(
            accepted,
            self.fixture.fixture.expected(),
        )

        self.assertNotEqual(
            accepted[3:],
            published[3:],
        )

        self.assertFalse(self.anchor.active)

    def test_anchor_mutation_during_hold_not_detected(self):
        """KNOWN LIMIT: fake lease cannot guarantee consistency."""

        original = self.fixture.anchor_snapshot()

        with self.gate().hold() as snapshot:
            self.assertTrue(self.anchor.active)

            self.anchor.snapshot = (
                self.fixture.anchor_snapshot(
                    (
                        snapshot[3] + 1,
                        snapshot[4] + 1,
                        snapshot[5] + 1,
                    )
                )
            )

            self.assertNotEqual(
                original,
                self.anchor.snapshot,
            )

        self.assertFalse(self.anchor.active)

        # Gate accepted the original held observation.
        # It cannot independently prove lease honesty.
        self.assertEqual(
            snapshot,
            self.fixture.fixture.expected(),
        )

    def test_forged_matching_anchor_is_accepted(self):
        """KNOWN LIMIT: equality cannot prove anchor provenance."""

        forged = ForgedAnchor(
            self.fixture.anchor_snapshot()
        )

        accepted = self.read(
            self.gate(anchor=forged)
        )

        self.assertEqual(
            accepted,
            self.fixture.fixture.expected(),
        )

        self.assertFalse(forged.active)

    def test_repeated_consistent_reads_do_not_publish(self):
        expected = self.fixture.fixture.expected()

        for _ in range(3):
            self.assertEqual(
                self.read(),
                expected,
            )

            self.assertFalse(self.anchor.active)

        self.assertEqual(
            self.fixture.fixture.read(self.source),
            expected,
        )


if __name__ == "__main__":
    unittest.main()
