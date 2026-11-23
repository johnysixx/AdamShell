"""A44 / 66.35D: adversarial tests for local SQLite deployment-floor CAS.

Reference-only storage; does NOT prove independent monotonic trust, secure key
custody, physical power-loss survival, or cross-store atomicity.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_a44_witness_deployment_floor_sqlite_cas_contract as floor_contract


class A44WitnessDeploymentFloorSQLiteCASAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.fixture = floor_contract.A44WitnessDeploymentFloorSQLiteCASContractTests(
            "test_01_bootstrap_signed_initial_read"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def test_01_reject_malformed_challenges_without_writes(self):
        for challenge in (None, "c" * 32, b"c" * 31, b"c" * 33, bytearray(b"c" * 32), True):
            with self.subTest(challenge=repr(challenge)):
                with self.assertRaises(ValueError):
                    with self.fixture.backend.hold(challenge=challenge):
                        pass
                with self.assertRaises(ValueError):
                    self.fixture.backend.advance_if_current(
                        operation_id=floor_contract.OP_A,
                        expected_epoch=1, next_epoch=2,
                        expected_minimum_generation=1, next_minimum_generation=2,
                        challenge=challenge,
                    )
                with self.assertRaises(ValueError):
                    self.fixture.backend.lookup_operation(
                        operation_id=floor_contract.OP_A, challenge=challenge
                    )
        self.assertEqual(self.fixture.read()["epoch"], 1)
        self.assertEqual(self.fixture.operation_count(), 0)

    def test_02_reject_malformed_operation_ids_without_writes(self):
        for op in (None, "", "bad", 12, b"a" * 32, "a" * 31):
            with self.subTest(operation_id=repr(op)):
                with self.assertRaises(ValueError):
                    self.fixture.backend.advance_if_current(
                        operation_id=op,
                        expected_epoch=1, next_epoch=2,
                        expected_minimum_generation=1, next_minimum_generation=2,
                        challenge=b"c" * 32,
                    )
                with self.assertRaises(ValueError):
                    self.fixture.backend.lookup_operation(
                        operation_id=op, challenge=b"l" * 32,
                    )
        self.assertEqual(self.fixture.operation_count(), 0)

    def test_03_reject_invalid_cas_counter_types(self):
        changes = (
            {"expected_epoch": True}, {"next_epoch": False},
            {"expected_minimum_generation": -1},
            {"next_minimum_generation": -1},
            {"expected_epoch": "1"}, {"next_epoch": None},
            {"next_epoch": 1 << 100},
            {"next_minimum_generation": 1 << 100},
        )
        for change in changes:
            with self.subTest(change=change):
                arguments = dict(
                    operation_id=floor_contract.OP_A,
                    expected_epoch=1, next_epoch=2,
                    expected_minimum_generation=1, next_minimum_generation=2,
                    challenge=b"c" * 32,
                )
                arguments.update(change)
                with self.assertRaises(ValueError):
                    self.fixture.backend.advance_if_current(**arguments)
        self.assertEqual(self.fixture.read()["epoch"], 1)
        self.assertEqual(self.fixture.operation_count(), 0)

    def test_04_reject_decreasing_minimum_or_skipping_epoch(self):
        for next_epoch, next_minimum in ((1, 2), (3, 2), (2, 0)):
            with self.subTest(next_epoch=next_epoch, minimum=next_minimum):
                with self.assertRaises(ValueError):
                    self.fixture.backend.advance_if_current(
                        operation_id=floor_contract.OP_A,
                        expected_epoch=1, next_epoch=next_epoch,
                        expected_minimum_generation=1,
                        next_minimum_generation=next_minimum,
                        challenge=b"c" * 32,
                    )
        self.assertEqual(self.fixture.read()["epoch"], 1)
        self.assertEqual(self.fixture.operation_count(), 0)

    def test_05_reject_bootstrap_with_shared_signing_key_before_creating_file(self):
        for field in ("authority_public_key", "witness_public_key"):
            with self.subTest(field=field):
                path = Path(self.fixture.temp.name) / (field + "-unsafe.sqlite3")
                arguments = dict(
                    path=path, signer=self.fixture.signer,
                    floor_id=floor_contract.FLOOR_ID,
                    subject_id=floor_contract.SUBJECT_ID,
                    authority_id=self.fixture.authority_id,
                    authority_public_key=self.fixture.authority_key,
                    witness_id=self.fixture.witness_id,
                    witness_public_key=self.fixture.witness_key,
                    initial_minimum_generation=1, initial_epoch=1,
                )
                arguments[field] = floor_contract.public_key(self.fixture.signer)
                with self.assertRaises(ValueError):
                    self.fixture.backend_type.bootstrap(**arguments)
                self.assertFalse(path.exists())

    def test_06_reject_stored_identity_substitution(self):
        cases = (
            ("floor_id", "forged-floor", floor_contract.FLOOR_ID),
            ("subject_id", "forged-subject", floor_contract.SUBJECT_ID),
            ("authority_id", "forged-authority", self.fixture.authority_id),
            ("witness_id", "forged-witness", self.fixture.witness_id),
        )
        for field, forged, trusted in cases:
            with self.subTest(field=field):
                self.fixture.sql(
                    "UPDATE witness_deployment_floor_state SET " + field + " = ? WHERE singleton_id = 1",
                    (forged,),
                )
                with self.assertRaises(ValueError):
                    self.fixture.read()
                with self.assertRaises(ValueError):
                    self.fixture.reopened()
                self.fixture.sql(
                    "UPDATE witness_deployment_floor_state SET " + field + " = ? WHERE singleton_id = 1",
                    (trusted,),
                )
        self.assertEqual(self.fixture.read()["epoch"], 1)

    def test_07_reject_stored_public_key_substitution(self):
        cases = (
            ("signer_public_key", floor_contract.public_key(self.fixture.signer)),
            ("authority_public_key", self.fixture.authority_key),
            ("witness_public_key", self.fixture.witness_key),
        )
        for field, trusted in cases:
            with self.subTest(field=field):
                self.fixture.sql(
                    "UPDATE witness_deployment_floor_state SET " + field + " = ? WHERE singleton_id = 1",
                    (b"x" * 32,),
                )
                with self.assertRaises(ValueError):
                    self.fixture.read()
                with self.assertRaises(ValueError):
                    self.fixture.reopened()
                self.fixture.sql(
                    "UPDATE witness_deployment_floor_state SET " + field + " = ? WHERE singleton_id = 1",
                    (trusted,),
                )
        self.assertEqual(self.fixture.read()["epoch"], 1)

    def test_08_reject_runtime_mutation_of_frozen_provider_ids(self):
        for field in ("floor_id", "subject_id", "authority_id", "witness_id"):
            with self.subTest(field=field):
                current = getattr(self.fixture.backend, field)
                object.__setattr__(self.fixture.backend, field, "forged-runtime-identity")
                try:
                    with self.assertRaises(ValueError):
                        self.fixture.read()
                finally:
                    object.__setattr__(self.fixture.backend, field, current)
        self.assertEqual(self.fixture.read()["epoch"], 1)

    def test_09_reject_runtime_mutation_of_frozen_signer(self):
        original = self.fixture.backend.signer
        object.__setattr__(self.fixture.backend, "signer", Ed25519PrivateKey.generate())
        try:
            with self.assertRaises(ValueError):
                self.fixture.read()
            with self.assertRaises(ValueError):
                self.fixture.cas()
        finally:
            object.__setattr__(self.fixture.backend, "signer", original)
        self.assertEqual(self.fixture.read()["epoch"], 1)
        self.assertEqual(self.fixture.operation_count(), 0)

    def test_10_refuse_corrupt_database_image_without_rebootstrap(self):
        path = Path(self.fixture.temp.name) / "corrupt-image.sqlite3"
        path.write_bytes(b"definitely-not-a-valid-sqlite-database")
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            self.fixture.reopened(path=path)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.fixture.read()["epoch"], 1)

    def test_11_missing_database_refused_without_creation(self):
        path = Path(self.fixture.temp.name) / "not-created.sqlite3"
        with self.assertRaises(ValueError):
            self.fixture.reopened(path=path)
        self.assertFalse(path.exists())
        self.assertEqual(self.fixture.operation_count(), 0)

    def test_12_missing_singleton_fails_closed_without_rebootstrap(self):
        self.fixture.sql("DELETE FROM witness_deployment_floor_state WHERE singleton_id = 1")
        with self.assertRaises(ValueError):
            self.fixture.read()
        with self.assertRaises(ValueError):
            self.fixture.reopened()
        with self.assertRaises(ValueError):
            self.fixture.cas()
        self.assertEqual(self.fixture.operation_count(), 0)

    def test_13_corrupted_receipt_epoch_blocks_lookup_and_repeat(self):
        self.assertEqual(self.fixture.cas()["status"], "committed")
        self.fixture.sql(
            "UPDATE witness_deployment_floor_operations SET next_epoch = 7 "
            "WHERE operation_id = ?", (floor_contract.OP_A,),
        )
        with self.assertRaises(ValueError):
            self.fixture.lookup(self.fixture.reopened())
        with self.assertRaises(ValueError):
            self.fixture.cas(self.fixture.reopened())
        self.assertEqual(self.fixture.read()["epoch"], 2)
        self.assertEqual(self.fixture.operation_count(), 1)

    def test_14_corrupted_receipt_minimum_blocks_lookup(self):
        self.assertEqual(self.fixture.cas()["status"], "committed")
        self.fixture.sql(
            "UPDATE witness_deployment_floor_operations "
            "SET committed_minimum_generation = 999 WHERE operation_id = ?",
            (floor_contract.OP_A,),
        )
        with self.assertRaises(ValueError):
            self.fixture.lookup()
        self.assertEqual(self.fixture.read()["minimum_generation"], 2)
        self.assertEqual(self.fixture.operation_count(), 1)

    def test_15_state_update_failure_publishes_no_receipt(self):
        self.fixture.sql(
            "CREATE TRIGGER block_floor_update BEFORE UPDATE ON "
            "witness_deployment_floor_state "
            "BEGIN SELECT RAISE(ABORT, 'injected state failure'); END"
        )
        with self.assertRaises(ValueError):
            self.fixture.cas()
        self.assertEqual((self.fixture.read()["epoch"], self.fixture.read()["minimum_generation"]), (1, 1))
        self.assertEqual(self.fixture.lookup()["status"], "unknown")
        self.assertEqual(self.fixture.operation_count(), 0)
        self.fixture.sql("DROP TRIGGER block_floor_update")
        self.assertEqual(self.fixture.cas(self.fixture.reopened())["status"], "committed")

    def test_16_after_receipt_insert_failure_rolls_back_state_and_receipt(self):
        self.fixture.sql(
            "CREATE TRIGGER block_floor_receipt AFTER INSERT ON "
            "witness_deployment_floor_operations "
            "BEGIN SELECT RAISE(ABORT, 'injected after-insert failure'); END"
        )
        with self.assertRaises(ValueError):
            self.fixture.cas()
        self.assertEqual(self.fixture.read()["epoch"], 1)
        self.assertEqual(self.fixture.read()["minimum_generation"], 1)
        self.assertEqual(self.fixture.lookup()["status"], "unknown")
        self.assertEqual(self.fixture.operation_count(), 0)
        self.fixture.sql("DROP TRIGGER block_floor_receipt")
        self.assertEqual(self.fixture.cas(self.fixture.reopened())["status"], "committed")
        self.assertEqual(self.fixture.operation_count(), 1)

    def test_17_signing_failure_after_commit_is_ambiguous_and_lookup_recovers(self):
        provider_type = type(self.fixture.backend)
        with patch.object(provider_type, "_signed", side_effect=RuntimeError("injected post-commit signing failure")):
            with self.assertRaises(ValueError):
                self.fixture.cas()
        self.assertEqual(self.fixture.read()["epoch"], 2)
        self.assertEqual(self.fixture.lookup(self.fixture.reopened())["status"], "committed")
        self.assertEqual(self.fixture.operation_count(), 1)
        # A client must never blindly replay an ambiguous CAS with a new ID.

    def test_18_floor_ahead_of_dual_generation_fails_closed_until_consistent(self):
        self.assertEqual(self.fixture.cas()["status"], "committed")
        with self.assertRaises(ValueError):
            self.fixture.gate(self.fixture.reopened(), minimum_epoch=2).read_generation()
        self.assertEqual(self.fixture.operation_count(), 1)
        self.fixture.deployment.advance_both()
        self.assertEqual(self.fixture.gate(self.fixture.reopened(), minimum_epoch=2).read_generation(), 2)
        self.assertEqual(self.fixture.operation_count(), 1)


if __name__ == "__main__":
    unittest.main()
