"""A44 durable publication witness journal contract.

EXPECTED RED until the witness journal module exists.

The journal is a local persistent record of:
- PREPARED: the publication attempt was registered.
- OBSERVED: a process asserted a Cronenberg ID and digest.

OBSERVED is NOT an independently verified manifestation.
It cannot, by itself, authorize replay, restore a Cronenberg,
or prove that canonical Universe state survived a restart.

The journal must provide:
- Exclusive creation and strict Universe identity binding.
- Typed immutable records.
- Idempotent preparation and observation.
- Rejection of conflicting identities and observations.
- Bounded total history, including observed entries.
- Restart persistence across real Python processes.
- Historical format validation on open.

Whole-file rollback, local tampering with valid records,
cross-process exactly-once, trusted attestation, and durable
Universe reconstruction are NOT established by this contract.

Only temporary SQLite databases are used.
"""

import dataclasses
import importlib
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from pathlib import Path


MODULE = (
    "core.existence."
    "history_receipt_trust_publication_witness"
)

UNIVERSE_ID = "a44_witness_test_universe"

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64

CRONENBERG_A = "cronenberg_deadbeef"
CRONENBERG_B = "cronenberg_1234abcd"


class A44DurablePublicationWitnessTests(unittest.TestCase):

    def setUp(self):
        directory = tempfile.TemporaryDirectory(
            prefix="a44_durable_witness_"
        )

        self.addCleanup(directory.cleanup)

        self.path = (
            Path(directory.name) / "witness.sqlite"
        )

        implementation = importlib.import_module(MODULE)

        self.Journal = (
            implementation.LocalDurablePublicationWitnessJournal
        )

        self.Record = (
            implementation.PublicationWitnessRecord
        )

        self.Phase = (
            implementation.PublicationWitnessPhase
        )

        self.store = self.Journal.create(
            self.path,
            universe_id=UNIVERSE_ID,
            max_entries=16,
        )

    def test_exclusive_creation_and_reopen(self):
        with self.assertRaises(ValueError):
            self.Journal.create(
                self.path,
                universe_id=UNIVERSE_ID,
                max_entries=16,
            )

        reopened = self.Journal.open(
            self.path,
            universe_id=UNIVERSE_ID,
        )

        self.assertIsNone(
            reopened.get("incident-not-recorded")
        )

        self.assertEqual(reopened.pending(), ())

    def test_foreign_universe_and_missing_storage_fail_closed(self):
        with self.assertRaises(ValueError):
            self.Journal.open(
                self.path,
                universe_id="foreign_universe",
            )

        with self.assertRaises(ValueError):
            self.Journal.open(
                self.path.parent / "missing.sqlite",
                universe_id=UNIVERSE_ID,
            )

        with self.assertRaises(ValueError):
            self.Journal.create(
                self.path.parent / "invalid.sqlite",
                universe_id="",
            )

    def test_prepare_creates_immutable_unverified_record(self):
        self.assertIs(
            self.store.prepare(
                "incident-prepare-001",
                "security_validation",
            ),
            True,
        )

        record = self.store.get(
            "incident-prepare-001"
        )

        self.assertIs(type(record), self.Record)

        self.assertEqual(
            record.universe_id,
            UNIVERSE_ID,
        )

        self.assertEqual(
            record.incident_id,
            "incident-prepare-001",
        )

        self.assertEqual(
            record.source_operation,
            "security_validation",
        )

        self.assertIs(
            record.phase,
            self.Phase.PREPARED,
        )

        self.assertIsNone(record.cronenberg_id)
        self.assertIsNone(record.manifestation_digest)

        self.assertIs(
            record.is_authoritative,
            False,
            "Local journal must never claim trust authority.",
        )

        with self.assertRaises(
            dataclasses.FrozenInstanceError
        ):
            record.incident_id = "changed"

    def test_prepare_replay_and_operation_conflict(self):
        incident_id = "incident-replayed-prepare"

        self.assertIs(
            self.store.prepare(
                incident_id,
                "security_validation",
            ),
            True,
        )

        self.assertIs(
            self.store.prepare(
                incident_id,
                "security_validation",
            ),
            False,
        )

        with self.assertRaises(ValueError):
            self.store.prepare(
                incident_id,
                "authority_reply",
            )

        self.assertEqual(
            self.store.get(incident_id).source_operation,
            "security_validation",
        )

    def test_observation_is_idempotent_but_unverified(self):
        incident_id = "incident-observed-001"

        self.store.prepare(
            incident_id,
            "security_validation",
        )

        self.assertIs(
            self.store.observe(
                incident_id,
                CRONENBERG_A,
                DIGEST_A,
            ),
            True,
        )

        self.assertIs(
            self.store.observe(
                incident_id,
                CRONENBERG_A,
                DIGEST_A,
            ),
            False,
        )

        record = self.store.get(incident_id)

        self.assertIs(
            record.phase,
            self.Phase.OBSERVED,
        )

        self.assertEqual(
            record.cronenberg_id,
            CRONENBERG_A,
        )

        self.assertEqual(
            record.manifestation_digest,
            DIGEST_A,
        )

        self.assertIs(
            record.is_authoritative,
            False,
            "Observed local data is not publication proof.",
        )

        self.assertEqual(self.store.pending(), ())

    def test_conflicting_observations_and_reused_identity_denied(self):
        first_id = "incident-observation-first"
        second_id = "incident-observation-second"

        self.store.prepare(
            first_id,
            "security_validation",
        )

        self.store.prepare(
            second_id,
            "security_validation",
        )

        self.store.observe(
            first_id,
            CRONENBERG_A,
            DIGEST_A,
        )

        for cronenberg_id, digest in (
            (CRONENBERG_B, DIGEST_A),
            (CRONENBERG_A, DIGEST_B),
        ):
            with self.subTest(
                cronenberg_id=cronenberg_id,
                digest=digest,
            ):
                with self.assertRaises(ValueError):
                    self.store.observe(
                        first_id,
                        cronenberg_id,
                        digest,
                    )

        with self.assertRaises(ValueError):
            self.store.observe(
                second_id,
                CRONENBERG_A,
                DIGEST_A,
            )

        self.assertIs(
            self.store.get(second_id).phase,
            self.Phase.PREPARED,
        )

    def test_observation_without_preparation_denied(self):
        incident_id = "incident-never-prepared"

        with self.assertRaises(ValueError):
            self.store.observe(
                incident_id,
                CRONENBERG_A,
                DIGEST_A,
            )

        self.assertIsNone(
            self.store.get(incident_id)
        )

    def test_invalid_identifiers_and_digests_fail_closed(self):
        for invalid in (
            None,
            "",
            "../incident",
            "bad/incident",
            "x" * 129,
            True,
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    self.store.prepare(
                        invalid,
                        "security_validation",
                    )

        with self.assertRaises(ValueError):
            self.store.prepare(
                "incident-unknown-operation",
                "unknown_operation",
            )

        incident_id = "incident-invalid-observation"

        self.store.prepare(
            incident_id,
            "security_validation",
        )

        for cronenberg_id, digest in (
            ("wrong_id", DIGEST_A),
            (CRONENBERG_A, "bad-digest"),
            (CRONENBERG_A, DIGEST_A.upper()),
            (CRONENBERG_A, None),
        ):
            with self.subTest(
                cronenberg_id=cronenberg_id,
                digest=digest,
            ):
                with self.assertRaises(ValueError):
                    self.store.observe(
                        incident_id,
                        cronenberg_id,
                        digest,
                    )

        self.assertIs(
            self.store.get(incident_id).phase,
            self.Phase.PREPARED,
        )

    def test_total_capacity_includes_observed_history(self):
        limited = self.Journal.create(
            self.path.parent / "limited.sqlite",
            universe_id=UNIVERSE_ID,
            max_entries=2,
        )

        for index, cronenberg_id, digest in (
            (1, CRONENBERG_A, DIGEST_A),
            (2, CRONENBERG_B, DIGEST_B),
        ):
            incident_id = f"incident-capacity-{index}"

            self.assertIs(
                limited.prepare(
                    incident_id,
                    "security_validation",
                ),
                True,
            )

            self.assertIs(
                limited.observe(
                    incident_id,
                    cronenberg_id,
                    digest,
                ),
                True,
            )

        self.assertEqual(limited.pending(), ())

        with self.assertRaises(ValueError):
            limited.prepare(
                "incident-capacity-third",
                "security_validation",
            )

        self.assertIsNone(
            limited.get("incident-capacity-third")
        )

    def test_pending_fifo_excludes_observed_entries(self):
        incident_ids = (
            "incident-fifo-001",
            "incident-fifo-002",
            "incident-fifo-003",
        )

        for incident_id in incident_ids:
            self.store.prepare(
                incident_id,
                "security_validation",
            )

        self.store.observe(
            incident_ids[1],
            CRONENBERG_A,
            DIGEST_A,
        )

        self.assertEqual(
            tuple(
                entry.incident_id
                for entry in self.store.pending(limit=2)
            ),
            (
                incident_ids[0],
                incident_ids[2],
            ),
        )

        self.assertEqual(
            tuple(
                entry.incident_id
                for entry in self.store.pending(limit=1)
            ),
            (incident_ids[0],),
        )

    def test_prepare_and_observe_survive_separate_processes(self):
        incident_id = "incident-child-process"

        child = r"""
import sys

from core.existence.history_receipt_trust_publication_witness import (
    LocalDurablePublicationWitnessJournal,
)

database, mode = sys.argv[1:]

store = LocalDurablePublicationWitnessJournal.open(
    database,
    universe_id="a44_witness_test_universe",
)

if mode == "prepare":
    assert store.prepare(
        "incident-child-process",
        "security_validation",
    ) is True

elif mode == "observe":
    assert store.observe(
        "incident-child-process",
        "cronenberg_deadbeef",
        "a" * 64,
    ) is True

else:
    raise AssertionError("Unknown child mode.")
"""

        for mode in ("prepare", "observe"):
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-c",
                    child,
                    str(self.path),
                    mode,
                ],
                cwd=str(Path.cwd()),
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.assertEqual(
                completed.returncode,
                0,
                completed.stdout + completed.stderr,
            )

            reopened = self.Journal.open(
                self.path,
                universe_id=UNIVERSE_ID,
            )

            expected_phase = (
                self.Phase.PREPARED
                if mode == "prepare"
                else self.Phase.OBSERVED
            )

            self.assertIs(
                reopened.get(incident_id).phase,
                expected_phase,
            )

        self.assertIs(
            self.store.get(incident_id).is_authoritative,
            False,
        )

    def test_corrupt_observed_history_rejected_on_open(self):
        incident_id = "incident-corrupt-history"

        self.store.prepare(
            incident_id,
            "security_validation",
        )

        self.store.observe(
            incident_id,
            CRONENBERG_A,
            DIGEST_A,
        )

        # Direct SQLite mutation simulates a malformed
        # historical claim. This checks structural
        # validation, NOT malicious tamper resistance.

        connection = sqlite3.connect(self.path)

        try:
            connection.execute(
                "UPDATE publication_witnesses "
                "SET manifestation_digest=? "
                "WHERE incident_id=?",
                (
                    "not-a-valid-digest",
                    incident_id,
                ),
            )

            connection.commit()

        finally:
            connection.close()

        with self.assertRaises(ValueError):
            self.Journal.open(
                self.path,
                universe_id=UNIVERSE_ID,
            )


if __name__ == "__main__":
    unittest.main()
