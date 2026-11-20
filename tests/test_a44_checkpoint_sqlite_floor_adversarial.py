"""A44 adversarial SQLite checkpoint revision-floor tests.

Eleven regression scenarios verify:

- invalid and mutated pins;
- tampered database rows and schemas;
- singleton integrity;
- stale CAS rejection;
- external SQLite writer locks;
- rollback-journal read/write exclusion;
- SQL parameter safety;
- integration with the checkpoint trust gate;
- whole-file rollback limitations.

One additional test is deliberately EXPECTED RED:

    test_wal_mode_must_not_bypass_held_floor

It detects whether an externally changed SQLite WAL mode
can bypass the held-read publication exclusion contract.

All files are created inside temporary test directories.

This suite does NOT establish independent key enrollment,
hostile filesystem rollback resistance, power-loss
durability or cross-backend atomicity.
"""

import shutil
import sqlite3
import sys
import unittest

from contextlib import closing
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_sqlite_floor as contract
import test_a44_checkpoint_backend_trust_gate as gate_contract


OLD = contract.OLD
NEXT = contract.NEXT

ROOT = contract.ROOT
EPOCH = contract.ENROLLMENT_EPOCH


class A44CheckpointSQLiteFloorAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44CheckpointSQLiteRevisionFloorContractTests(
                "test_bootstrap_held_snapshot_and_explicit_identity"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.store = self.fixture.bootstrap()
        self.path = self.fixture.path

    def snapshot(self, store=None):
        if store is None:
            store = self.store

        return self.fixture.snapshot(store)

    def sql(self, statement, parameters=()):
        with closing(
            sqlite3.connect(
                self.path,
                isolation_level=None,
                timeout=0.15,
            )
        ) as connection:
            return connection.execute(
                statement,
                parameters,
            ).fetchall()

    def test_mutated_instance_pins_rejected(self):
        mutations = (
            ("_path", object()),
            ("expected_root_id", ""),
            ("expected_root_id", True),
            ("expected_root_id", "foreign_root"),
            ("expected_root_public_key", b"short"),
            (
                "expected_root_public_key",
                bytearray(self.fixture.root_public_key),
            ),
            ("expected_epoch", True),
            ("expected_epoch", -1),
        )

        for field, replacement in mutations:
            with self.subTest(field=field):
                store = self.fixture.reopen()

                object.__setattr__(
                    store,
                    field,
                    replacement,
                )

                with self.assertRaises(ValueError):
                    self.snapshot(store)

        self.assertEqual(
            self.snapshot(),
            self.fixture.expected(),
        )

    def test_tampered_root_key_and_epoch_rejected(self):
        valid = self.fixture.expected()

        mutations = (
            ("root_id", "forged_root", valid[0]),
            ("root_public_key", b"X" * 32, valid[1]),
            ("root_public_key", b"short", valid[1]),
            ("enrollment_epoch", EPOCH + 1, valid[2]),
        )

        for column, malicious, restored in mutations:
            with self.subTest(column=column, value=repr(malicious)):
                self.sql(
                    "UPDATE checkpoint_revision_floor "
                    f"SET {column} = ? WHERE singleton_id = 1",
                    (malicious,),
                )

                with self.assertRaises(ValueError):
                    self.fixture.reopen()

                with self.assertRaises(ValueError):
                    self.snapshot()

                with self.assertRaises(ValueError):
                    self.store.advance_if_current(
                        expected_revision=OLD,
                        next_revision=NEXT,
                    )

                self.sql(
                    "UPDATE checkpoint_revision_floor "
                    f"SET {column} = ? WHERE singleton_id = 1",
                    (restored,),
                )

                self.assertEqual(
                    self.snapshot(),
                    valid,
                )

    def test_missing_singleton_fails_closed(self):
        self.sql(
            "DELETE FROM checkpoint_revision_floor "
            "WHERE singleton_id = 1"
        )

        with self.assertRaises(ValueError):
            self.fixture.reopen()

        with self.assertRaises(ValueError):
            self.snapshot()

        with self.assertRaises(ValueError):
            self.store.advance_if_current(
                expected_revision=OLD,
                next_revision=NEXT,
            )

        rows = self.sql(
            "SELECT COUNT(*) FROM checkpoint_revision_floor"
        )

        self.assertEqual(rows, [(0,)])

    def test_duplicate_singleton_cannot_be_inserted(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.sql(
                "INSERT INTO checkpoint_revision_floor "
                "(singleton_id, root_id, root_public_key, "
                "enrollment_epoch, minimum_revision) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    1,
                    ROOT,
                    self.fixture.root_public_key,
                    EPOCH,
                    NEXT,
                ),
            )

        self.assertEqual(
            self.snapshot(),
            self.fixture.expected(),
        )

    def test_schema_replacement_fails_closed(self):
        self.sql(
            "DROP TABLE checkpoint_revision_floor"
        )

        self.sql(
            "CREATE TABLE checkpoint_revision_floor "
            "(singleton_id INTEGER PRIMARY KEY, "
            "minimum_revision INTEGER)"
        )

        with self.assertRaises(ValueError):
            self.fixture.reopen()

        with self.assertRaises(ValueError):
            self.snapshot()

        with self.assertRaises(ValueError):
            self.store.advance_if_current(
                expected_revision=OLD,
                next_revision=NEXT,
            )

    def test_stale_cas_cannot_lower_or_replace_floor(self):
        stale = self.fixture.reopen()

        self.store.advance_if_current(
            expected_revision=OLD,
            next_revision=NEXT,
        )

        for previous, target in (
            (OLD, NEXT + 1),
            (NEXT, OLD),
            (NEXT, NEXT),
            (NEXT, True),
            (True, NEXT + 1),
        ):
            with self.subTest(previous=repr(previous), target=repr(target)):
                with self.assertRaises(ValueError):
                    stale.advance_if_current(
                        expected_revision=previous,
                        next_revision=target,
                    )

                self.assertEqual(
                    self.snapshot(),
                    self.fixture.expected(NEXT),
                )

    def test_external_write_lock_blocks_cas_then_recovers(
        self
    ):
        with closing(
            sqlite3.connect(
                self.path,
                isolation_level=None,
                timeout=0.15,
            )
        ) as blocker:
            blocker.execute("BEGIN IMMEDIATE")

            try:
                with self.assertRaises(ValueError):
                    self.store.advance_if_current(
                        expected_revision=OLD,
                        next_revision=NEXT,
                    )

            finally:
                if blocker.in_transaction:
                    blocker.rollback()

        self.assertEqual(
            self.snapshot(),
            self.fixture.expected(),
        )

        self.assertEqual(
            self.store.advance_if_current(
                expected_revision=OLD,
                next_revision=NEXT,
            ),
            self.fixture.expected(NEXT),
        )

    def test_delete_mode_held_read_blocks_raw_writer_commit(
        self
    ):
        mode = self.sql("PRAGMA journal_mode")[0][0]

        self.assertEqual(
            mode.lower(),
            "delete",
        )

        with self.store.hold() as held:
            self.assertEqual(
                held,
                self.fixture.expected(),
            )

            with closing(
                sqlite3.connect(
                    self.path,
                    isolation_level=None,
                    timeout=0.15,
                )
            ) as writer:
                writer.execute("BEGIN IMMEDIATE")

                try:
                    writer.execute(
                        "UPDATE checkpoint_revision_floor "
                        "SET minimum_revision = ? "
                        "WHERE singleton_id = 1",
                        (NEXT,),
                    )

                    with self.assertRaises(
                        sqlite3.OperationalError
                    ):
                        writer.commit()

                finally:
                    if writer.in_transaction:
                        writer.rollback()

            self.assertEqual(
                held[3],
                OLD,
            )

        self.assertEqual(
            self.snapshot(),
            self.fixture.expected(),
        )

        self.store.advance_if_current(
            expected_revision=OLD,
            next_revision=NEXT,
        )

        self.assertEqual(
            self.snapshot(),
            self.fixture.expected(NEXT),
        )

    def test_root_identity_is_sql_parameter_not_sql_code(
        self
    ):
        unusual_root = (
            "root'); DROP TABLE checkpoint_revision_floor; --"
        )

        alternate_path = (
            Path(self.fixture.folder.name)
            / "parameterized-root.sqlite3"
        )

        store_type = type(self.store)

        alternate = store_type.bootstrap(
            path=alternate_path,
            root_id=unusual_root,
            root_public_key=self.fixture.root_public_key,
            enrollment_epoch=EPOCH,
            minimum_revision=OLD,
        )

        with alternate.hold() as snapshot:
            self.assertEqual(
                snapshot[0],
                unusual_root,
            )

        reopened = store_type.open(
            path=alternate_path,
            expected_root_id=unusual_root,
            expected_root_public_key=self.fixture.root_public_key,
            expected_epoch=EPOCH,
        )

        self.assertEqual(
            self.fixture.snapshot(reopened)[3],
            OLD,
        )

        self.assertEqual(
            self.snapshot(),
            self.fixture.expected(),
        )

    def test_sqlite_floor_integrates_with_held_trust_gate(
        self
    ):
        trust = (
            gate_contract.A44CheckpointBackendTrustGateContractTests(
                "test_valid_nested_held_trust_and_signed_read"
            )
        )

        trust.setUp()
        self.addCleanup(trust.doCleanups)

        integrated_path = (
            Path(self.fixture.folder.name)
            / "integrated-trust-floor.sqlite3"
        )

        store_type = type(self.store)

        integrated = store_type.bootstrap(
            path=integrated_path,
            root_id=ROOT,
            root_public_key=trust.fixture.root_public,
            enrollment_epoch=EPOCH,
            minimum_revision=OLD,
        )

        another = store_type.open(
            path=integrated_path,
            expected_root_id=ROOT,
            expected_root_public_key=trust.fixture.root_public,
            expected_epoch=EPOCH,
        )

        gate = trust.make_gate(
            revision_floor_source=integrated,
        )

        with gate.hold() as snapshot:
            self.assertEqual(
                snapshot[2],
                OLD,
            )

            self.assertTrue(trust.enrollment.active)
            self.assertTrue(trust.backend.active)

            with self.assertRaises(ValueError):
                another.advance_if_current(
                    expected_revision=OLD,
                    next_revision=NEXT,
                )

        self.assertFalse(trust.enrollment.active)
        self.assertFalse(trust.backend.active)

        self.assertEqual(
            another.advance_if_current(
                expected_revision=OLD,
                next_revision=NEXT,
            )[3],
            NEXT,
        )

        # Backend remains OLD, but held floor is now NEXT.
        with self.assertRaises(ValueError):
            with gate.hold():
                pass

        self.assertEqual(
            trust.backend.revision,
            OLD,
        )

    def test_valid_older_file_copy_can_still_rollback(
        self
    ):
        old_copy = (
            Path(self.fixture.folder.name)
            / "old-valid-checkpoint-floor.sqlite3"
        )

        shutil.copyfile(
            self.path,
            old_copy,
        )

        self.store.advance_if_current(
            expected_revision=OLD,
            next_revision=NEXT,
        )

        self.assertEqual(
            self.snapshot(self.fixture.reopen()),
            self.fixture.expected(NEXT),
        )

        shutil.copyfile(
            old_copy,
            self.path,
        )

        # This is a documented limitation, not a protection.
        self.assertEqual(
            self.snapshot(self.fixture.reopen()),
            self.fixture.expected(OLD),
        )

        for name in (
            "restore",
            "republish",
            "authorize",
        ):
            with self.subTest(name=name):
                self.assertFalse(
                    hasattr(self.store, name)
                )

    def test_wal_mode_must_not_bypass_held_floor(self):
        """EXPECTED RED until journal mode is enforced on open.

        An external actor changes a valid SQLite database from
        DELETE to WAL. In WAL, a writer can commit while a
        reader holds an active snapshot.

        The floor source must reject the unsupported mode
        before treating held reads as publication exclusion.
        """

        with closing(
            sqlite3.connect(
                self.path,
                isolation_level=None,
                timeout=0.15,
            )
        ) as connection:
            changed = connection.execute(
                "PRAGMA journal_mode=WAL"
            ).fetchone()[0]

        self.assertEqual(
            changed.lower(),
            "wal",
        )

        try:
            reopened = self.fixture.reopen()

        except ValueError:
            # Correct hardening may reject WAL at open.
            return

        # If the source permits opening, it must still
        # fail closed rather than expose an unsafe lease.
        try:
            with reopened.hold() as held:
                self.assertEqual(
                    held[3],
                    OLD,
                )

                contender = self.fixture.reopen()

                contender.advance_if_current(
                    expected_revision=OLD,
                    next_revision=NEXT,
                )

        except ValueError:
            # Correct hardening may reject hold or CAS.
            return

        self.fail(
            "WAL mode allowed checkpoint floor CAS to commit "
            "during an active held read transaction."
        )


if __name__ == "__main__":
    unittest.main()
