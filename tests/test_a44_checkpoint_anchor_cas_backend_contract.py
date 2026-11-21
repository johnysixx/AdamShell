"""A44 / 66.26B reference backend atomicity and recovery contract.

Expected RED: SQLiteReferenceSignedCheckpointAnchorCASAuthority absent.

BACKEND API:

SQLiteReferenceSignedCheckpointAnchorCASAuthority.bootstrap(
    *, path, signer, anchor_id, authority_id, authority_public_key,
    root_id, root_public_key, enrollment_epoch, initial_revision,
    initial_generation, initial_fence_token)

SQLiteReferenceSignedCheckpointAnchorCASAuthority.open(
    *, path, signer, expected_anchor_id, expected_authority_id,
    expected_authority_public_key, expected_root_id,
    expected_root_public_key, expected_enrollment_epoch)

provider.hold(*, challenge)
    -> context manager yielding (canonical_bytes, Ed25519_signature)

provider.advance_if_current(
    *, operation_id, expected_revision, next_revision,
    expected_generation, expected_fence_token, challenge)
    -> (canonical_bytes, Ed25519_signature)

provider.lookup_operation(*, operation_id, challenge)
    -> (canonical_bytes, Ed25519_signature)

Signed JSON must match the existing pinned read and CAS clients.

Database tables used by fault injection:
    checkpoint_anchor_cas_state
    checkpoint_anchor_cas_operations

SECURITY BOUNDARY:

This is a local SQLite REFERENCE backend for atomicity and
restart recovery, NOT an independently trusted remote anchor.

The caller supplies the signing key. No independent enrollment,
remote service, rollback-resistant high-water storage,
cross-store atomicity, or checkpoint restoration is proven.

Replacing the database with an older valid copy can restore
previous state and remove previously committed operation records.
"""

import importlib
import shutil
import sqlite3
import tempfile
import unittest

from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from core.existence.history_receipt_trust_checkpoint_anchor_cas_client import (
    PinnedSignedCheckpointAnchorCASClient,
)

from core.existence.history_receipt_trust_checkpoint_pinned_anchor_client import (
    PinnedSignedCheckpointAnchorSource,
)


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_anchor_cas_backend_sqlite_reference"
)

TYPE = "SQLiteReferenceSignedCheckpointAnchorCASAuthority"

OP_A = "a" * 32
OP_B = "b" * 32


def public_key(signer):
    return signer.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


