"""A44 / 66.32B RED: SQLite reference provisioning-generation CAS.

Target production module:
core.existence.history_receipt_trust_checkpoint_protected_provisioning_floor_cas_backend_sqlite_reference

Target class SQLiteReferenceSignedProvisioningGenerationCASAuthority:
 bootstrap(*, path, signer, authority_id, subject_id, initial_generation)
 open(*, path, signer, expected_authority_id, expected_subject_id)

Exposes the signed generation-floor authority protocol:
 hold(*, challenge) -> context manager of (canonical_message, signature)
 advance_if_current(*, operation_id, expected_generation,
                    next_generation, challenge) -> signed pair
 lookup_operation(*, operation_id, challenge) -> signed pair

Required SQLite tables:
 provisioning_generation_state
 provisioning_generation_operations
State and operation receipt must commit atomically in one SQLite transaction.

LIMITATIONS: local SQLite reference only; no actual independent trust,
physical durability, rollback-resistant media, remotely linearizable
service, secure signer provisioning, or cross-store transaction.
"""

import importlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_a44_checkpoint_protected_provisioning_floor_contract as floor_contract

MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_floor_cas_backend_sqlite_reference"
)
TYPE = "SQLiteReferenceSignedProvisioningGenerationCASAuthority"
AUTHORITY_ID = floor_contract.AUTHORITY_ID
SUBJECT_ID = floor_contract.SUBJECT_ID
OP_A = floor_contract.OP_A
OP_B = floor_contract.OP_B
OP_C = "c" * 32
OP_D = "d" * 32


