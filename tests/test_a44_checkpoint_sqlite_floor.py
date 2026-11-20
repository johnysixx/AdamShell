"""A44 checkpoint SQLite revision-floor contract.

EXPECTED RED: production SQLite checkpoint floor is absent.

Proposed API:

    SQLiteCheckpointRevisionFloorSource.bootstrap(
        path=Path,
        root_id=str,
        root_public_key=bytes,
        enrollment_epoch=int,
        minimum_revision=int,
    )

    SQLiteCheckpointRevisionFloorSource.open(
        path=Path,
        expected_root_id=str,
        expected_root_public_key=bytes,
        expected_epoch=int,
    )

    store.hold() -> context manager yielding:
        (root_id, root_public_key,
         enrollment_epoch, minimum_revision)

    store.advance_if_current(
        expected_revision=int,
        next_revision=int,
    ) -> resulting floor snapshot

Required properties:

- Exclusive database creation; no implicit replacement.
- Strict root key, identity, epoch and revision validation.
- Persistence across ordinary reopen operations.
- SQLite-transactional compare-and-swap publication.
- Strictly increasing revisions.
- Held read prevents concurrent revision publication.
- Stale writers fail without modifying the floor.
- Unusable and corrupted databases fail closed.
- Error paths release database transactions.
- No checkpoint restoration or republication API.

CRITICAL SECURITY LIMITATIONS:

SQLite is local durable storage, not an independently
authenticated root of trust.

A caller-selected root pin is not independently enrolled.

A local attacker able to replace the complete database
can replace it with a valid older copy.

The contract explicitly tests that rollback limitation.

Passing these tests does NOT prove:

- independent key enrollment;
- hostile filesystem rollback resistance;
- survival of power loss or storage-device failure;
- external-backend CAS linearizability;
- cross-system atomicity;
- independent authorization to restore checkpoints.

All databases are created in temporary test directories.
No real trust configuration or signing secret is stored.
"""

import importlib
import shutil
import tempfile
import unittest

from pathlib import Path

from cryptography.hazmat.primitives import (
    serialization,
)

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from test_a44_checkpoint_backend_trust_gate import (
    ROOT,
    OLD,
    NEXT,
    ENROLLMENT_EPOCH,
)


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_sqlite_floor"
)


