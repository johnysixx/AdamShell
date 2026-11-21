"""A44 / 66.26D SQLite reference backend adversarial tests.

Covers:
- competing CAS operations and duplicate operation IDs
- restart recovery and lost acknowledgements
- historical idempotent receipts
- injected failure during second publication
- corrupted state, identities and operation records
- missing tables, corrupt files and unsupported WAL mode
- whole-file rollback as a KNOWN security limitation

All databases are local temporary SQLite reference stores.

Passing these tests does NOT prove remote independence,
power-loss durability, hardware-protected signing keys,
rollback resistance or cross-store atomicity.
"""

import shutil
import sqlite3
import sys
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_anchor_cas_backend_contract as contract


OP_A = contract.OP_A
OP_B = contract.OP_B
OP_C = "c" * 32
OP_D = "d" * 32


class A44AnchorCASBackendAdversarialTests(unittest.TestCase):

    def setUp(self):
        self.fixture = (
            contract.A44AnchorCASBackendAtomicRecoveryContractTests(
                "test_01_bootstrap_supports_pinned_signed_read"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.path = self.fixture.path
        self.initial = self.fixture.initial
        self.first = self.fixture.first
        self.second = self.fixture.second

    def _sql(self, statement, parameters=()):
        with closing(sqlite3.connect(self.path)) as db:
            with db:
                return db.execute(
                    statement,
                    parameters,
                ).rowcount

    def _rows(self):
        with closing(sqlite3.connect(self.path)) as db:
            row = db.execute(
                "SELECT COUNT(*) "
                "FROM checkpoint_anchor_cas_operations"
            ).fetchone()

        return row[0]

    def _second_commit(self):
        return self.fixture.advance(
            operation_id=OP_B,
            expected_revision=11,
            next_revision=12,
            expected_generation=21,
            expected_fence_token=31,
        )

    def test_01_multiple_commits_survive_reopen(self):
        for i in range(4):
            published = self.fixture.advance(
                operation_id=f"{i + 1:032x}",
                expected_revision=10 + i,
                next_revision=11 + i,
                expected_generation=20 + i,
                expected_fence_token=30 + i,
            )

            self.assertEqual(
                published[5:],
                (11 + i, 21 + i, 31 + i),
            )

        final = self.initial[:5] + (14, 24, 34)

        reopened = self.fixture.reopened()

        self.assertEqual(
            self.fixture.read(reopened),
            final,
        )

        for i in range(4):
            status, snapshot = self.fixture.lookup(
                operation_id=f"{i + 1:032x}",
                provider=reopened,
            )

            self.assertEqual(status, "committed")
            self.assertEqual(snapshot, final)

        self.assertEqual(self._rows(), 4)

    def test_02_old_idempotent_receipt_never_rewinds_state(self):
        self.assertEqual(
            self.fixture.advance(),
            self.first,
        )

        self.assertEqual(
            self._second_commit(),
            self.second,
        )

        reopened = self.fixture.reopened()

        historical_receipt = self.fixture.advance(
            reopened
        )

        self.assertEqual(
            historical_receipt,
            self.first,
        )

        self.assertEqual(
            self.fixture.read(reopened),
            self.second,
        )

        self.assertEqual(self._rows(), 2)

    def test_03_concurrent_duplicate_id_commits_once(self):
        def attempt(_):
            return self.fixture.advance()

        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(
                pool.map(attempt, range(2))
            )

        self.assertEqual(
            responses,
            [self.first, self.first],
        )

        self.assertEqual(
            self.fixture.read(self.fixture.reopened()),
            self.first,
        )

        self.assertEqual(self._rows(), 1)

    def test_04_concurrent_distinct_ids_have_one_winner(self):
        ids = (OP_A, OP_B, OP_C, OP_D)

        def attempt(operation_id):
            try:
                result = self.fixture.advance(
                    operation_id=operation_id,
                )

                return operation_id, result

            except ValueError:
                return operation_id, None

        with ThreadPoolExecutor(max_workers=4) as pool:
            outcomes = list(
                pool.map(attempt, ids)
            )

        winners = [
            operation_id
            for operation_id, snapshot in outcomes
            if snapshot == self.first
        ]

        self.assertEqual(len(winners), 1)

        self.assertEqual(
            self.fixture.read(self.fixture.reopened()),
            self.first,
        )

        self.assertEqual(self._rows(), 1)

        for operation_id in ids:
            status, snapshot = self.fixture.lookup(
                operation_id=operation_id
            )

            expected_status = (
                "committed"
                if operation_id == winners[0]
                else "unknown"
            )

            self.assertEqual(status, expected_status)
            self.assertEqual(snapshot, self.first)

    def test_05_unknown_lookup_survives_reopen_without_write(self):
        reopened = self.fixture.reopened()

        for operation_id in (OP_A, OP_B):
            status, snapshot = self.fixture.lookup(
                operation_id=operation_id,
                provider=reopened,
            )

            self.assertEqual(status, "unknown")
            self.assertEqual(snapshot, self.initial)

        self.assertEqual(self._rows(), 0)

        self.assertEqual(
            self.fixture.read(reopened),
            self.initial,
        )

    def test_06_lost_ack_recovery_prevents_duplicate_commit(self):
        class LostAck:
            def __init__(self, backend):
                self.backend = backend

            def __getattr__(self, name):
                return getattr(self.backend, name)

            def advance_if_current(self, **request):
                self.backend.advance_if_current(
                    **request
                )

                raise TimeoutError(
                    "Simulated lost acknowledgement."
                )

        with self.assertRaises(ValueError):
            self.fixture.advance(
                LostAck(self.fixture.backend)
            )

        reopened = self.fixture.reopened()

        self.assertEqual(
            self.fixture.lookup(provider=reopened),
            ("committed", self.first),
        )

        self.assertEqual(
            self.fixture.advance(reopened),
            self.first,
        )

        self.assertEqual(
            self.fixture.read(reopened),
            self.first,
        )

        self.assertEqual(self._rows(), 1)

    def test_07_second_operation_insert_failure_preserves_first(self):
        self.assertEqual(
            self.fixture.advance(),
            self.first,
        )

        self._sql(
            "CREATE TRIGGER reject_second_insert "
            "BEFORE INSERT ON checkpoint_anchor_cas_operations "
            f"WHEN NEW.operation_id = '{OP_B}' "
            "BEGIN "
            "SELECT RAISE(ABORT, 'injected second insert failure'); "
            "END"
        )

        with self.assertRaises(ValueError):
            self._second_commit()

        reopened = self.fixture.reopened()

        self.assertEqual(
            self.fixture.read(reopened),
            self.first,
        )

        self.assertEqual(
            self.fixture.lookup(provider=reopened),
            ("committed", self.first),
        )

        self.assertEqual(
            self.fixture.lookup(
                operation_id=OP_B,
                provider=reopened,
            ),
            ("unknown", self.first),
        )

        self.assertEqual(self._rows(), 1)

    def test_08_second_state_update_failure_preserves_first(self):
        self.assertEqual(
            self.fixture.advance(),
            self.first,
        )

        self._sql(
            "CREATE TRIGGER reject_second_update "
            "BEFORE UPDATE ON checkpoint_anchor_cas_state "
            "WHEN OLD.revision = 11 "
            "BEGIN "
            "SELECT RAISE(ABORT, 'injected second update failure'); "
            "END"
        )

        with self.assertRaises(ValueError):
            self._second_commit()

        reopened = self.fixture.reopened()

        self.assertEqual(
            self.fixture.read(reopened),
            self.first,
        )

        self.assertEqual(
            self.fixture.lookup(provider=reopened),
            ("committed", self.first),
        )

        self.assertEqual(
            self.fixture.lookup(
                operation_id=OP_B,
                provider=reopened,
            ),
            ("unknown", self.first),
        )

        self.assertEqual(self._rows(), 1)

    def test_09_negative_persisted_counter_rejected(self):
        self._sql(
            "UPDATE checkpoint_anchor_cas_state "
            "SET revision = -1 "
            "WHERE singleton_id = 1"
        )

        with self.assertRaises(ValueError):
            self.fixture.read()

        with self.assertRaises(ValueError):
            self.fixture.reopened()

        with self.assertRaises(ValueError):
            self.fixture.lookup()

        self.assertEqual(self._rows(), 0)

    def test_10_modified_stored_anchor_key_rejected(self):
        self._sql(
            "UPDATE checkpoint_anchor_cas_state "
            "SET anchor_public_key = ? "
            "WHERE singleton_id = 1",
            (b"\x01" * 32,),
        )

        with self.assertRaises(ValueError):
            self.fixture.read()

        with self.assertRaises(ValueError):
            self.fixture.reopened()

    def test_11_modified_stored_authority_key_rejected(self):
        self._sql(
            "UPDATE checkpoint_anchor_cas_state "
            "SET authority_public_key = ? "
            "WHERE singleton_id = 1",
            (b"\x02" * 32,),
        )

        with self.assertRaises(ValueError):
            self.fixture.read()

        with self.assertRaises(ValueError):
            self.fixture.reopened()

    def test_12_modified_stored_root_key_rejected(self):
        self._sql(
            "UPDATE checkpoint_anchor_cas_state "
            "SET root_public_key = ? "
            "WHERE singleton_id = 1",
            (b"\x03" * 32,),
        )

        with self.assertRaises(ValueError):
            self.fixture.read()

        with self.assertRaises(ValueError):
            self.fixture.reopened()

    def test_13_corrupted_operation_record_fails_closed(self):
        self.assertEqual(
            self.fixture.advance(),
            self.first,
        )

        self._sql(
            "UPDATE checkpoint_anchor_cas_operations "
            "SET committed_generation = committed_generation + 5 "
            "WHERE operation_id = ?",
            (OP_A,),
        )

        reopened = self.fixture.reopened()

        # The state row remains readable.
        self.assertEqual(
            self.fixture.read(reopened),
            self.first,
        )

        # The operation receipt must not be accepted.
        with self.assertRaises(ValueError):
            self.fixture.lookup(provider=reopened)

        with self.assertRaises(ValueError):
            self.fixture.advance(reopened)

        self.assertEqual(self._rows(), 1)

    def test_14_missing_operation_table_fails_closed(self):
        self._sql(
            "DROP TABLE checkpoint_anchor_cas_operations"
        )

        self.assertEqual(
            self.fixture.read(),
            self.initial,
        )

        with self.assertRaises(ValueError):
            self.fixture.advance()

        with self.assertRaises(ValueError):
            self.fixture.lookup()

        self.assertEqual(
            self.fixture.read(),
            self.initial,
        )

    def test_15_missing_state_table_rejects_open(self):
        self._sql(
            "DROP TABLE checkpoint_anchor_cas_state"
        )

        with self.assertRaises(ValueError):
            self.fixture.reopened()

        with self.assertRaises(ValueError):
            self.fixture.read()

    def test_16_corrupt_database_image_rejected(self):
        # No SQLite connections are left open.
        self.path.write_bytes(
            b"not a valid SQLite database image"
        )

        with self.assertRaises(ValueError):
            self.fixture.reopened()

        with self.assertRaises(ValueError):
            self.fixture.read()

    def test_17_unsupported_wal_mode_rejected(self):
        with closing(sqlite3.connect(self.path)) as db:
            mode = db.execute(
                "PRAGMA journal_mode=WAL"
            ).fetchone()

            self.assertEqual(
                mode[0].lower(),
                "wal",
            )

        with self.assertRaises(ValueError):
            self.fixture.reopened()

        with self.assertRaises(ValueError):
            self.fixture.read()

    def test_18_whole_file_rollback_is_known_limit(self):
        """KNOWN LIMIT: old local DB image restores old counters."""

        backup = (
            Path(self.fixture.temp.name)
            / "precommit-backup.sqlite3"
        )

        shutil.copyfile(
            self.path,
            backup,
        )

        self.assertEqual(
            self.fixture.advance(),
            self.first,
        )

        self.assertEqual(self._rows(), 1)

        # Local database and operation log roll back together.
        shutil.copyfile(
            backup,
            self.path,
        )

        reopened = self.fixture.reopened()

        self.assertEqual(
            self.fixture.read(reopened),
            self.initial,
        )

        self.assertEqual(
            self.fixture.lookup(provider=reopened),
            ("unknown", self.initial),
        )

        self.assertEqual(self._rows(), 0)

        # A separately preserved high-water floor would reject it.
        with self.assertRaises(ValueError):
            self.fixture.read(
                reopened,
                floor=self.first,
            )


if __name__ == "__main__":
    unittest.main()