class A44ProvisioningGenerationSQLiteBackendContractTests(unittest.TestCase):
    def setUp(self):
        module = importlib.import_module(MODULE)
        self.backend_type = getattr(module, TYPE)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "provisioning-generation.sqlite3"
        self.signer = Ed25519PrivateKey.generate()
        self.backend = self.backend_type.bootstrap(
            path=self.path,
            signer=self.signer,
            authority_id=AUTHORITY_ID,
            subject_id=SUBJECT_ID,
            initial_generation=1,
        )

    def reopened(self, **changes):
        arguments = dict(
            path=self.path,
            signer=self.signer,
            expected_authority_id=AUTHORITY_ID,
            expected_subject_id=SUBJECT_ID,
        )
        arguments.update(changes)
        return self.backend_type.open(**arguments)

    def client(self, backend=None, **changes):
        if backend is None:
            backend = self.backend
        arguments = dict(
            authority=backend,
            expected_authority_id=AUTHORITY_ID,
            expected_authority_public_key=floor_contract.public_key(self.signer),
            expected_subject_id=SUBJECT_ID,
            minimum_generation=1,
        )
        arguments.update(changes)
        module = importlib.import_module(floor_contract.MODULE)
        return getattr(module, floor_contract.TYPE).from_authority(**arguments)

    def advance(self, backend=None, *, operation_id=OP_A,
                expected_generation=1, next_generation=2):
        return self.client(backend).advance_if_current(
            operation_id=operation_id,
            expected_generation=expected_generation,
            next_generation=next_generation,
        )

    def lookup(self, backend=None, operation_id=OP_A):
        return self.client(backend).lookup_operation(operation_id=operation_id)

    def generation(self, backend=None, minimum_generation=1):
        return self.client(backend, minimum_generation=minimum_generation).read_generation()

    def sql(self, statement, args=()):
        with closing(sqlite3.connect(self.path, timeout=5.0)) as connection:
            with connection:
                connection.execute(statement, args)

    def operation_count(self):
        with closing(sqlite3.connect(self.path, timeout=5.0)) as connection:
            return connection.execute(
                "SELECT COUNT(*) FROM provisioning_generation_operations"
            ).fetchone()[0]

    def test_01_bootstrap_signed_initial_read(self):
        self.assertTrue(self.path.is_file())
        self.assertEqual(self.generation(), 1)

    def test_02_open_recovers_signed_initial_state(self):
        self.assertEqual(self.generation(self.reopened()), 1)
        self.assertEqual(self.lookup(self.reopened()), ("unknown", 1))

    def test_03_committed_cas_survives_restart(self):
        self.assertEqual(self.advance(), 2)
        self.assertEqual(self.generation(self.reopened()), 2)
        self.assertEqual(self.lookup(self.reopened()), ("committed", 2))

    def test_04_sequential_cas_generations_and_receipts(self):
        self.assertEqual(self.advance(), 2)
        self.assertEqual(self.advance(
            operation_id=OP_B, expected_generation=2, next_generation=3
        ), 3)
        self.assertEqual(self.generation(self.reopened()), 3)
        self.assertEqual(self.operation_count(), 2)
        self.assertEqual(self.lookup(self.reopened(), OP_A), ("committed", 3))
        self.assertEqual(self.lookup(self.reopened(), OP_B), ("committed", 3))

    def test_05_idempotent_committed_cas_survives_reopen(self):
        self.assertEqual(self.advance(), 2)
        self.assertEqual(self.advance(self.reopened()), 2)
        self.assertEqual(self.operation_count(), 1)
        self.assertEqual(self.generation(), 2)

    def test_06_operation_id_cannot_rebind_different_request(self):
        self.assertEqual(self.advance(), 2)
        with self.assertRaises(ValueError):
            self.advance(
                self.reopened(), operation_id=OP_A,
                expected_generation=2, next_generation=3,
            )
        self.assertEqual(self.generation(), 2)
        self.assertEqual(self.operation_count(), 1)

    def test_07_competing_stale_cas_does_not_publish(self):
        self.assertEqual(self.advance(), 2)
        with self.assertRaises(ValueError):
            self.advance(self.reopened(), operation_id=OP_B)
        self.assertEqual(self.lookup(operation_id=OP_B), ("unknown", 2))
        self.assertEqual(self.operation_count(), 1)

    def test_08_concurrent_different_operations_single_winner(self):
        def attempt(op):
            try:
                return self.advance(self.reopened(), operation_id=op)
            except ValueError:
                return None
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(attempt, (OP_A, OP_B, OP_C, OP_D)))
        self.assertEqual(results.count(2), 1)
        self.assertEqual(results.count(None), 3)
        self.assertEqual(self.generation(self.reopened()), 2)
        self.assertEqual(self.operation_count(), 1)

    def test_09_concurrent_identical_cas_idempotent(self):
        def attempt(_):
            return self.advance(self.reopened(), operation_id=OP_A)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(attempt, range(4)))
        self.assertEqual(results, [2] * 4)
        self.assertEqual(self.operation_count(), 1)
        self.assertEqual(self.generation(), 2)

    def test_10_lost_ack_after_commit_recovered_by_lookup(self):
        class LostAckProxy:
            def __init__(self, actual):
                self.actual = actual
                self.hold = actual.hold
                self.lookup_operation = actual.lookup_operation
                self.calls = 0
            def advance_if_current(self, **kwargs):
                self.calls += 1
                self.actual.advance_if_current(**kwargs)
                raise TimeoutError("Simulated acknowledgement loss")
        proxy = LostAckProxy(self.backend)
        with self.assertRaises(ValueError):
            self.advance(proxy)
        self.assertEqual(proxy.calls, 1)
        self.assertEqual(self.lookup(self.reopened()), ("committed", 2))
        self.assertEqual(self.operation_count(), 1)

    def test_11_unknown_lookup_nonmutating_after_reopen(self):
        self.assertEqual(self.lookup(self.reopened(), OP_B), ("unknown", 1))
        self.assertEqual(self.operation_count(), 0)
        self.assertEqual(self.generation(), 1)

    def test_12_bootstrap_refuses_existing_database(self):
        with self.assertRaises(ValueError):
            self.backend_type.bootstrap(
                path=self.path, signer=self.signer,
                authority_id=AUTHORITY_ID, subject_id=SUBJECT_ID,
                initial_generation=1,
            )
        self.assertEqual(self.generation(), 1)
        self.assertEqual(self.operation_count(), 0)

    def test_13_open_refuses_missing_database_without_creation(self):
        absent = Path(self.temp.name) / "not-present.sqlite3"
        with self.assertRaises(ValueError):
            self.reopened(path=absent)
        self.assertFalse(absent.exists())

    def test_14_open_refuses_other_signer(self):
        with self.assertRaises(ValueError):
            self.reopened(signer=Ed25519PrivateKey.generate())
        self.assertEqual(self.generation(), 1)

    def test_15_open_refuses_authority_or_subject_substitution(self):
        for name, value in (
            ("expected_authority_id", "impostor-authority"),
            ("expected_subject_id", "impostor-subject"),
        ):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    self.reopened(**{name: value})
        self.assertEqual(self.generation(), 1)

    def test_16_corrupt_stored_state_fails_closed(self):
        self.sql(
            "UPDATE provisioning_generation_state SET generation = -1 "
            "WHERE singleton_id = 1"
        )
        with self.assertRaises(ValueError):
            self.generation()
        with self.assertRaises(ValueError):
            self.reopened()

    def test_17_corrupt_committed_receipt_fails_closed(self):
        self.assertEqual(self.advance(), 2)
        self.sql(
            "UPDATE provisioning_generation_operations "
            "SET committed_generation = -1 WHERE operation_id = ?",
            (OP_A,),
        )
        with self.assertRaises(ValueError):
            self.lookup(self.reopened())
        self.assertEqual(self.generation(), 2)

    def test_18_operation_insert_failure_rolls_back_state(self):
        self.sql(
            "CREATE TRIGGER fail_receipt_insert "
            "BEFORE INSERT ON provisioning_generation_operations "
            "BEGIN SELECT RAISE(ABORT, 'injected failure'); END"
        )
        with self.assertRaises(ValueError):
            self.advance()
        self.assertEqual(self.generation(self.reopened()), 1)
        self.assertEqual(self.lookup(), ("unknown", 1))
        self.sql("DROP TRIGGER fail_receipt_insert")
        self.assertEqual(self.advance(self.reopened()), 2)
        self.assertEqual(self.operation_count(), 1)

    def test_19_old_valid_database_image_rollback_known_limit(self):
        previous = Path(self.temp.name) / "older-valid.sqlite3"
        shutil.copy2(self.path, previous)
        self.assertEqual(self.advance(), 2)
        shutil.copy2(previous, self.path)
        rolled_back = self.reopened()
        self.assertEqual(self.generation(rolled_back), 1)
        self.assertEqual(self.lookup(rolled_back), ("unknown", 1))
        with self.assertRaises(ValueError):
            self.generation(rolled_back, minimum_generation=2)

    def test_20_signed_provisioning_bootstrap_after_restart(self):
        fixture = floor_contract.A44ProtectedProvisioningFloorContractTests(
            "test_01_signed_initial_generation"
        )
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        client = self.client(self.reopened())
        old = client.bind_provisioning(
            source=fixture.fixture.source,
            manifest=fixture.fixture.manifest,
            signature=fixture.fixture.signature,
        )
        self.assertEqual(old.pins.provisioning_generation, 1)
        self.assertEqual(self.advance(), 2)
        client = self.client(self.reopened(), minimum_generation=2)
        with self.assertRaises(ValueError):
            client.bind_provisioning(
                source=fixture.fixture.source,
                manifest=fixture.fixture.manifest,
                signature=fixture.fixture.signature,
            )
        manifest, signature = fixture.update_source()
        newer = client.bind_provisioning(
            source=fixture.fixture.source,
            manifest=manifest,
            signature=signature,
        )
        self.assertEqual(newer.pins.provisioning_generation, 2)


if __name__ == "__main__":
    unittest.main()
