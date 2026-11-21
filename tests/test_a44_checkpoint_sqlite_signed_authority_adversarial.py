"""A44 adversarial SQLite signed checkpoint authority tests.

Tests exercise SQLite state corruption, signer failures,
64-bit counter boundaries, local transactional exclusion,
ambiguous post-commit failures and complete-file rollback.

SECURITY LIMITS:
- These tests run only against isolated temporary SQLite files.
- Local SQLite transactions are not remotely held leases.
- No hardware/power-loss durability proof is established.
- Complete-file rollback remains possible.
- Caller pins are not independently enrolled.
- No checkpoint restore or republication is authorized.
"""

import shutil
import sqlite3
import sys
import unittest

from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_sqlite_signed_authority as contract


OLD = contract.OLD
NEXT = contract.NEXT
GENERATION = contract.GENERATION
FENCE = contract.FENCE
CHALLENGE = contract.CHALLENGE

MAX_SQLITE_INTEGER = (1 << 63) - 1

TABLE = "checkpoint_signed_authority_state"


class BytesSubclass(bytes):
    pass


class A44CheckpointSQLiteSignedAuthorityAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44CheckpointSQLiteSignedAuthorityContractTests(
                "test_canonical_signed_held_read"
            )
        )

        self.fixture.setUp()

        self.addCleanup(
            self.fixture.doCleanups
        )

    def database(self, suffix):
        return (
            Path(self.fixture.folder.name)
            / f"adversarial-{suffix}.sqlite3"
        )

    def bootstrap(self, *, path=None, **changes):
        selected = (
            self.fixture.path
            if path is None
            else path
        )

        return self.fixture.bootstrap(
            path=selected,
            **changes,
        )

    def client(self, backend, **changes):
        return self.fixture.client(
            backend,
            **changes,
        )

    def read(self, source):
        return self.fixture.read(
            source
        )

    def advance(self, source, **changes):
        return self.fixture.advance(
            source,
            **changes,
        )

    def expected(
        self,
        revision=OLD,
        generation=GENERATION,
        fence=FENCE,
    ):
        return self.fixture.expected(
            revision,
            generation,
            fence,
        )

    @staticmethod
    def execute(path, statement, parameters=()):
        with closing(
            sqlite3.connect(
                path,
                timeout=0.15,
            )
        ) as connection:
            with connection:
                connection.execute(
                    statement,
                    parameters,
                )

    @staticmethod
    def read_counters(path):
        with closing(
            sqlite3.connect(path)
        ) as connection:
            return connection.execute(
                "SELECT revision, generation, fence_token "
                f"FROM {TABLE} WHERE singleton_id = 1"
            ).fetchone()

    def test_stored_identity_and_public_keys_cannot_be_rebound(
        self
    ):
        attacks = (
            ("authority_id", "foreign-authority"),
            ("authority_public_key", b"\x42" * 32),
            ("root_id", "foreign-root"),
            ("root_public_key", b"\x43" * 32),
            ("enrollment_epoch", contract.EPOCH + 1),
        )

        for index, (field, value) in enumerate(attacks):
            with self.subTest(field=field):
                path = self.database(
                    f"identity-{index}"
                )

                backend = self.bootstrap(path=path)

                self.execute(
                    path,
                    f"UPDATE {TABLE} SET {field} = ? "
                    "WHERE singleton_id = 1",
                    (value,),
                )

                with self.assertRaises(ValueError):
                    self.read(
                        self.client(backend)
                    )

                with self.assertRaises(ValueError):
                    self.fixture.reopen(
                        path=path
                    )

                with self.assertRaises(ValueError):
                    backend.advance_if_current(
                        expected_revision=OLD,
                        next_revision=NEXT,
                        expected_generation=GENERATION,
                        expected_fence_token=FENCE,
                        challenge=CHALLENGE,
                    )

                self.assertEqual(
                    self.read_counters(path),
                    (OLD, GENERATION, FENCE),
                )

    def test_deleted_row_and_missing_table_fail_closed(
        self
    ):
        mutations = (
            (
                "missing-row",
                f"DELETE FROM {TABLE}",
            ),
            (
                "missing-table",
                f"DROP TABLE {TABLE}",
            ),
        )

        for name, statement in mutations:
            with self.subTest(mutation=name):
                path = self.database(name)

                backend = self.bootstrap(path=path)

                self.execute(
                    path,
                    statement,
                )

                with self.assertRaises(ValueError):
                    self.read(
                        self.client(backend)
                    )

                with self.assertRaises(ValueError):
                    self.fixture.reopen(
                        path=path
                    )

                with self.assertRaises(ValueError):
                    backend.advance_if_current(
                        expected_revision=OLD,
                        next_revision=NEXT,
                        expected_generation=GENERATION,
                        expected_fence_token=FENCE,
                        challenge=CHALLENGE,
                    )

    def test_invalid_stored_counter_types_fail_closed(
        self
    ):
        for index, field in enumerate(
            ("revision", "generation", "fence_token")
        ):
            with self.subTest(counter=field):
                path = self.database(
                    f"counter-{index}"
                )

                backend = self.bootstrap(path=path)

                with closing(
                    sqlite3.connect(path)
                ) as connection:
                    connection.execute(
                        "PRAGMA ignore_check_constraints=ON"
                    )

                    with connection:
                        connection.execute(
                            f"UPDATE {TABLE} "
                            f"SET {field} = ? "
                            "WHERE singleton_id = 1",
                            ("not-an-integer",),
                        )

                with self.assertRaises(ValueError):
                    self.read(
                        self.client(backend)
                    )

                with self.assertRaises(ValueError):
                    self.fixture.reopen(
                        path=path
                    )

                with self.assertRaises(ValueError):
                    backend.advance_if_current(
                        expected_revision=OLD,
                        next_revision=NEXT,
                        expected_generation=GENERATION,
                        expected_fence_token=FENCE,
                        challenge=CHALLENGE,
                    )

    def test_sqlite_64bit_counter_limits_are_enforced(
        self
    ):
        invalid_bootstrap = (
            ("initial_revision", MAX_SQLITE_INTEGER + 1),
            ("initial_generation", MAX_SQLITE_INTEGER + 1),
            ("initial_fence_token", MAX_SQLITE_INTEGER + 1),
        )

        for index, (field, value) in enumerate(
            invalid_bootstrap
        ):
            with self.subTest(bootstrap_field=field):
                path = self.database(
                    f"overflow-bootstrap-{index}"
                )

                with self.assertRaises(ValueError):
                    self.bootstrap(
                        path=path,
                        **{field: value},
                    )

                self.assertFalse(
                    path.exists()
                )

        cases = (
            (
                "generation",
                {"initial_generation": MAX_SQLITE_INTEGER},
                {
                    "expected_generation": MAX_SQLITE_INTEGER,
                    "expected_fence_token": FENCE,
                },
            ),
            (
                "fence",
                {"initial_fence_token": MAX_SQLITE_INTEGER},
                {
                    "expected_generation": GENERATION,
                    "expected_fence_token": MAX_SQLITE_INTEGER,
                },
            ),
        )

        for index, (name, initial, requested) in enumerate(
            cases
        ):
            with self.subTest(overflow=name):
                path = self.database(
                    f"overflow-cas-{index}"
                )

                backend = self.bootstrap(
                    path=path,
                    **initial,
                )

                before = self.read_counters(path)

                with self.assertRaises(ValueError):
                    backend.advance_if_current(
                        expected_revision=OLD,
                        next_revision=NEXT,
                        challenge=CHALLENGE,
                        **requested,
                    )

                self.assertEqual(
                    self.read_counters(path),
                    before,
                )

        backend = self.bootstrap(
            path=self.database("overflow-target")
        )

        with self.assertRaises(ValueError):
            backend.advance_if_current(
                expected_revision=OLD,
                next_revision=MAX_SQLITE_INTEGER + 1,
                expected_generation=GENERATION,
                expected_fence_token=FENCE,
                challenge=CHALLENGE,
            )

    def test_signer_failure_after_commit_has_uncertain_result(
        self
    ):
        backend = self.bootstrap()

        source = self.client(backend)

        with patch.object(
            self.fixture.backend_type,
            "_signed",
            side_effect=RuntimeError(
                "Injected post-commit signer failure."
            ),
        ):
            with self.assertRaises(ValueError):
                self.advance(source)

        # The database has committed before its acknowledgement
        # could be signed. Failure must not be interpreted as
        # rollback of the operation.

        published = self.expected(
            NEXT,
            GENERATION + 1,
            FENCE + 1,
        )

        self.assertEqual(
            self.read(
                self.client(self.fixture.reopen())
            ),
            published,
        )

        with self.assertRaises(ValueError):
            self.advance(source)

        self.assertEqual(
            self.read_counters(self.fixture.path),
            (
                NEXT,
                GENERATION + 1,
                FENCE + 1,
            ),
        )

    def test_signer_failure_during_read_releases_lock(
        self
    ):
        backend = self.bootstrap()

        source = self.client(backend)

        with patch.object(
            self.fixture.backend_type,
            "_signed",
            side_effect=RuntimeError(
                "Injected held-read signing failure."
            ),
        ):
            with self.assertRaises(ValueError):
                self.read(source)

        # No held transaction may survive the signing error.

        self.assertEqual(
            self.advance(source),
            self.expected(
                NEXT,
                GENERATION + 1,
                FENCE + 1,
            ),
        )

    def test_external_signer_replacement_is_rejected(
        self
    ):
        backend = self.bootstrap()

        with closing(
            sqlite3.connect(self.fixture.path)
        ) as connection:
            stored_public = connection.execute(
                f"SELECT authority_public_key FROM {TABLE}"
            ).fetchone()[0]

        self.assertEqual(
            stored_public,
            self.fixture.public_key,
        )

        private_raw = self.fixture.signer.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # This is a check of the reference schema, not
        # an assertion of private key isolation or HSM use.
        self.assertNotIn(
            private_raw,
            self.fixture.path.read_bytes(),
        )

        rogue = Ed25519PrivateKey.generate()

        object.__setattr__(
            backend,
            "signer",
            rogue,
        )

        with self.assertRaises(ValueError):
            self.read(
                self.client(backend)
            )

        with self.assertRaises(ValueError):
            backend.advance_if_current(
                expected_revision=OLD,
                next_revision=NEXT,
                expected_generation=GENERATION,
                expected_fence_token=FENCE,
                challenge=CHALLENGE,
            )

        with self.assertRaises(ValueError):
            self.fixture.reopen(
                signer=rogue
            )

        self.assertEqual(
            self.read(
                self.client(self.fixture.reopen())
            ),
            self.expected(),
        )

    def test_wal_mode_change_is_rejected(
        self
    ):
        backend = self.bootstrap()

        with closing(
            sqlite3.connect(
                self.fixture.path,
                isolation_level=None,
            )
        ) as connection:
            journal = connection.execute(
                "PRAGMA journal_mode=WAL"
            ).fetchone()[0]

            self.assertEqual(
                journal.lower(),
                "wal",
            )

        with self.assertRaises(ValueError):
            self.fixture.reopen()

        with self.assertRaises(ValueError):
            self.read(
                self.client(backend)
            )

        with self.assertRaises(ValueError):
            backend.advance_if_current(
                expected_revision=OLD,
                next_revision=NEXT,
                expected_generation=GENERATION,
                expected_fence_token=FENCE,
                challenge=CHALLENGE,
            )

        self.assertEqual(
            self.read_counters(self.fixture.path),
            (OLD, GENERATION, FENCE),
        )

    def test_held_read_blocks_external_sqlite_writer(
        self
    ):
        backend = self.bootstrap()

        source = self.client(backend)

        with source.hold() as held:
            self.assertEqual(
                held,
                self.expected(),
            )

            with closing(
                sqlite3.connect(
                    self.fixture.path,
                    timeout=0.05,
                    isolation_level=None,
                )
            ) as connection:
                connection.execute(
                    "PRAGMA busy_timeout=50"
                )

                try:
                    with self.assertRaises(
                        sqlite3.OperationalError
                    ):
                        connection.execute(
                            "BEGIN IMMEDIATE"
                        )

                        connection.execute(
                            f"UPDATE {TABLE} "
                            "SET revision = ? "
                            "WHERE singleton_id = 1",
                            (NEXT,),
                        )

                        connection.commit()

                finally:
                    if connection.in_transaction:
                        connection.rollback()

            self.assertEqual(
                held[3:],
                (OLD, GENERATION, FENCE),
            )

        self.assertEqual(
            self.advance(source),
            self.expected(
                NEXT,
                GENERATION + 1,
                FENCE + 1,
            ),
        )

    def test_multiple_handles_reject_stale_publication(
        self
    ):
        first = self.bootstrap()
        second = self.fixture.reopen()

        first_client = self.client(first)
        second_client = self.client(second)

        self.assertEqual(
            self.advance(first_client),
            self.expected(
                NEXT,
                GENERATION + 1,
                FENCE + 1,
            ),
        )

        with self.assertRaises(ValueError):
            self.advance(
                second_client,
                old_revision=OLD,
                new_revision=NEXT + 1,
            )

        self.assertEqual(
            self.read_counters(self.fixture.path),
            (
                NEXT,
                GENERATION + 1,
                FENCE + 1,
            ),
        )

        self.assertEqual(
            self.advance(
                second_client,
                old_revision=NEXT,
                new_revision=NEXT + 1,
                old_generation=GENERATION + 1,
                old_fence=FENCE + 1,
            ),
            self.expected(
                NEXT + 1,
                GENERATION + 2,
                FENCE + 2,
            ),
        )

    def test_complete_file_rollback_remains_possible(
        self
    ):
        backend = self.bootstrap()

        older = self.database(
            "older-valid-copy"
        )

        shutil.copyfile(
            self.fixture.path,
            older,
        )

        self.assertEqual(
            self.advance(self.client(backend)),
            self.expected(
                NEXT,
                GENERATION + 1,
                FENCE + 1,
            ),
        )

        self.assertEqual(
            self.read(
                self.client(self.fixture.reopen())
            )[3],
            NEXT,
        )

        # Deliberate complete-file rollback simulation.
        shutil.copyfile(
            older,
            self.fixture.path,
        )

        reopened = self.fixture.reopen()

        self.assertEqual(
            self.read(self.client(reopened)),
            self.expected(),
        )

        strict = self.client(
            reopened,
            minimum_revision=NEXT,
            minimum_generation=GENERATION + 1,
            minimum_fence_token=FENCE + 1,
        )

        with self.assertRaises(ValueError):
            self.read(strict)

        # The stale caller pins still accept the older state.
        self.assertEqual(
            self.read(self.client(reopened)),
            self.expected(),
        )

    def test_invalid_transport_challenges_never_publish(
        self
    ):
        backend = self.bootstrap()

        invalid = (
            None,
            True,
            b"",
            b"x" * 31,
            b"x" * 33,
            bytearray(CHALLENGE),
            BytesSubclass(CHALLENGE),
            "not-bytes",
        )

        for challenge in invalid:
            with self.subTest(
                challenge_type=type(challenge).__name__,
                challenge=repr(challenge)[:40],
            ):
                with self.assertRaises(ValueError):
                    with backend.hold(
                        challenge=challenge
                    ):
                        self.fail(
                            "Invalid challenge accepted."
                        )

                with self.assertRaises(ValueError):
                    backend.advance_if_current(
                        expected_revision=OLD,
                        next_revision=NEXT,
                        expected_generation=GENERATION,
                        expected_fence_token=FENCE,
                        challenge=challenge,
                    )

        self.assertEqual(
            self.read_counters(self.fixture.path),
            (
                OLD,
                GENERATION,
                FENCE,
            ),
        )

        self.assertEqual(
            self.read(self.client(backend)),
            self.expected(),
        )


if __name__ == "__main__":
    unittest.main()