class A44AnchorCASBackendAtomicRecoveryContractTests(
    unittest.TestCase
):

    def setUp(self):
        module = importlib.import_module(MODULE)
        self.backend_type = getattr(module, TYPE)

        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.path = (
            Path(self.temp.name)
            / "reference-anchor.sqlite3"
        )

        self.anchor_signer = Ed25519PrivateKey.generate()
        self.authority_signer = Ed25519PrivateKey.generate()
        self.root_signer = Ed25519PrivateKey.generate()

        self.anchor_key = public_key(self.anchor_signer)
        self.authority_key = public_key(self.authority_signer)
        self.root_key = public_key(self.root_signer)

        self.anchor_id = "a44-test-anchor"
        self.authority_id = "a44-test-authority"
        self.root_id = "a44-test-root"
        self.epoch = 3

        self.initial = (
            self.authority_id,
            self.authority_key,
            self.root_id,
            self.root_key,
            self.epoch,
            10,
            20,
            30,
        )

        self.first = self.initial[:5] + (
            11, 21, 31
        )

        self.second = self.initial[:5] + (
            12, 22, 32
        )

        self.backend = self.backend_type.bootstrap(
            path=self.path,
            signer=self.anchor_signer,
            anchor_id=self.anchor_id,
            authority_id=self.authority_id,
            authority_public_key=self.authority_key,
            root_id=self.root_id,
            root_public_key=self.root_key,
            enrollment_epoch=self.epoch,
            initial_revision=10,
            initial_generation=20,
            initial_fence_token=30,
        )

    def reopened(self, **changes):
        values = {
            "path": self.path,
            "signer": self.anchor_signer,
            "expected_anchor_id": self.anchor_id,
            "expected_authority_id": self.authority_id,
            "expected_authority_public_key": self.authority_key,
            "expected_root_id": self.root_id,
            "expected_root_public_key": self.root_key,
            "expected_enrollment_epoch": self.epoch,
        }

        values.update(changes)

        return self.backend_type.open(**values)

    def pins(self, provider=None, *, floor=None):
        if provider is None:
            provider = self.backend

        if floor is None:
            floor = self.initial

        return {
            "provider": provider,
            "expected_anchor_id": self.anchor_id,
            "expected_anchor_public_key": self.anchor_key,
            "expected_authority_id": self.authority_id,
            "expected_authority_public_key": self.authority_key,
            "expected_root_id": self.root_id,
            "expected_root_public_key": self.root_key,
            "expected_enrollment_epoch": self.epoch,
            "minimum_revision": floor[5],
            "minimum_generation": floor[6],
            "minimum_fence_token": floor[7],
        }

    def client(self, provider=None, *, floor=None):
        return PinnedSignedCheckpointAnchorCASClient.from_provider(
            **self.pins(provider, floor=floor)
        )

    def source(self, provider=None, *, floor=None):
        return PinnedSignedCheckpointAnchorSource.from_provider(
            **self.pins(provider, floor=floor)
        )

    def read(self, provider=None, *, floor=None):
        with self.source(
            provider,
            floor=floor,
        ).hold() as snapshot:
            return snapshot

    def advance(self, provider=None, **changes):
        arguments = {
            "operation_id": OP_A,
            "expected_revision": 10,
            "next_revision": 11,
            "expected_generation": 20,
            "expected_fence_token": 30,
        }

        arguments.update(changes)

        return self.client(
            provider
        ).advance_if_current(**arguments)

    def lookup(
        self,
        operation_id=OP_A,
        provider=None,
        *,
        floor=None,
    ):
        return self.client(
            provider,
            floor=floor,
        ).lookup_operation(
            operation_id=operation_id
        )

    def direct_advance(self, **changes):
        arguments = {
            "operation_id": OP_A,
            "expected_revision": 10,
            "next_revision": 11,
            "expected_generation": 20,
            "expected_fence_token": 30,
            "challenge": b"\x11" * 32,
        }

        arguments.update(changes)

        return self.backend.advance_if_current(
            **arguments
        )

    def test_01_bootstrap_supports_pinned_signed_read(self):
        self.assertEqual(
            self.read(),
            self.initial,
        )

        self.assertTrue(
            self.path.is_file()
        )

        self.assertEqual(
            self.read(self.reopened()),
            self.initial,
        )

    def test_02_cas_signed_client_and_read_compatible(self):
        self.assertEqual(
            self.advance(),
            self.first,
        )

        self.assertEqual(
            self.read(),
            self.first,
        )

        self.assertEqual(
            self.lookup(),
            ("committed", self.first),
        )

    def test_03_repeated_id_is_idempotent(self):
        self.assertEqual(
            self.advance(),
            self.first,
        )

        self.assertEqual(
            self.advance(),
            self.first,
        )

        self.assertEqual(
            self.read(),
            self.first,
        )

    def test_04_idempotence_survives_reopen(self):
        self.assertEqual(
            self.advance(),
            self.first,
        )

        restarted = self.reopened()

        self.assertEqual(
            self.advance(restarted),
            self.first,
        )

        self.assertEqual(
            self.lookup(provider=restarted),
            ("committed", self.first),
        )

    def test_05_lost_ack_reconciled_after_reopen(self):
        class LostAckProvider:
            def __init__(self, underlying):
                self.underlying = underlying

            def __getattr__(self, name):
                return getattr(
                    self.underlying,
                    name,
                )

            def advance_if_current(self, **request):
                self.underlying.advance_if_current(
                    **request
                )

                raise TimeoutError(
                    "Acknowledgement lost after commit."
                )

        with self.assertRaises(ValueError):
            self.advance(
                LostAckProvider(self.backend)
            )

        restarted = self.reopened()

        self.assertEqual(
            self.lookup(provider=restarted),
            ("committed", self.first),
        )

        self.assertEqual(
            self.read(restarted),
            self.first,
        )

    def test_06_stale_cas_does_not_record_commit(self):
        with self.assertRaises(ValueError):
            self.advance(
                expected_revision=100,
                next_revision=101,
            )

        self.assertEqual(
            self.read(),
            self.initial,
        )

        self.assertEqual(
            self.lookup(),
            ("unknown", self.initial),
        )

    def test_07_operation_id_cannot_bind_different_request(self):
        self.assertEqual(
            self.advance(),
            self.first,
        )

        with self.assertRaises(ValueError):
            self.advance(
                next_revision=12
            )

        self.assertEqual(
            self.read(),
            self.first,
        )

    def test_08_sequential_commits_are_monotonic(self):
        self.assertEqual(
            self.advance(),
            self.first,
        )

        self.assertEqual(
            self.advance(
                operation_id=OP_B,
                expected_revision=11,
                next_revision=12,
                expected_generation=21,
                expected_fence_token=31,
            ),
            self.second,
        )

        self.assertEqual(
            self.read(self.reopened()),
            self.second,
        )

        self.assertEqual(
            self.lookup(OP_A),
            ("committed", self.second),
        )

        self.assertEqual(
            self.lookup(OP_B),
            ("committed", self.second),
        )

    def test_09_invalid_backend_requests_fail_closed(self):
        attacks = (
            {"operation_id": "invalid"},
            {"operation_id": "A" * 32},
            {"expected_revision": True},
            {"next_revision": 10},
            {"expected_generation": False},
            {"expected_fence_token": -1},
            {"challenge": b"short"},
        )

        for changes in attacks:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.direct_advance(
                        **changes
                    )

        with self.assertRaises(ValueError):
            self.backend.lookup_operation(
                operation_id="bad",
                challenge=b"\x22" * 32,
            )

        with self.assertRaises(ValueError):
            with self.backend.hold(
                challenge=b"short"
            ):
                pass

        self.assertEqual(
            self.read(),
            self.initial,
        )

    def test_10_open_missing_file_fails_closed(self):
        missing = (
            Path(self.temp.name)
            / "missing.sqlite3"
        )

        with self.assertRaises(ValueError):
            self.reopened(
                path=missing
            )

        self.assertFalse(
            missing.exists()
        )

    def test_11_open_mismatched_pins_fails_closed(self):
        attacks = (
            {"expected_anchor_id": "wrong"},
            {"expected_authority_id": "wrong"},
            {
                "expected_authority_public_key":
                b"\x01" * 32
            },
            {"expected_root_id": "wrong"},
            {
                "expected_root_public_key":
                b"\x02" * 32
            },
            {
                "expected_enrollment_epoch":
                self.epoch + 1
            },
            {
                "signer":
                Ed25519PrivateKey.generate()
            },
        )

        for changes in attacks:
            with self.subTest(
                changed_fields=tuple(changes)
            ):
                with self.assertRaises(ValueError):
                    self.reopened(
                        **changes
                    )

        self.assertEqual(
            self.read(),
            self.initial,
        )

    def test_12_failed_operation_insert_rolls_back_state(self):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute(
                """
                CREATE TRIGGER block_operation_insert
                BEFORE INSERT
                ON checkpoint_anchor_cas_operations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'injected operation write failure'
                    );
                END
                """
            )

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(
            self.read(self.reopened()),
            self.initial,
        )

        self.assertEqual(
            self.lookup(),
            ("unknown", self.initial),
        )

    def test_13_failed_state_update_rolls_back_operation(self):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute(
                """
                CREATE TRIGGER block_state_update
                BEFORE UPDATE
                ON checkpoint_anchor_cas_state
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'injected state write failure'
                    );
                END
                """
            )

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(
            self.read(self.reopened()),
            self.initial,
        )

        self.assertEqual(
            self.lookup(),
            ("unknown", self.initial),
        )

    def test_14_competing_cas_attempts_publish_at_most_once(self):
        def attempt(operation_id):
            try:
                snapshot = self.advance(
                    operation_id=operation_id
                )

                return True, snapshot

            except ValueError:
                return False, None

        with ThreadPoolExecutor(max_workers=2) as executor:
            responses = list(
                executor.map(
                    attempt,
                    (OP_A, OP_B),
                )
            )

        self.assertEqual(
            sum(success for success, _ in responses),
            1,
        )

        self.assertEqual(
            self.read(self.reopened()),
            self.first,
        )

        statuses = sorted((
            self.lookup(OP_A)[0],
            self.lookup(OP_B)[0],
        ))

        self.assertEqual(
            statuses,
            ["committed", "unknown"],
        )

    def test_15_bootstrap_never_overwrites_existing_store(self):
        with self.assertRaises(ValueError):
            self.backend_type.bootstrap(
                path=self.path,
                signer=self.anchor_signer,
                anchor_id=self.anchor_id,
                authority_id=self.authority_id,
                authority_public_key=self.authority_key,
                root_id=self.root_id,
                root_public_key=self.root_key,
                enrollment_epoch=self.epoch,
                initial_revision=0,
                initial_generation=0,
                initial_fence_token=0,
            )

        self.assertEqual(
            self.read(),
            self.initial,
        )

    def test_16_whole_file_rollback_remains_possible(self):
        """KNOWN LIMIT: local SQLite is not rollback-resistant."""

        backup = (
            Path(self.temp.name)
            / "before.sqlite3"
        )

        shutil.copyfile(
            self.path,
            backup,
        )

        self.assertEqual(
            self.advance(),
            self.first,
        )

        shutil.copyfile(
            backup,
            self.path,
        )

        restarted = self.reopened()

        self.assertEqual(
            self.read(restarted),
            self.initial,
        )

        self.assertEqual(
            self.lookup(provider=restarted),
            ("unknown", self.initial),
        )

        with self.assertRaises(ValueError):
            self.read(
                restarted,
                floor=self.first,
            )

    def test_17_no_restore_or_republish_capability(self):
        forbidden = (
            "restore",
            "republish",
            "publish",
            "reset",
            "force_advance",
        )

        for name in forbidden:
            self.assertFalse(
                hasattr(self.backend, name),
                name,
            )


if __name__ == "__main__":
    unittest.main()
