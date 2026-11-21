"""A44 / 66.29B SQLite reference high-water CAS recovery contract.

EXPECTED RED: production backend module is not installed.

TARGET API:

SQLiteReferenceSignedProtectedHighWaterCASAuthority.bootstrap(
    *, path, signer, store_id, enrollment,
    initial_revision, initial_generation, initial_fence_token
)

SQLiteReferenceSignedProtectedHighWaterCASAuthority.open(
    *, path, signer, expected_store_id, enrollment
)

The returned provider exposes:
    hold(*, challenge)
    advance_if_current(
        *, operation_id, expected_revision, next_revision,
        expected_generation, expected_fence_token, challenge
    )
    lookup_operation(*, operation_id, challenge)

All responses conform to the existing canonical Ed25519-signed
protected-high-water protocol.

REQUIRED SQLITE TABLES:

    protected_high_water_state
    protected_high_water_operations

State and committed operation receipt must be published in one
SQLite transaction. Recovery reads the persisted operation record.

SECURITY LIMITS:
- The backend is a LOCAL SQLITE REFERENCE implementation.
- A separate file is not an independent security boundary.
- Signed results cannot prove an honest external authority.
- A valid whole-file rollback may restore older state.
- No remote service, HSM or protected key provisioning.
- No physical power-loss durability proof.
- No cross-store atomicity or checkpoint restoration.
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

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from core.existence.history_receipt_trust_checkpoint_protected_high_water import (
    PinnedSignedProtectedHighWaterClient,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_anchor_trusted_enrollment_contract as enrollment_contract
import test_a44_checkpoint_anchor_cas_backend_contract as backend_contract


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_high_water_cas_backend_sqlite_reference"
)

TYPE = "SQLiteReferenceSignedProtectedHighWaterCASAuthority"

STORE_ID = "a44-reference-protected-high-water"

OP_A = "a" * 32
OP_B = "b" * 32
OP_C = "c" * 32
OP_D = "d" * 32


class A44ProtectedHighWaterCASBackendContractTests(
    unittest.TestCase
):

    def setUp(self):
        module = importlib.import_module(MODULE)
        self.backend_type = getattr(module, TYPE)

        self.enrollment_fixture = (
            enrollment_contract.A44CheckpointAnchorTrustedEnrollmentContractTests(
                "test_01_signed_enrollment_binds_read_and_cas"
            )
        )

        self.enrollment_fixture.setUp()
        self.addCleanup(
            self.enrollment_fixture.doCleanups
        )

        self.enrollment = (
            self.enrollment_fixture.enrolled()
        )

        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.path = (
            Path(self.temp.name)
            / "reference-high-water.sqlite3"
        )

        self.signer = Ed25519PrivateKey.generate()
        self.signer_key = backend_contract.public_key(
            self.signer
        )

        self.initial = (10, 20, 30)
        self.first = (11, 21, 31)
        self.second = (12, 22, 32)

        self.backend = self.backend_type.bootstrap(
            path=self.path,
            signer=self.signer,
            store_id=STORE_ID,
            enrollment=self.enrollment,
            initial_revision=10,
            initial_generation=20,
            initial_fence_token=30,
        )

    def reopened(self, **changes):
        arguments = {
            "path": self.path,
            "signer": self.signer,
            "expected_store_id": STORE_ID,
            "enrollment": self.enrollment,
        }

        arguments.update(changes)

        return self.backend_type.open(
            **arguments
        )

    def client(self, provider=None, **changes):
        if provider is None:
            provider = self.backend

        arguments = {
            "provider": provider,
            "enrollment": self.enrollment,
            "expected_store_id": STORE_ID,
            "expected_store_public_key": self.signer_key,
            "minimum_revision": 10,
            "minimum_generation": 20,
            "minimum_fence_token": 30,
        }

        arguments.update(changes)

        return PinnedSignedProtectedHighWaterClient.from_provider(
            **arguments
        )

    def read(self, provider=None, **changes):
        with self.client(
            provider,
            **changes,
        ).hold_floor() as floor:
            return floor

    def advance(
        self,
        provider=None,
        **changes,
    ):
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
        ).advance_if_current(
            **arguments
        )

    def lookup(self, operation_id=OP_A, provider=None):
        return self.client(
            provider
        ).lookup_operation(
            operation_id=operation_id
        )

    def operation_count(self):
        with closing(
            sqlite3.connect(self.path)
        ) as connection:
            return connection.execute(
                "SELECT COUNT(*) FROM protected_high_water_operations"
            ).fetchone()[0]

    def test_01_bootstrap_produces_verified_signed_read(self):
        self.assertTrue(
            self.path.is_file()
        )

        self.assertEqual(
            self.read(),
            self.initial,
        )

    def test_02_open_recovers_signed_state(self):
        reopened = self.reopened()

        self.assertEqual(
            self.read(reopened),
            self.initial,
        )

    def test_03_committed_cas_survives_reopen(self):
        self.assertEqual(
            self.advance(),
            self.first,
        )

        reopened = self.reopened()

        self.assertEqual(
            self.read(reopened),
            self.first,
        )

        self.assertEqual(
            self.lookup(provider=reopened),
            ("committed", self.first),
        )

    def test_04_sequential_cas_persists_monotonic_counters(self):
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
            self.operation_count(),
            2,
        )

    def test_05_idempotent_retry_survives_reopen(self):
        self.assertEqual(
            self.advance(),
            self.first,
        )

        reopened = self.reopened()

        self.assertEqual(
            self.advance(reopened),
            self.first,
        )

        self.assertEqual(
            self.operation_count(),
            1,
        )

        self.assertEqual(
            self.read(reopened),
            self.first,
        )

    def test_06_reused_operation_id_cannot_change_request(self):
        self.assertEqual(
            self.advance(),
            self.first,
        )

        with self.assertRaises(ValueError):
            self.advance(
                self.reopened(),
                next_revision=12,
            )

        self.assertEqual(
            self.read(),
            self.first,
        )

        self.assertEqual(
            self.operation_count(),
            1,
        )

    def test_07_stale_competing_cas_does_not_publish(self):
        self.assertEqual(
            self.advance(),
            self.first,
        )

        with self.assertRaises(ValueError):
            self.advance(
                self.reopened(),
                operation_id=OP_B,
            )

        self.assertEqual(
            self.lookup(OP_B),
            ("unknown", self.first),
        )

        self.assertEqual(
            self.operation_count(),
            1,
        )

    def test_08_concurrent_distinct_cas_single_winner(self):
        operations = (
            OP_A,
            OP_B,
            OP_C,
            OP_D,
        )

        def attempt(operation_id):
            provider = self.reopened()

            try:
                return self.advance(
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
            results.count(self.first),
            1,
        )

        self.assertEqual(
            self.operation_count(),
            1,
        )

        self.assertEqual(
            self.read(self.reopened()),
            self.first,
        )

    def test_09_concurrent_identical_cas_is_idempotent(self):
        def attempt(_):
            return self.advance(
                self.reopened()
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
            [self.first] * 4,
        )

        self.assertEqual(
            self.operation_count(),
            1,
        )

        self.assertEqual(
            self.read(),
            self.first,
        )

    def test_10_lost_ack_after_commit_recovers_by_lookup(self):
        backend = self.backend

        class LostAcknowledgementProvider:
            def __init__(self):
                self.calls = 0

            def hold(self, *, challenge):
                return backend.hold(
                    challenge=challenge
                )

            def lookup_operation(self, *, operation_id, challenge):
                return backend.lookup_operation(
                    operation_id=operation_id,
                    challenge=challenge,
                )

            def advance_if_current(self, **arguments):
                self.calls += 1

                response = backend.advance_if_current(
                    **arguments
                )

                if self.calls == 1:
                    raise TimeoutError(
                        "Simulated lost acknowledgement after COMMIT."
                    )

                return response

        unreliable = LostAcknowledgementProvider()
        client = self.client(unreliable)

        with self.assertRaises(ValueError):
            client.advance_if_current(
                operation_id=OP_A,
                expected_revision=10,
                next_revision=11,
                expected_generation=20,
                expected_fence_token=30,
            )

        self.assertEqual(
            unreliable.calls,
            1,
        )

        reopened = self.reopened()

        self.assertEqual(
            self.lookup(provider=reopened),
            ("committed", self.first),
        )

        self.assertEqual(
            self.advance(reopened),
            self.first,
        )

        self.assertEqual(
            self.operation_count(),
            1,
        )

    def test_11_unknown_lookup_survives_reopen_without_write(self):
        reopened = self.reopened()

        self.assertEqual(
            self.lookup(OP_B, provider=reopened),
            ("unknown", self.initial),
        )

        self.assertEqual(
            self.operation_count(),
            0,
        )

        self.assertEqual(
            self.read(reopened),
            self.initial,
        )

    def test_12_bootstrap_refuses_existing_store(self):
        with self.assertRaises(ValueError):
            self.backend_type.bootstrap(
                path=self.path,
                signer=self.signer,
                store_id=STORE_ID,
                enrollment=self.enrollment,
                initial_revision=10,
                initial_generation=20,
                initial_fence_token=30,
            )

        self.assertEqual(
            self.read(),
            self.initial,
        )

    def test_13_open_refuses_missing_store(self):
        missing = (
            Path(self.temp.name)
            / "missing-high-water.sqlite3"
        )

        with self.assertRaises(ValueError):
            self.reopened(
                path=missing,
            )

        self.assertFalse(
            missing.exists()
        )

    def test_14_open_refuses_wrong_store_signer(self):
        attacker = Ed25519PrivateKey.generate()

        with self.assertRaises(ValueError):
            self.reopened(
                signer=attacker,
            )

        self.assertEqual(
            self.read(),
            self.initial,
        )

    def test_15_open_refuses_wrong_store_identity(self):
        with self.assertRaises(ValueError):
            self.reopened(
                expected_store_id="another-high-water-store",
            )

        self.assertEqual(
            self.read(),
            self.initial,
        )

    def test_16_open_rejects_enrollment_floor_above_state(self):
        higher_enrollment = self.enrollment.raise_floor(
            minimum_revision=11,
            minimum_generation=21,
            minimum_fence_token=31,
        )

        with self.assertRaises(ValueError):
            self.reopened(
                enrollment=higher_enrollment,
            )

        self.assertEqual(
            self.read(),
            self.initial,
        )

    def test_17_corrupt_stored_negative_counter_fails_closed(self):
        with closing(
            sqlite3.connect(self.path)
        ) as connection:
            with connection:
                connection.execute(
                    "UPDATE protected_high_water_state "
                    "SET revision = -1 WHERE singleton_id = 1"
                )

        with self.assertRaises(ValueError):
            self.read()

        with self.assertRaises(ValueError):
            self.reopened()

    def test_18_failed_operation_insert_rolls_back_state(self):
        with closing(
            sqlite3.connect(self.path)
        ) as connection:
            with connection:
                connection.execute(
                    "CREATE TRIGGER reject_high_water_operation "
                    "BEFORE INSERT ON protected_high_water_operations "
                    "BEGIN SELECT RAISE(ABORT, 'injected write failure'); "
                    "END"
                )

        with self.assertRaises(ValueError):
            self.advance()

        self.assertEqual(
            self.read(self.reopened()),
            self.initial,
        )

        self.assertEqual(
            self.operation_count(),
            0,
        )

        with closing(
            sqlite3.connect(self.path)
        ) as connection:
            with connection:
                connection.execute(
                    "DROP TRIGGER reject_high_water_operation"
                )

        self.assertEqual(
            self.advance(self.reopened()),
            self.first,
        )

        self.assertEqual(
            self.operation_count(),
            1,
        )

    def test_19_historical_retry_never_rewinds_current_state(self):
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

        reopened = self.reopened()

        self.assertEqual(
            self.advance(reopened),
            self.first,
        )

        self.assertEqual(
            self.read(reopened),
            self.second,
        )

        self.assertEqual(
            self.lookup(OP_A, provider=reopened),
            ("committed", self.second),
        )

        self.assertEqual(
            self.operation_count(),
            2,
        )

    def test_20_whole_file_rollback_is_explicit_known_limit(self):
        backup = (
            Path(self.temp.name)
            / "old-valid-high-water.sqlite3"
        )

        shutil.copyfile(
            self.path,
            backup,
        )

        self.assertEqual(
            self.advance(),
            self.first,
        )

        higher_minima = {
            "minimum_revision": 11,
            "minimum_generation": 21,
            "minimum_fence_token": 31,
        }

        self.assertEqual(
            self.read(**higher_minima),
            self.first,
        )

        # Adversarial replacement of the complete valid
        # SQLite store is a KNOWN SECURITY LIMIT.
        shutil.copyfile(
            backup,
            self.path,
        )

        reopened = self.reopened()

        # Original stale trusted minima accept old signed state.
        self.assertEqual(
            self.read(reopened),
            self.initial,
        )

        self.assertEqual(
            self.lookup(OP_A, provider=reopened),
            ("unknown", self.initial),
        )

        # An independently retained floor catches the rollback.
        with self.assertRaises(ValueError):
            self.read(
                reopened,
                **higher_minima,
            )


if __name__ == "__main__":
    unittest.main()
