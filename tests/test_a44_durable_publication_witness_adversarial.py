"""A44 adversarial local publication witness validation.

Expected RED:
Replacing the SQLite witness table with a valid-looking
but non-unique schema can introduce duplicate incident
identities that historical validation must reject.

The other tests exercise concurrency, atomic rollback,
malformed history and explicitly documented trust gaps.

This is not a malicious-host security guarantee.
All databases are temporary.
"""

import sqlite3
import tempfile
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, contextmanager
from pathlib import Path

from core.existence.history_receipt_trust_publication_witness import (
    LocalDurablePublicationWitnessJournal,
    PublicationWitnessPhase,
)


WORLD = "a44_adversarial_witness_world"

CRON_A = "cronenberg_deadbeef"
CRON_B = "cronenberg_1234abcd"

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


@contextmanager
def edit_database(path):
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            yield connection


class A44PublicationWitnessAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        directory = tempfile.TemporaryDirectory(
            prefix="a44_witness_adversarial_"
        )

        self.addCleanup(directory.cleanup)

        self.path = (
            Path(directory.name) / "witness.sqlite"
        )

        self.Journal = LocalDurablePublicationWitnessJournal

        self.store = self.Journal.create(
            self.path,
            universe_id=WORLD,
            max_entries=16,
        )

    def handles(self, count, path=None):
        return [
            self.Journal.open(
                self.path if path is None else path,
                universe_id=WORLD,
            )
            for _ in range(count)
        ]

    def test_concurrent_same_incident_prepare_is_idempotent(self):
        handles = self.handles(8)

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(
                pool.map(
                    lambda handle: handle.prepare(
                        "incident-concurrent-same",
                        "security_validation",
                    ),
                    handles,
                )
            )

        self.assertEqual(
            sum(value is True for value in results),
            1,
        )

        self.assertEqual(
            sum(value is False for value in results),
            7,
        )

        reopened = self.Journal.open(
            self.path,
            universe_id=WORLD,
        )

        self.assertEqual(
            len(reopened.pending()),
            1,
        )

    def test_concurrent_distinct_incidents_obey_capacity(self):
        path = self.path.parent / "limited.sqlite"

        limited = self.Journal.create(
            path,
            universe_id=WORLD,
            max_entries=3,
        )

        handles = self.handles(8, path)

        def create_incident(index):
            try:
                return handles[index].prepare(
                    f"incident-capacity-{index}",
                    "security_validation",
                )

            except ValueError as exc:
                if "capacity" not in str(exc):
                    raise

                return "full"

        with ThreadPoolExecutor(max_workers=8) as pool:
            outcomes = list(
                pool.map(
                    create_incident,
                    range(8),
                )
            )

        self.assertEqual(
            sum(value is True for value in outcomes),
            3,
        )

        self.assertEqual(
            outcomes.count("full"),
            5,
        )

        self.assertEqual(
            len(limited.pending()),
            3,
        )

    def test_concurrent_same_observation_is_idempotent(self):
        incident_id = "incident-concurrent-observe"

        self.store.prepare(
            incident_id,
            "security_validation",
        )

        handles = self.handles(8)

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(
                pool.map(
                    lambda handle: handle.observe(
                        incident_id,
                        CRON_A,
                        DIGEST_A,
                    ),
                    handles,
                )
            )

        self.assertEqual(
            sum(value is True for value in results),
            1,
        )

        self.assertEqual(
            sum(value is False for value in results),
            7,
        )

        self.assertIs(
            self.store.get(incident_id).phase,
            PublicationWitnessPhase.OBSERVED,
        )

    def test_simultaneous_conflicting_observations_rejected(self):
        incident_id = "incident-concurrent-conflict"

        self.store.prepare(
            incident_id,
            "security_validation",
        )

        handles = self.handles(2)

        def observe(index):
            cronenberg = (
                CRON_A if index == 0 else CRON_B
            )

            digest = (
                DIGEST_A if index == 0 else DIGEST_B
            )

            try:
                return handles[index].observe(
                    incident_id,
                    cronenberg,
                    digest,
                )

            except ValueError as exc:
                if "Conflicting publication observation" not in str(exc):
                    raise

                return "conflict"

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(
                pool.map(observe, range(2))
            )

        self.assertEqual(
            sum(value is True for value in results),
            1,
        )

        self.assertEqual(
            results.count("conflict"),
            1,
        )

        record = self.store.get(incident_id)

        self.assertIn(
            (record.cronenberg_id, record.manifestation_digest),
            (
                (CRON_A, DIGEST_A),
                (CRON_B, DIGEST_B),
            ),
        )

    def test_prepare_sqlite_abort_rolls_back(self):
        incident_id = "incident-insert-aborted"

        with edit_database(self.path) as connection:
            connection.execute(
                "CREATE TRIGGER witness_abort_insert "
                "BEFORE INSERT ON publication_witnesses "
                "BEGIN "
                "SELECT RAISE(ABORT, 'injected insert failure'); "
                "END"
            )

        with self.assertRaises(ValueError):
            self.store.prepare(
                incident_id,
                "security_validation",
            )

        self.assertIsNone(
            self.store.get(incident_id)
        )

        with edit_database(self.path) as connection:
            connection.execute(
                "DROP TRIGGER witness_abort_insert"
            )

        self.assertIs(
            self.store.prepare(
                incident_id,
                "security_validation",
            ),
            True,
        )

    def test_observe_sqlite_abort_preserves_prepared(self):
        incident_id = "incident-update-aborted"

        self.store.prepare(
            incident_id,
            "security_validation",
        )

        with edit_database(self.path) as connection:
            connection.execute(
                "CREATE TRIGGER witness_abort_update "
                "BEFORE UPDATE OF phase "
                "ON publication_witnesses "
                "BEGIN "
                "SELECT RAISE(ABORT, 'injected update failure'); "
                "END"
            )

        with self.assertRaises(ValueError):
            self.store.observe(
                incident_id,
                CRON_A,
                DIGEST_A,
            )

        self.assertIs(
            self.store.get(incident_id).phase,
            PublicationWitnessPhase.PREPARED,
        )

        with edit_database(self.path) as connection:
            connection.execute(
                "DROP TRIGGER witness_abort_update"
            )

        self.assertIs(
            self.store.observe(
                incident_id,
                CRON_A,
                DIGEST_A,
            ),
            True,
        )

    def test_invalid_historical_operation_rejected_on_open(self):
        incident_id = "incident-invalid-operation"

        self.store.prepare(
            incident_id,
            "security_validation",
        )

        with edit_database(self.path) as connection:
            connection.execute(
                "UPDATE publication_witnesses "
                "SET source_operation='unsupported_operation' "
                "WHERE incident_id=?",
                (incident_id,),
            )

        with self.assertRaises(ValueError):
            self.Journal.open(
                self.path,
                universe_id=WORLD,
            )

    def test_deleted_historical_sequence_rejected_on_open(self):
        self.store.prepare(
            "incident-sequence-001",
            "security_validation",
        )

        self.store.prepare(
            "incident-sequence-002",
            "security_validation",
        )

        with edit_database(self.path) as connection:
            connection.execute(
                "DELETE FROM publication_witnesses "
                "WHERE incident_id=?",
                ("incident-sequence-001",),
            )

        with self.assertRaises(ValueError):
            self.Journal.open(
                self.path,
                universe_id=WORLD,
            )

    def test_invalid_observed_cronenberg_rejected_on_open(self):
        incident_id = "incident-invalid-cronenberg"

        self.store.prepare(
            incident_id,
            "security_validation",
        )

        self.store.observe(
            incident_id,
            CRON_A,
            DIGEST_A,
        )

        with edit_database(self.path) as connection:
            connection.execute(
                "UPDATE publication_witnesses "
                "SET cronenberg_id='bad-cronenberg-id' "
                "WHERE incident_id=?",
                (incident_id,),
            )

        with self.assertRaises(ValueError):
            self.Journal.open(
                self.path,
                universe_id=WORLD,
            )

    def test_foreign_universe_history_rejected_on_open(self):
        incident_id = "incident-foreign-row"

        self.store.prepare(
            incident_id,
            "security_validation",
        )

        with edit_database(self.path) as connection:
            connection.execute(
                "UPDATE publication_witnesses "
                "SET universe_id='different_universe' "
                "WHERE incident_id=?",
                (incident_id,),
            )

        with self.assertRaises(ValueError):
            self.Journal.open(
                self.path,
                universe_id=WORLD,
            )

    def test_local_observations_and_metadata_are_untrusted(self):
        """Document existing limits, not a secure behavior."""

        path = self.path.parent / "untrusted.sqlite"

        limited = self.Journal.create(
            path,
            universe_id=WORLD,
            max_entries=1,
        )

        incident_id = "incident-unverified-claim"

        limited.prepare(
            incident_id,
            "security_validation",
        )

        # The journal cannot check whether this ID
        # refers to a real canonical Universe entity.
        limited.observe(
            incident_id,
            CRON_A,
            DIGEST_A,
        )

        self.assertFalse(
            limited.get(incident_id).is_authoritative
        )

        with self.assertRaises(ValueError):
            limited.prepare(
                "incident-over-limit",
                "security_validation",
            )

        # Deliberate demonstration of the documented
        # local-metadata tampering limitation.
        with edit_database(path) as connection:
            connection.execute(
                "UPDATE publication_witness_metadata "
                "SET max_entries=2 WHERE singleton_id=1"
            )

        reopened = self.Journal.open(
            path,
            universe_id=WORLD,
        )

        self.assertIs(
            reopened.prepare(
                "incident-over-limit",
                "security_validation",
            ),
            True,
        )

        self.assertFalse(
            reopened.get(incident_id).is_authoritative
        )

    def test_duplicate_historical_incident_identity_rejected_on_open(self):
        """EXPECTED RED: valid-looking duplicate history."""

        incident_id = "incident-duplicate-history"

        self.store.prepare(
            incident_id,
            "security_validation",
        )

        # Rebuild the local table without its uniqueness
        # constraints while preserving valid row shapes,
        # sequence values and SQLite quick_check.
        #
        # This is a malformed-schema diagnostic, not a
        # claim of resistance to arbitrary host attacks.
        with edit_database(self.path) as connection:
            connection.execute(
                "ALTER TABLE publication_witnesses "
                "RENAME TO witness_original"
            )

            connection.execute(
                "CREATE TABLE publication_witnesses ("
                "sequence INTEGER PRIMARY KEY AUTOINCREMENT, "
                "universe_id TEXT NOT NULL, "
                "incident_id TEXT NOT NULL, "
                "source_operation TEXT NOT NULL, "
                "phase TEXT NOT NULL, "
                "cronenberg_id TEXT, "
                "manifestation_digest TEXT)"
            )

            columns = (
                "sequence, universe_id, incident_id, "
                "source_operation, phase, cronenberg_id, "
                "manifestation_digest"
            )

            connection.execute(
                f"INSERT INTO publication_witnesses ({columns}) "
                f"SELECT {columns} FROM witness_original"
            )

            connection.execute(
                "DROP TABLE witness_original"
            )

            connection.execute(
                "INSERT INTO publication_witnesses "
                "(universe_id, incident_id, "
                "source_operation, phase, "
                "cronenberg_id, manifestation_digest) "
                "VALUES (?, ?, ?, 'prepared', NULL, NULL)",
                (
                    WORLD,
                    incident_id,
                    "security_validation",
                ),
            )

            self.assertEqual(
                connection.execute(
                    "PRAGMA quick_check"
                ).fetchone(),
                ("ok",),
            )

            self.assertEqual(
                connection.execute(
                    "SELECT seq FROM sqlite_sequence "
                    "WHERE name='publication_witnesses'"
                ).fetchone(),
                (2,),
            )

        # This should reject duplicate historical
        # incident identities, even when each row
        # separately passes field validation.
        with self.assertRaises(ValueError):
            self.Journal.open(
                self.path,
                universe_id=WORLD,
            )


    def test_duplicate_historical_cronenberg_identity_rejected_on_open(self):
        """Reject two distinct incidents bound to one Cronenberg ID."""

        first = "incident-duplicate-cronenberg-first"
        second = "incident-duplicate-cronenberg-second"

        self.store.prepare(first, "security_validation")
        self.store.prepare(second, "security_validation")

        self.store.observe(first, CRON_A, DIGEST_A)
        self.store.observe(second, CRON_B, DIGEST_B)

        # Remove database uniqueness constraints to simulate
        # malformed local schema with individually valid rows.
        with edit_database(self.path) as connection:
            connection.execute(
                "ALTER TABLE publication_witnesses "
                "RENAME TO witness_original"
            )

            connection.execute(
                "CREATE TABLE publication_witnesses ("
                "sequence INTEGER PRIMARY KEY AUTOINCREMENT, "
                "universe_id TEXT NOT NULL, "
                "incident_id TEXT NOT NULL, "
                "source_operation TEXT NOT NULL, "
                "phase TEXT NOT NULL, "
                "cronenberg_id TEXT, "
                "manifestation_digest TEXT)"
            )

            columns = (
                "sequence, universe_id, incident_id, "
                "source_operation, phase, cronenberg_id, "
                "manifestation_digest"
            )

            connection.execute(
                f"INSERT INTO publication_witnesses ({columns}) "
                f"SELECT {columns} FROM witness_original"
            )

            connection.execute("DROP TABLE witness_original")

            connection.execute(
                "UPDATE publication_witnesses "
                "SET cronenberg_id=? WHERE incident_id=?",
                (CRON_A, second),
            )

            self.assertEqual(
                connection.execute(
                    "PRAGMA quick_check"
                ).fetchone(),
                ("ok",),
            )

            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM publication_witnesses "
                    "WHERE cronenberg_id=?",
                    (CRON_A,),
                ).fetchone(),
                (2,),
            )

        with self.assertRaises(ValueError):
            self.Journal.open(
                self.path,
                universe_id=WORLD,
            )

if __name__ == "__main__":
    unittest.main()
