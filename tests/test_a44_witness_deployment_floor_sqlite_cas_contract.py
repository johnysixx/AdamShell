"""A44 / 66.35B RED: SQLite reference monotonic witness deployment floor CAS.

Production target:
core.existence.history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_cas_backend_sqlite_reference

SQLiteReferenceSignedWitnessDeploymentFloorCASAuthority:
 bootstrap(*, path, signer, floor_id, subject_id, authority_id,
           authority_public_key, witness_id, witness_public_key,
           initial_minimum_generation, initial_epoch)
 open(*, path, signer, expected_floor_id, expected_subject_id,
        expected_authority_id, expected_authority_public_key,
        expected_witness_id, expected_witness_public_key)
 hold(*, challenge) -> context manager of (message, signature)
 advance_if_current(*, operation_id, expected_epoch, next_epoch,
                    expected_minimum_generation, next_minimum_generation,
                    challenge) -> (signed CAS message, signature)
 lookup_operation(*, operation_id, challenge) -> (signed lookup, signature)

Database tables: witness_deployment_floor_state and
witness_deployment_floor_operations. State and operation receipt must be
committed in ONE local SQLite transaction, no blind retry after lost ack.

LOCAL REFERENCE ONLY. An old valid DB image can roll back receipts and floors;
no independently durable monotonic root, isolated key custody, physical
power-loss guarantee, remote linearizability or cross-store atomicity is proven.
"""

import importlib
import json
import shutil
import sqlite3
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_a44_witness_deployment_floor_contract as deployment_contract

MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_cas_backend_sqlite_reference"
)
CLASS = "SQLiteReferenceSignedWitnessDeploymentFloorCASAuthority"
FLOOR_ID = deployment_contract.FLOOR_ID
SUBJECT_ID = deployment_contract.SUBJECT_ID
DOMAIN = deployment_contract.DOMAIN
OP_A, OP_B, OP_C, OP_D = (letter * 32 for letter in "abcd")
_READ_FIELDS = frozenset({
    "domain", "version", "operation", "floor_id", "subject_id",
    "authority_id", "authority_public_key_hex", "witness_id",
    "witness_public_key_hex", "minimum_generation", "epoch", "challenge_hex",
})
_CAS_FIELDS = _READ_FIELDS | frozenset({
    "operation_id", "expected_epoch", "next_epoch",
    "expected_minimum_generation", "next_minimum_generation", "status",
})
_LOOKUP_FIELDS = _READ_FIELDS | frozenset({"operation_id", "status"})


