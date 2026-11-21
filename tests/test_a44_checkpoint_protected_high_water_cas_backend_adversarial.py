"""A44 / 66.29D SQLite high-water CAS adversarial regression.

Validates fail-closed behavior against malformed SQLite state,
signed identity substitution, corrupted operation receipts,
CAS conflicts, transaction failures and ambiguous acknowledgements.

EXPLICIT LIMITS:
- The backend is a local SQLite reference implementation.
- A valid old database can replace the current database.
- Operation records have no external tamper-evident protection.
- Local concurrency does not prove remote linearizability.
- No secure provisioning or protected signing key is provided.
- No physical power-loss guarantee or cross-store atomicity.
"""

import shutil
import sqlite3
import sys
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_protected_high_water_cas_backend_contract as contract


class A44ProtectedHighWaterCASBackendAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44ProtectedHighWaterCASBackendContractTests(
                "test_01_bootstrap_produces_verified_signed_read"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def sql(self, statement, parameters=()):
        with closing(
            sqlite3.connect(
                self.fixture.path,
                timeout=5.0,
            )
        ) as connection:
            with connection:
                connection.execute(
                    statement,
                    parameters,
                )

    def update_state(self, column, value):
        allowed = {
            "store_id",
            "store_public_key",
            "anchor_id",
            "anchor_public_key",
            "authority_id",
            "authority_public_key",
            "root_id",
            "root_public_key",
            "enrollment_epoch",
            "revision",
            "generation",
            "fence_token",
        }

        if column not in allowed:
            raise ValueError(
                "Unsupported test state column."
            )

        self.sql(
            f"UPDATE protected_high_water_state "
            f"SET {column} = ? WHERE singleton_id = 1",
            (value,),
        )

    def test_01_attacker_signing_key_cannot_reopen_store(self):
        attacker = Ed25519PrivateKey.generate()

        with self.assertRaises(ValueError):
            self.fixture.reopened(
                signer=attacker,
            )

        self.assertEqual(
            self.fixture.read(),
            self.fixture.initial,
        )

    def test_02_stored_store_identity_or_key_tamper_rejected(self):
        cases = (
            (
                "store_id",
                "attacker-high-water",
                contract.STORE_ID,
            ),
            (
                "store_public_key",
                b"\x99" * 32,
                self.fixture.signer_key,
            ),
        )

        for column, bad, original in cases:
            with self.subTest(column=column):
                self.update_state(column, bad)

                try:
                    with self.assertRaises(ValueError):
                        self.fixture.read()

                    with self.assertRaises(ValueError):
                        self.fixture.reopened()

                finally:
                    self.update_state(
                        column,
                        original,
                    )

        self.assertEqual(
            self.fixture.read(),
            self.fixture.initial,
        )

    def test_03_enrollment_identity_and_key_tamper_rejected(self):
        enrollment = self.fixture.enrollment

        cases = (
            (
                "anchor_id",
                "forged-anchor",
                enrollment.expected_anchor_id,
            ),
            (
                "anchor_public_key",
                b"\x91" * 32,
                enrollment.expected_anchor_public_key,
            ),
            (
                "authority_id",
                "forged-authority",
                enrollment.expected_authority_id,
            ),
            (
                "authority_public_key",
                b"\x92" * 32,
                enrollment.expected_authority_public_key,
            ),
            (
                "root_id",
                "forged-root",
                enrollment.expected_root_id,
            ),
            (
                "root_public_key",
                b"\x93" * 32,
                enrollment.expected_root_public_key,
            ),
            (
                "enrollment_epoch",
                enrollment.expected_enrollment_epoch + 1,
                enrollment.expected_enrollment_epoch,
            ),
        )

        for column, bad, original in cases:
            with self.subTest(column=column):
                self.update_state(column, bad)

                try:
                    with self.assertRaises(ValueError):
                        self.fixture.read()

                    with self.assertRaises(ValueError):
                        self.fixture.reopened()

                finally:
                    self.update_state(
                        column,
                        original,
                    )

        self.assertEqual(
            self.fixture.read(),
            self.fixture.initial,
        )

    def test_04_missing_persisted_singleton_fails_closed(self):
        self.sql(
            "DELETE FROM protected_high_water_state "
            "WHERE singleton_id = 1"
        )

        with self.assertRaises(ValueError):
            self.fixture.read()

        with self.assertRaises(ValueError):
            self.fixture.reopened()

        with self.assertRaises(ValueError):
            self.fixture.lookup()

        self.assertTrue(
            self.fixture.path.exists()
        )

    def test_05_negative_stored_counters_fail_closed(self):
        cases = (
            ("revision", 10),
            ("generation", 20),
            ("fence_token", 30),
        )

        for column, original in cases:
            with self.subTest(column=column):
                self.update_state(column, -1)

                try:
                    with self.assertRaises(ValueError):
                        self.fixture.read()

                    with self.assertRaises(ValueError):
                        self.fixture.reopened()

                finally:
                    self.update_state(
                        column,
                        original,
                    )

        self.assertEqual(
            self.fixture.read(),
            self.fixture.initial,
        )

    def test_06_higher_enrollment_floor_blocks_old_store(self):
        higher = self.fixture.enrollment.raise_floor(
            minimum_revision=11,
            minimum_generation=21,
            minimum_fence_token=31,
        )

        with self.assertRaises(ValueError):
            self.fixture.reopened(
                enrollment=higher,
            )

        with self.assertRaises(ValueError):
            self.fixture.read(
                minimum_revision=11,
                minimum_generation=21,
                minimum_fence_token=31,
            )

        self.assertEqual(
            self.fixture.advance(),
            self.fixture.first,
        )

        reopened = self.fixture.reopened(
            enrollment=higher,
        )

        self.assertEqual(
            self.fixture.read(
                reopened,
                minimum_revision=11,
                minimum_generation=21,
                minimum_fence_token=31,
            ),
            self.fixture.first,
        )

    def test_07_corrupt_operation_receipt_fails_closed(self):
        self.assertEqual(
            self.fixture.advance(),
            self.fixture.first,
        )

        self.sql(
            "UPDATE protected_high_water_operations "
            "SET committed_generation = 99 "
            "WHERE operation_id = ?",
            (contract.OP_A,),
        )

        with self.assertRaises(ValueError):
            self.fixture.lookup()

        with self.assertRaises(ValueError):
            self.fixture.advance(
                self.fixture.reopened()
            )

        self.assertEqual(
            self.fixture.read(),
            self.fixture.first,
        )

    def test_08_future_operation_receipt_is_rejected(self):
        self.assertEqual(
            self.fixture.advance(),
            self.fixture.first,
        )

        # The receipt remains internally consistent,
        # but claims a committed revision above the
        # actual persisted high-water state.
        self.sql(
            "UPDATE protected_high_water_operations "
            "SET expected_revision = 20, "
            "next_revision = 21, "
            "committed_revision = 21 "
            "WHERE operation_id = ?",
            (contract.OP_A,),
        )

        with self.assertRaises(ValueError):
            self.fixture.lookup()

        with self.assertRaises(ValueError):
            self.fixture.advance(
                self.fixture.reopened(),
                expected_revision=20,
                next_revision=21,
                expected_generation=20,
                expected_fence_token=30,
            )

        self.assertEqual(
            self.fixture.read(),
            self.fixture.first,
        )

    def test_09_deleted_operation_receipt_is_known_limit(self):
        self.assertEqual(
            self.fixture.advance(),
            self.fixture.first,
        )

        self.sql(
            "DELETE FROM protected_high_water_operations "
            "WHERE operation_id = ?",
            (contract.OP_A,),
        )

        # KNOWN LIMIT: the store cannot cryptographically
        # detect external deletion of its operation journal.
        self.assertEqual(
            self.fixture.lookup(),
            ("unknown", self.fixture.first),
        )

        self.assertEqual(
            self.fixture.read(),
            self.fixture.first,
        )

        with self.assertRaises(ValueError):
            self.fixture.advance(
                self.fixture.reopened()
            )

        self.assertEqual(
            self.fixture.operation_count(),
            0,
        )

    def test_10_missing_state_cannot_authorize_cas_or_rebootstrap(self):
        self.sql(
            "DELETE FROM protected_high_water_state "
            "WHERE singleton_id = 1"
        )

        with self.assertRaises(ValueError):
            self.fixture.advance()

        self.assertEqual(
            self.fixture.operation_count(),
            0,
        )

        with self.assertRaises(ValueError):
            self.fixture.backend_type.bootstrap(
                path=self.fixture.path,
                signer=self.fixture.signer,
                store_id=contract.STORE_ID,
                enrollment=self.fixture.enrollment,
                initial_revision=10,
                initial_generation=20,
                initial_fence_token=30,
            )

        self.assertTrue(
            self.fixture.path.exists()
        )

    def test_11_injected_operation_insert_failure_is_atomic(self):
        self.sql(
            "CREATE TRIGGER reject_high_water_operation_adversarial "
            "BEFORE INSERT ON protected_high_water_operations "
            "BEGIN "
            "SELECT RAISE(ABORT, 'injected failure'); "
            "END"
        )

        with self.assertRaises(ValueError):
            self.fixture.advance()

        self.assertEqual(
            self.fixture.read(),
            self.fixture.initial,
        )

        self.assertEqual(
            self.fixture.operation_count(),
            0,
        )

        self.sql(
            "DROP TRIGGER reject_high_water_operation_adversarial"
        )

        self.assertEqual(
            self.fixture.advance(
                self.fixture.reopened()
            ),
            self.fixture.first,
        )

        self.assertEqual(
            self.fixture.operation_count(),
            1,
        )

    def test_12_concurrent_distinct_cas_has_single_winner(self):
        operations = (
            contract.OP_A,
            contract.OP_B,
            contract.OP_C,
            contract.OP_D,
        )

        def attempt(operation_id):
            provider = self.fixture.reopened()

            try:
                return self.fixture.advance(
                    provider,
                    operation_id=operation_id,
                )

            except ValueError:
                return None

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(
                executor.map(
                    attempt,
                    operations,
                )
            )

        self.assertEqual(
            results.count(self.fixture.first),
            1,
        )

        self.assertEqual(
            self.fixture.operation_count(),
            1,
        )

        self.assertEqual(
            self.fixture.read(self.fixture.reopened()),
            self.fixture.first,
        )

    def test_13_concurrent_identical_cas_is_idempotent(self):
        def attempt(_):
            return self.fixture.advance(
                self.fixture.reopened(),
                operation_id=contract.OP_A,
            )

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(
                executor.map(
                    attempt,
                    range(4),
                )
            )

        self.assertEqual(
            results,
            [self.fixture.first] * 4,
        )

        self.assertEqual(
            self.fixture.operation_count(),
            1,
        )

        self.assertEqual(
            self.fixture.read(),
            self.fixture.first,
        )

    def test_14_stale_cas_does_not_create_operation(self):
        self.assertEqual(
            self.fixture.advance(),
            self.fixture.first,
        )

        with self.assertRaises(ValueError):
            self.fixture.advance(
                self.fixture.reopened(),
                operation_id=contract.OP_B,
            )

        self.assertEqual(
            self.fixture.lookup(
                contract.OP_B,
                provider=self.fixture.reopened(),
            ),
            ("unknown", self.fixture.first),
        )

        self.assertEqual(
            self.fixture.operation_count(),
            1,
        )

    def test_15_operation_id_rebinding_refused_after_restart(self):
        self.assertEqual(
            self.fixture.advance(),
            self.fixture.first,
        )

        reopened = self.fixture.reopened()

        with self.assertRaises(ValueError):
            self.fixture.advance(
                reopened,
                operation_id=contract.OP_A,
                next_revision=12,
            )

        self.assertEqual(
            self.fixture.operation_count(),
            1,
        )

        self.assertEqual(
            self.fixture.read(reopened),
            self.fixture.first,
        )

    def test_16_lost_ack_after_commit_resolved_by_lookup(self):
        backend = self.fixture.backend

        class LostAcknowledgement:
            def __init__(self):
                self.calls = 0

            def hold(self, *, challenge):
                return backend.hold(
                    challenge=challenge
                )

            def lookup_operation(
                self,
                *,
                operation_id,
                challenge,
            ):
                return backend.lookup_operation(
                    operation_id=operation_id,
                    challenge=challenge,
                )

            def advance_if_current(self, **arguments):
                self.calls += 1

                backend.advance_if_current(
                    **arguments
                )

                raise TimeoutError(
                    "Acknowledgement lost after commit."
                )

        unreliable = LostAcknowledgement()

        client = self.fixture.client(
            unreliable
        )

        with self.assertRaises(ValueError):
            client.advance_if_current(
                operation_id=contract.OP_A,
                expected_revision=10,
                next_revision=11,
                expected_generation=20,
                expected_fence_token=30,
            )

        self.assertEqual(
            unreliable.calls,
            1,
        )

        reopened = self.fixture.reopened()

        self.assertEqual(
            self.fixture.lookup(
                provider=reopened
            ),
            ("committed", self.fixture.first),
        )

        self.assertEqual(
            self.fixture.advance(reopened),
            self.fixture.first,
        )

        self.assertEqual(
            self.fixture.operation_count(),
            1,
        )

    def test_17_historical_receipt_never_rewinds_current_state(self):
        self.assertEqual(
            self.fixture.advance(),
            self.fixture.first,
        )

        self.assertEqual(
            self.fixture.advance(
                operation_id=contract.OP_B,
                expected_revision=11,
                next_revision=12,
                expected_generation=21,
                expected_fence_token=31,
            ),
            self.fixture.second,
        )

        reopened = self.fixture.reopened()

        self.assertEqual(
            self.fixture.advance(reopened),
            self.fixture.first,
        )

        self.assertEqual(
            self.fixture.read(reopened),
            self.fixture.second,
        )

        self.assertEqual(
            self.fixture.lookup(
                contract.OP_A,
                provider=reopened,
            ),
            ("committed", self.fixture.second),
        )

        self.assertEqual(
            self.fixture.operation_count(),
            2,
        )

    def test_18_valid_whole_file_rollback_is_known_limit(self):
        backup = (
            Path(self.fixture.temp.name)
            / "old-valid-high-water.sqlite3"
        )

        shutil.copyfile(
            self.fixture.path,
            backup,
        )

        self.assertEqual(
            self.fixture.advance(),
            self.fixture.first,
        )

        higher = {
            "minimum_revision": 11,
            "minimum_generation": 21,
            "minimum_fence_token": 31,
        }

        self.assertEqual(
            self.fixture.read(**higher),
            self.fixture.first,
        )

        # A valid older DB image may replace the newer one.
        # This is deliberately documented as a security limit.
        shutil.copyfile(
            backup,
            self.fixture.path,
        )

        reopened = self.fixture.reopened()

        self.assertEqual(
            self.fixture.read(reopened),
            self.fixture.initial,
        )

        self.assertEqual(
            self.fixture.lookup(
                provider=reopened
            ),
            ("unknown", self.fixture.initial),
        )

        # The rollback is detectable only when higher trusted
        # minima survive independently of the replaced store.
        with self.assertRaises(ValueError):
            self.fixture.read(
                reopened,
                **higher,
            )


if __name__ == "__main__":
    unittest.main()