class A44CheckpointSQLiteRevisionFloorContractTests(
    unittest.TestCase
):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.store_type = (
            module.SQLiteCheckpointRevisionFloorSource
        )

        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)

        self.path = (
            Path(self.folder.name)
            / "checkpoint-revision-floor.sqlite3"
        )

        private = Ed25519PrivateKey.generate()

        self.root_public_key = (
            private.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
        )

    def bootstrap(self, **changes):
        arguments = {
            "path": self.path,
            "root_id": ROOT,
            "root_public_key": self.root_public_key,
            "enrollment_epoch": ENROLLMENT_EPOCH,
            "minimum_revision": OLD,
        }

        arguments.update(changes)

        return self.store_type.bootstrap(**arguments)

    def reopen(self, **changes):
        arguments = {
            "path": self.path,
            "expected_root_id": ROOT,
            "expected_root_public_key": self.root_public_key,
            "expected_epoch": ENROLLMENT_EPOCH,
        }

        arguments.update(changes)

        return self.store_type.open(**arguments)

    @staticmethod
    def snapshot(store):
        with store.hold() as snapshot:
            return snapshot

    def expected(self, revision=OLD):
        return (
            ROOT,
            self.root_public_key,
            ENROLLMENT_EPOCH,
            revision,
        )

    def test_bootstrap_held_snapshot_and_explicit_identity(self):
        store = self.bootstrap()

        self.assertTrue(self.path.is_file())

        with store.hold() as snapshot:
            self.assertIs(type(snapshot), tuple)
            self.assertEqual(len(snapshot), 4)

            self.assertEqual(
                snapshot,
                self.expected(),
            )

            self.assertIs(type(snapshot[1]), bytes)
            self.assertIs(type(snapshot[2]), int)
            self.assertIs(type(snapshot[3]), int)

        self.assertEqual(
            self.snapshot(store),
            self.expected(),
        )

    def test_reopen_preserves_published_floor(self):
        store = self.bootstrap()

        publication = store.advance_if_current(
            expected_revision=OLD,
            next_revision=NEXT,
        )

        self.assertEqual(
            publication,
            self.expected(NEXT),
        )

        # A new handle simulates an ordinary process reopen,
        # not a crash, power failure or hostile rollback.
        reopened = self.reopen()

        self.assertEqual(
            self.snapshot(reopened),
            self.expected(NEXT),
        )

    def test_existing_database_cannot_be_rebootstrapped(
        self
    ):
        store = self.bootstrap()

        before = self.path.read_bytes()

        with self.assertRaises(ValueError):
            self.bootstrap(
                minimum_revision=OLD - 1
            )

        self.assertEqual(
            self.path.read_bytes(),
            before,
        )

        self.assertEqual(
            self.snapshot(store),
            self.expected(),
        )

    def test_missing_and_corrupt_database_fail_closed(
        self
    ):
        self.assertFalse(self.path.exists())

        with self.assertRaises(ValueError):
            self.reopen()

        self.assertFalse(self.path.exists())

        self.path.write_bytes(
            b"not-a-sqlite-database"
        )

        with self.assertRaises(ValueError):
            self.reopen()

    def test_invalid_bootstrap_inputs_do_not_create_store(
        self
    ):
        invalid = (
            {"root_id": None},
            {"root_id": ""},
            {"root_id": True},
            {"root_id": " invalid"},
            {"root_public_key": b"short"},
            {
                "root_public_key": bytearray(
                    self.root_public_key
                )
            },
            {"enrollment_epoch": True},
            {"enrollment_epoch": -1},
            {"enrollment_epoch": "2"},
            {"minimum_revision": True},
            {"minimum_revision": -1},
            {"minimum_revision": "12"},
        )

        for changes in invalid:
            with self.subTest(changes=repr(changes)[:90]):
                with self.assertRaises(ValueError):
                    self.bootstrap(**changes)

                self.assertFalse(
                    self.path.exists()
                )

    def test_reopen_requires_matching_root_and_epoch(
        self
    ):
        store = self.bootstrap()

        invalid = (
            {"expected_root_id": "foreign_root"},
            {"expected_root_id": ""},
            {"expected_root_id": True},
            {
                "expected_root_public_key":
                    b"\x42" * 32
            },
            {
                "expected_root_public_key":
                    bytearray(self.root_public_key)
            },
            {
                "expected_epoch":
                    ENROLLMENT_EPOCH + 1
            },
            {"expected_epoch": True},
            {"expected_epoch": -1},
        )

        for changes in invalid:
            with self.subTest(changes=repr(changes)[:90]):
                with self.assertRaises(ValueError):
                    self.reopen(**changes)

        self.assertEqual(
            self.snapshot(store),
            self.expected(),
        )

    def test_cas_advances_monotonically_and_returns_snapshot(
        self
    ):
        store = self.bootstrap()

        result = store.advance_if_current(
            expected_revision=OLD,
            next_revision=NEXT,
        )

        self.assertEqual(
            result,
            self.expected(NEXT),
        )

        self.assertEqual(
            self.snapshot(store),
            self.expected(NEXT),
        )

        with self.assertRaises(ValueError):
            store.advance_if_current(
                expected_revision=OLD,
                next_revision=NEXT,
            )

        self.assertEqual(
            self.snapshot(store),
            self.expected(NEXT),
        )

    def test_invalid_cas_preconditions_never_change_floor(
        self
    ):
        store = self.bootstrap()

        invalid = (
            (True, NEXT),
            (-1, NEXT),
            (OLD - 1, NEXT),
            ("12", NEXT),
            (OLD, True),
            (OLD, -1),
            (OLD, OLD),
            (OLD, OLD - 1),
            (OLD, "13"),
            (OLD, 13.0),
        )

        for predecessor, target in invalid:
            with self.subTest(
                predecessor=repr(predecessor),
                target=repr(target),
            ):
                with self.assertRaises(ValueError):
                    store.advance_if_current(
                        expected_revision=predecessor,
                        next_revision=target,
                    )

                self.assertEqual(
                    self.snapshot(store),
                    self.expected(),
                )

    def test_two_handles_reject_stale_cas_publication(
        self
    ):
        first = self.bootstrap()
        second = self.reopen()

        first.advance_if_current(
            expected_revision=OLD,
            next_revision=NEXT,
        )

        with self.assertRaises(ValueError):
            second.advance_if_current(
                expected_revision=OLD,
                next_revision=NEXT + 1,
            )

        self.assertEqual(
            self.snapshot(first),
            self.expected(NEXT),
        )

        self.assertEqual(
            self.snapshot(second),
            self.expected(NEXT),
        )

        second.advance_if_current(
            expected_revision=NEXT,
            next_revision=NEXT + 1,
        )

        self.assertEqual(
            self.snapshot(first),
            self.expected(NEXT + 1),
        )

    def test_held_read_blocks_conflicting_publication(
        self
    ):
        first = self.bootstrap()
        second = self.reopen()

        with first.hold() as snapshot:
            self.assertEqual(
                snapshot,
                self.expected(),
            )

            # A second SQLite connection cannot publish
            # while the held revision transaction is active.
            with self.assertRaises(ValueError):
                second.advance_if_current(
                    expected_revision=OLD,
                    next_revision=NEXT,
                )

            self.assertEqual(
                snapshot[3],
                OLD,
            )

        # The failed writer does not poison later work.
        result = second.advance_if_current(
            expected_revision=OLD,
            next_revision=NEXT,
        )

        self.assertEqual(
            result,
            self.expected(NEXT),
        )

    def test_caller_error_releases_held_transaction(
        self
    ):
        first = self.bootstrap()
        second = self.reopen()

        with self.assertRaises(
            (RuntimeError, ValueError)
        ):
            with first.hold():
                raise RuntimeError(
                    "Injected caller failure."
                )

        # A leaked read transaction would prevent CAS.
        publication = second.advance_if_current(
            expected_revision=OLD,
            next_revision=NEXT,
        )

        self.assertEqual(
            publication,
            self.expected(NEXT),
        )

    def test_file_replacement_rollback_remains_possible(
        self
    ):
        store = self.bootstrap()

        old_copy = (
            Path(self.folder.name)
            / "older-valid-floor.sqlite3"
        )

        shutil.copyfile(
            self.path,
            old_copy,
        )

        store.advance_if_current(
            expected_revision=OLD,
            next_revision=NEXT,
        )

        self.assertEqual(
            self.snapshot(self.reopen()),
            self.expected(NEXT),
        )

        # ATTACK SIMULATION:
        # Replace the complete local database with
        # an earlier otherwise valid database copy.
        shutil.copyfile(
            old_copy,
            self.path,
        )

        reopened = self.reopen()

        self.assertEqual(
            self.snapshot(reopened),
            self.expected(OLD),
        )

        # EXPECTED LIMITATION:
        # No external monotonic anchor knows NEXT existed.
        # SQLite alone cannot reject valid older file copies.

        for name in (
            "restore",
            "republish",
            "authorize",
        ):
            with self.subTest(name=name):
                self.assertFalse(
                    hasattr(reopened, name)
                )


if __name__ == "__main__":
    unittest.main()
