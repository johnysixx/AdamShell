"""A44 / 66.32D: adversarial SQLite provisioning-generation tests.

This is a LOCAL SQLite reference only, not a rollback-resistant trust root.
Every test uses a temporary database from the existing contract fixture.
"""

import shutil
import sqlite3
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_a44_checkpoint_protected_provisioning_floor_sqlite_backend_contract as sqlite_contract

OP_A = "a" * 32
OP_B = "b" * 32
OP_C = "c" * 32
OP_D = "d" * 32

STATE = "provisioning_generation_state"
OPERATIONS = "provisioning_generation_operations"


class A44ProvisioningGenerationSQLiteBackendAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.fixture = sqlite_contract.A44ProvisioningGenerationSQLiteBackendContractTests(
            "test_01_bootstrap_signed_initial_read"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def sql(self, statement, parameters=()):
        with closing(sqlite3.connect(self.fixture.path, timeout=5)) as db:
            with db:
                return db.execute(statement, parameters).rowcount

    def count(self):
        with closing(sqlite3.connect(self.fixture.path, timeout=5)) as db:
            return db.execute(
                f"SELECT COUNT(*) FROM {OPERATIONS}"
            ).fetchone()[0]

    def client(self, backend=None):
        return (
            self.fixture.client()
            if backend is None
            else self.fixture.client(backend=backend)
        )

    def advance(self, operation_id=OP_A, expected=1, proposed=2, backend=None):
        return self.client(backend).advance_if_current(
            operation_id=operation_id,
            expected_generation=expected,
            next_generation=proposed,
        )

    def lookup(self, operation_id=OP_A, backend=None):
        return self.client(backend).lookup_operation(operation_id=operation_id)

    def test_01_stored_authority_id_substitution_rejected(self):
        self.sql(f"UPDATE {STATE} SET authority_id=?", ("evil-authority",))
        with self.assertRaises(ValueError):
            self.client().read_generation()
        with self.assertRaises(ValueError):
            self.fixture.reopened()

    def test_02_stored_subject_id_substitution_rejected(self):
        self.sql(f"UPDATE {STATE} SET subject_id=?", ("evil-subject",))
        with self.assertRaises(ValueError):
            self.client().read_generation()

    def test_03_negative_generation_rejected(self):
        try:
            self.sql(f"UPDATE {STATE} SET generation=-1")
        except sqlite3.IntegrityError:
            self.assertEqual(self.client().read_generation(), 1)
            return
        with self.assertRaises(ValueError):
            self.client().read_generation()

    def test_04_noninteger_generation_rejected(self):
        self.sql(f"UPDATE {STATE} SET generation=?", ("not-an-integer",))
        with self.assertRaises(ValueError):
            self.client().read_generation()

    def test_05_missing_state_row_rejected(self):
        self.sql(f"DELETE FROM {STATE}")
        with self.assertRaises(ValueError):
            self.client().read_generation()
        with self.assertRaises(ValueError):
            self.fixture.reopened()

    def test_06_other_signer_cannot_reopen(self):
        with self.assertRaises(ValueError):
            self.fixture.reopened(signer=Ed25519PrivateKey.generate())
        self.assertEqual(self.client().read_generation(), 1)

    def test_07_malformed_fresh_challenge_rejected(self):
        for challenge in (b"", b"x" * 31, b"x" * 33, "x" * 32):
            with self.subTest(challenge=repr(challenge)[:30]):
                with self.assertRaises(ValueError):
                    with self.fixture.backend.hold(challenge=challenge):
                        pass
        self.assertEqual(self.client().read_generation(), 1)

    def test_08_invalid_operation_ids_rejected(self):
        for op in ("", "A" * 32, "g" * 32, "a" * 31, None):
            with self.subTest(op=repr(op)):
                with self.assertRaises(ValueError):
                    self.advance(operation_id=op)
                with self.assertRaises(ValueError):
                    self.lookup(operation_id=op)
        self.assertEqual(self.client().read_generation(), 1)
        self.assertEqual(self.count(), 0)

    def test_09_stale_competing_cas_never_publishes(self):
        self.assertEqual(self.advance(), 2)
        with self.assertRaises(ValueError):
            self.advance(operation_id=OP_B)
        self.assertEqual(self.client(self.fixture.reopened()).read_generation(), 2)
        self.assertEqual(self.lookup(OP_B), ("unknown", 2))
        self.assertEqual(self.count(), 1)

    def test_10_nonmonotonic_cas_never_publishes(self):
        for proposed in (0, 1, 3, -1):
            with self.subTest(proposed=proposed):
                with self.assertRaises(ValueError):
                    self.advance(proposed=proposed)
        self.assertEqual(self.client().read_generation(), 1)
        self.assertEqual(self.count(), 0)

    def test_11_committed_idempotence_survives_reopen(self):
        self.assertEqual(self.advance(), 2)
        self.assertEqual(self.advance(backend=self.fixture.reopened()), 2)
        self.assertEqual(self.lookup(backend=self.fixture.reopened()), ("committed", 2))
        self.assertEqual(self.count(), 1)

    def test_12_operation_id_rebinding_rejected_after_restart(self):
        self.assertEqual(self.advance(), 2)
        with self.assertRaises(ValueError):
            self.advance(expected=2, proposed=3, backend=self.fixture.reopened())
        self.assertEqual(self.client().read_generation(), 2)
        self.assertEqual(self.count(), 1)

    def test_13_corrupt_committed_receipt_rejected(self):
        self.assertEqual(self.advance(), 2)
        try:
            self.sql(
                f"UPDATE {OPERATIONS} SET next_generation=-1 WHERE operation_id=?",
                (OP_A,),
            )
        except sqlite3.IntegrityError:
            self.assertEqual(self.lookup(), ("committed", 2))
            return
        with self.assertRaises(ValueError):
            self.lookup(backend=self.fixture.reopened())

    def test_14_receipt_insert_failure_rolls_back_state(self):
        self.sql(
            f"CREATE TRIGGER reject_generation_receipt BEFORE INSERT ON {OPERATIONS} "
            "BEGIN SELECT RAISE(ABORT, 'injected receipt failure'); END"
        )
        with self.assertRaises(ValueError):
            self.advance()
        self.assertEqual(self.client().read_generation(), 1)
        self.assertEqual(self.count(), 0)
        self.sql("DROP TRIGGER reject_generation_receipt")
        self.assertEqual(self.advance(), 2)

    def test_15_deleted_receipt_is_known_local_limit(self):
        self.assertEqual(self.advance(), 2)
        self.sql(f"DELETE FROM {OPERATIONS} WHERE operation_id=?", (OP_A,))
        self.assertEqual(self.client(self.fixture.reopened()).read_generation(), 2)
        self.assertEqual(self.lookup(backend=self.fixture.reopened()), ("unknown", 2))

    def test_16_concurrent_distinct_cas_single_winner(self):
        def attempt(op):
            try:
                return self.advance(op, backend=self.fixture.reopened())
            except ValueError:
                return None
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(attempt, (OP_A, OP_B, OP_C, OP_D)))
        self.assertEqual(results.count(2), 1)
        self.assertEqual(results.count(None), 3)
        self.assertEqual(self.count(), 1)
        self.assertEqual(self.client().read_generation(), 2)

    def test_17_concurrent_identical_cas_idempotent(self):
        def attempt(_):
            return self.advance(OP_A, backend=self.fixture.reopened())
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(attempt, range(4)))
        self.assertEqual(results, [2] * 4)
        self.assertEqual(self.count(), 1)
        self.assertEqual(self.client().read_generation(), 2)

    def test_18_old_valid_sqlite_image_rollback_known_limit(self):
        old_image = self.fixture.path.parent / "old-generation-image.sqlite3"
        shutil.copy2(self.fixture.path, old_image)
        self.assertEqual(self.advance(), 2)
        self.assertEqual(self.lookup(), ("committed", 2))
        shutil.copy2(old_image, self.fixture.path)
        self.assertEqual(self.client(self.fixture.reopened()).read_generation(), 1)
        self.assertEqual(self.lookup(backend=self.fixture.reopened()), ("unknown", 1))


if __name__ == "__main__":
    unittest.main()