def canonical(document):
    return json.dumps(
        document, sort_keys=True, ensure_ascii=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("ascii")


def public_key(signer):
    return signer.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


class A44WitnessDeploymentFloorSQLiteCASContractTests(unittest.TestCase):
    def setUp(self):
        module = importlib.import_module(MODULE)
        self.backend_type = getattr(module, CLASS)
        self.deployment = deployment_contract.A44WitnessDeploymentFloorContractTests(
            "test_01_matching_signed_floor_and_dual_read"
        )
        self.deployment.setUp()
        self.addCleanup(self.deployment.doCleanups)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "deployment-floor.sqlite3"
        self.signer = Ed25519PrivateKey.generate()
        self.guard = self.deployment.guard
        self.authority_id = self.guard.client.expected_authority_id
        self.authority_key = self.guard.client.expected_authority_public_key
        self.witness_id = self.guard.expected_witness_id
        self.witness_key = self.guard.expected_witness_public_key
        self.backend = self.backend_type.bootstrap(
            path=self.path, signer=self.signer,
            floor_id=FLOOR_ID, subject_id=SUBJECT_ID,
            authority_id=self.authority_id,
            authority_public_key=self.authority_key,
            witness_id=self.witness_id, witness_public_key=self.witness_key,
            initial_minimum_generation=1, initial_epoch=1,
        )

    def reopened(self, **changes):
        arguments = dict(
            path=self.path, signer=self.signer,
            expected_floor_id=FLOOR_ID,
            expected_subject_id=SUBJECT_ID,
            expected_authority_id=self.authority_id,
            expected_authority_public_key=self.authority_key,
            expected_witness_id=self.witness_id,
            expected_witness_public_key=self.witness_key,
        )
        arguments.update(changes)
        return self.backend_type.open(**arguments)

    def signed(self, response, *, operation, challenge):
        self.assertIs(type(response), tuple)
        self.assertEqual(len(response), 2)
        message, signature = response
        self.assertIs(type(message), bytes)
        self.assertIs(type(signature), bytes)
        self.assertEqual(len(signature), 64)
        self.signer.public_key().verify(signature, message)
        doc = json.loads(message.decode("ascii"))
        self.assertEqual(message, canonical(doc))
        fields = {"read": _READ_FIELDS, "cas": _CAS_FIELDS,
                  "lookup": _LOOKUP_FIELDS}[operation]
        self.assertEqual(set(doc), fields)
        self.assertEqual(doc["domain"], DOMAIN)
        self.assertEqual(doc["version"], 1)
        self.assertEqual(doc["operation"], operation)
        self.assertEqual(doc["floor_id"], FLOOR_ID)
        self.assertEqual(doc["subject_id"], SUBJECT_ID)
        self.assertEqual(doc["authority_id"], self.authority_id)
        self.assertEqual(doc["authority_public_key_hex"], self.authority_key.hex())
        self.assertEqual(doc["witness_id"], self.witness_id)
        self.assertEqual(doc["witness_public_key_hex"], self.witness_key.hex())
        self.assertEqual(doc["challenge_hex"], challenge.hex())
        self.assertIs(type(doc["minimum_generation"]), int)
        self.assertIs(type(doc["epoch"]), int)
        return doc

    def read(self, backend=None):
        if backend is None:
            backend = self.backend
        challenge = b"r" * 32
        with backend.hold(challenge=challenge) as response:
            return self.signed(response, operation="read", challenge=challenge)

    def cas(self, backend=None, *, operation_id=OP_A,
            expected_epoch=1, next_epoch=2,
            expected_minimum_generation=1, next_minimum_generation=2):
        if backend is None:
            backend = self.backend
        challenge = b"c" * 32
        pair = backend.advance_if_current(
            operation_id=operation_id,
            expected_epoch=expected_epoch, next_epoch=next_epoch,
            expected_minimum_generation=expected_minimum_generation,
            next_minimum_generation=next_minimum_generation,
            challenge=challenge,
        )
        doc = self.signed(pair, operation="cas", challenge=challenge)
        self.assertEqual(doc["operation_id"], operation_id)
        self.assertEqual(doc["expected_epoch"], expected_epoch)
        self.assertEqual(doc["next_epoch"], next_epoch)
        self.assertEqual(doc["expected_minimum_generation"], expected_minimum_generation)
        self.assertEqual(doc["next_minimum_generation"], next_minimum_generation)
        self.assertIn(doc["status"], ("committed", "rejected"))
        return doc

    def lookup(self, backend=None, operation_id=OP_A):
        if backend is None:
            backend = self.backend
        challenge = b"l" * 32
        doc = self.signed(
            backend.lookup_operation(operation_id=operation_id, challenge=challenge),
            operation="lookup", challenge=challenge,
        )
        self.assertEqual(doc["operation_id"], operation_id)
        self.assertIn(doc["status"], ("committed", "unknown"))
        return doc

    def operation_count(self):
        with closing(sqlite3.connect(self.path, timeout=5.0)) as connection:
            return connection.execute(
                "SELECT COUNT(*) FROM witness_deployment_floor_operations"
            ).fetchone()[0]

    def sql(self, statement, args=()):
        with closing(sqlite3.connect(self.path, timeout=5.0)) as connection:
            with connection:
                connection.execute(statement, args)

    def gate(self, backend=None, minimum_epoch=1):
        return self.deployment.gate(
            floor_source=self.backend if backend is None else backend,
            expected_floor_public_key=public_key(self.signer),
            minimum_epoch=minimum_epoch,
        )

    def test_01_bootstrap_signed_initial_read(self):
        self.assertTrue(self.path.is_file())
        self.assertEqual((self.read()["minimum_generation"], self.read()["epoch"]), (1, 1))
        self.assertEqual(self.operation_count(), 0)

    def test_02_existing_three_layer_gate_accepts_sqlite_provider(self):
        self.assertEqual(self.gate().read_generation(), 1)
        self.assertEqual(self.gate(self.reopened()).read_generation(), 1)

    def test_03_open_preserves_initial_floor_and_unknown_lookup(self):
        self.assertEqual(self.read(self.reopened())["epoch"], 1)
        self.assertEqual(self.lookup(self.reopened())["status"], "unknown")
        self.assertEqual(self.operation_count(), 0)

    def test_04_signed_cas_persists_floor_epoch_and_receipt(self):
        doc = self.cas()
        self.assertEqual((doc["status"], doc["epoch"], doc["minimum_generation"]),
                         ("committed", 2, 2))
        saved = self.read(self.reopened())
        self.assertEqual((saved["epoch"], saved["minimum_generation"]), (2, 2))
        self.assertEqual(self.lookup(self.reopened())["status"], "committed")
        self.assertEqual(self.operation_count(), 1)

    def test_05_gate_accepts_published_floor_after_dual_advance(self):
        self.deployment.advance_both()
        self.assertEqual(self.cas()["status"], "committed")
        self.assertEqual(self.gate(self.reopened(), minimum_epoch=2).read_generation(), 2)

    def test_06_advanced_floor_rejects_older_dual_generation(self):
        self.assertEqual(self.cas()["status"], "committed")
        with self.assertRaises(ValueError):
            self.gate().read_generation()
        self.deployment.advance_both()
        self.assertEqual(self.gate().read_generation(), 2)

    def test_07_stale_cas_rejected_without_receipt_or_change(self):
        self.assertEqual(self.cas()["status"], "committed")
        self.assertEqual(self.cas(operation_id=OP_B)["status"], "rejected")
        self.assertEqual(self.read()["epoch"], 2)
        self.assertEqual(self.operation_count(), 1)
        self.assertEqual(self.lookup(operation_id=OP_B)["status"], "unknown")

    def test_08_nonmonotonic_cas_parameters_rejected(self):
        for change in (
            dict(next_epoch=1),
            dict(next_epoch=3),
            dict(next_minimum_generation=0),
            dict(expected_epoch=True),
            dict(next_minimum_generation="2"),
        ):
            with self.subTest(change=change):
                parameters = dict(
                    operation_id=OP_A, expected_epoch=1, next_epoch=2,
                    expected_minimum_generation=1, next_minimum_generation=2,
                    challenge=b"c" * 32,
                )
                parameters.update(change)
                with self.assertRaises(ValueError):
                    self.backend.advance_if_current(**parameters)
        self.assertEqual(self.read()["epoch"], 1)
        self.assertEqual(self.operation_count(), 0)

    def test_09_idempotent_operation_replayed_after_reopen(self):
        self.assertEqual(self.cas()["status"], "committed")
        self.assertEqual(self.cas(self.reopened())["status"], "committed")
        self.assertEqual(self.operation_count(), 1)
        self.assertEqual(self.read()["epoch"], 2)

    def test_10_operation_id_cannot_rebind_different_cas(self):
        self.assertEqual(self.cas()["status"], "committed")
        with self.assertRaises(ValueError):
            self.cas(self.reopened(), expected_epoch=2, next_epoch=3,
                     expected_minimum_generation=2, next_minimum_generation=3)
        self.assertEqual(self.read()["epoch"], 2)
        self.assertEqual(self.operation_count(), 1)

    def test_11_concurrent_distinct_operations_one_winner(self):
        def attempt(operation):
            return self.cas(self.reopened(), operation_id=operation)["status"]
        with ThreadPoolExecutor(max_workers=4) as pool:
            answers = list(pool.map(attempt, (OP_A, OP_B, OP_C, OP_D)))
        self.assertEqual(answers.count("committed"), 1)
        self.assertEqual(answers.count("rejected"), 3)
        self.assertEqual(self.read()["epoch"], 2)
        self.assertEqual(self.operation_count(), 1)

    def test_12_concurrent_same_operation_idempotent(self):
        def attempt(_):
            return self.cas(self.reopened())["status"]
        with ThreadPoolExecutor(max_workers=4) as pool:
            answers = list(pool.map(attempt, range(4)))
        self.assertEqual(answers, ["committed"] * 4)
        self.assertEqual(self.operation_count(), 1)
        self.assertEqual(self.read()["epoch"], 2)

    def test_13_lost_ack_recovered_by_original_operation_lookup(self):
        challenge = b"c" * 32
        def lose_ack_after_commit():
            self.backend.advance_if_current(
                operation_id=OP_A, expected_epoch=1, next_epoch=2,
                expected_minimum_generation=1, next_minimum_generation=2,
                challenge=challenge,
            )
            raise TimeoutError("Simulated lost acknowledgement after commit")

        with self.assertRaises(TimeoutError):
            lose_ack_after_commit()
        # Ambiguous outcome: inspect the ORIGINAL operation ID, never blind retry.
        self.assertEqual(self.lookup(self.reopened(), OP_A)["status"], "committed")
        self.assertEqual(self.operation_count(), 1)
        self.assertEqual(self.read()["epoch"], 2)

    def test_14_unknown_lookup_is_nonmutating(self):
        self.assertEqual(self.lookup(self.reopened(), OP_B)["status"], "unknown")
        self.assertEqual(self.read()["epoch"], 1)
        self.assertEqual(self.operation_count(), 0)

    def test_15_bootstrap_refuses_existing_and_open_refuses_missing(self):
        with self.assertRaises(ValueError):
            self.backend_type.bootstrap(
                path=self.path, signer=self.signer, floor_id=FLOOR_ID,
                subject_id=SUBJECT_ID, authority_id=self.authority_id,
                authority_public_key=self.authority_key,
                witness_id=self.witness_id, witness_public_key=self.witness_key,
                initial_minimum_generation=1, initial_epoch=1,
            )
        missing = Path(self.temp.name) / "missing-floor.sqlite3"
        with self.assertRaises(ValueError):
            self.reopened(path=missing)
        self.assertFalse(missing.exists())
        self.assertEqual(self.read()["epoch"], 1)

    def test_16_open_rejects_signer_ids_and_pinned_key_substitution(self):
        changes = (
            {"signer": Ed25519PrivateKey.generate()},
            {"expected_floor_id": "other-floor"},
            {"expected_subject_id": "other-subject"},
            {"expected_authority_id": "other-authority"},
            {"expected_witness_id": "other-witness"},
            {"expected_authority_public_key": b"x" * 32},
            {"expected_witness_public_key": b"x" * 32},
        )
        for change in changes:
            with self.subTest(change=list(change)):
                with self.assertRaises(ValueError):
                    self.reopened(**change)
        self.assertEqual(self.read()["epoch"], 1)

    def test_17_receipt_insert_failure_rolls_back_state(self):
        self.sql(
            "CREATE TRIGGER block_receipt BEFORE INSERT ON "
            "witness_deployment_floor_operations "
            "BEGIN SELECT RAISE(ABORT, 'injected receipt failure'); END"
        )
        with self.assertRaises(ValueError):
            self.cas()
        self.assertEqual((self.read()["epoch"], self.read()["minimum_generation"]), (1, 1))
        self.assertEqual(self.lookup()["status"], "unknown")
        self.sql("DROP TRIGGER block_receipt")
        self.assertEqual(self.cas(self.reopened())["status"], "committed")
        self.assertEqual(self.operation_count(), 1)

    def test_18_corrupt_stored_floor_rejected(self):
        self.sql("UPDATE witness_deployment_floor_state SET epoch = -1 WHERE singleton_id = 1")
        with self.assertRaises(ValueError):
            self.read()
        with self.assertRaises(ValueError):
            self.reopened()

    def test_19_corrupt_receipt_rejected_without_read_state_loss(self):
        self.assertEqual(self.cas()["status"], "committed")
        self.sql(
            "UPDATE witness_deployment_floor_operations SET committed_epoch = -1 "
            "WHERE operation_id = ?", (OP_A,),
        )
        with self.assertRaises(ValueError):
            self.lookup(self.reopened())
        self.assertEqual(self.read()["epoch"], 2)

    def test_20_old_valid_db_rollback_known_limit_with_epoch_pin(self):
        old = Path(self.temp.name) / "older-valid-floor.sqlite3"
        shutil.copy2(self.path, old)
        self.assertEqual(self.cas()["status"], "committed")
        self.deployment.advance_both()
        self.assertEqual(self.gate(minimum_epoch=2).read_generation(), 2)
        shutil.copy2(old, self.path)
        rolled_back = self.reopened()
        self.assertEqual(self.read(rolled_back)["epoch"], 1)
        self.assertEqual(self.lookup(rolled_back)["status"], "unknown")
        # Signed but old floor read is accepted when caller's epoch pin was
        # also rolled back. Only an independently retained epoch rejects it.
        self.assertEqual(self.gate(rolled_back, minimum_epoch=1).read_generation(), 2)
        with self.assertRaises(ValueError):
            self.gate(rolled_back, minimum_epoch=2).read_generation()


if __name__ == "__main__":
    unittest.main()
