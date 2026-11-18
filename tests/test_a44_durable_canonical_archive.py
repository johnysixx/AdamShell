"""A44 durable canonical evidence archive ? EXPECTED RED.

The archive stores a bounded, detached, local projection
captured from an already existing canonical Universe triad.

It is NOT a full restorable Cronenberg checkpoint.
Its SQLite history is not authenticated or rollback-proof.
A parsed archived projection is never authoritative.
No missing entity may be created from archived data.
"""

import hashlib
import importlib
import io
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, redirect_stdout
from pathlib import Path

from core.existence.history_receipt_trust_attack_cronenberg import (
    SecurityAttackDetected,
)

from core.existence.history_receipt_trust_canonical_recovery import (
    CanonicalSecurityPublicationEvidence,
)

from core.existence.history_receipt_trust_incident_cronenberg_reconciliation import (
    SecurityIncidentCronenbergReconciler,
)

from core.existence.history_receipt_trust_incident_outbox import (
    LocalDurableSecurityIncidentOutbox,
)

from core.existence.history_receipt_trust_publication_witness import (
    LocalDurablePublicationWitnessJournal,
)

from universe.universe import Universe


MODULE = (
    "core.existence."
    "history_receipt_trust_canonical_archive"
)

WORLD = "a44_666_canonical_archive"
OPERATION = "security_validation"
INCIDENT = "incident-canonical-archive"


def canonical_digest(payload):
    body = {
        key: value
        for key, value in payload.items()
        if key != "projection_sha256"
    }

    encoded = json.dumps(
        body,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


class A44DurableCanonicalArchiveContractTests(
    unittest.TestCase
):

    def setUp(self):
        implementation = importlib.import_module(MODULE)

        self.Archive = (
            implementation.LocalDurableCanonicalEvidenceArchive
        )

        directory = tempfile.TemporaryDirectory(
            prefix="a44_666_archive_contract_"
        )

        self.addCleanup(directory.cleanup)

        self.root = Path(directory.name)
        self.path = self.root / "archive.sqlite"

        self.store = self.Archive.create(
            self.path,
            universe_id=WORLD,
            max_entries=4,
        )

        self.outbox = LocalDurableSecurityIncidentOutbox.create(
            self.root / "outbox.sqlite",
            max_pending=8,
            max_total=16,
        )

        with redirect_stdout(io.StringIO()):
            self.world = Universe(universe_id=WORLD)

    def publish(self, incident_id=INCIDENT):
        coordinator = SecurityIncidentCronenbergReconciler(
            universe=self.world,
            outbox=self.outbox,
        )

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SecurityAttackDetected):
                coordinator.reject(
                    incident_id=incident_id,
                    source_operation=OPERATION,
                    attack=SecurityAttackDetected(
                        "archive contract rejection"
                    ),
                )

    def capture(
        self,
        incident_id=INCIDENT,
        *,
        store=None,
        world=None,
        operation=OPERATION,
    ):
        target = self.store if store is None else store
        universe = self.world if world is None else world

        return target.capture_live(
            universe=universe,
            incident_id=incident_id,
            source_operation=operation,
        )

    def test_exclusive_creation_and_reopen(self):
        with self.assertRaises(ValueError):
            self.Archive.create(
                self.path,
                universe_id=WORLD,
                max_entries=4,
            )

        reopened = self.Archive.open(
            self.path,
            universe_id=WORLD,
        )

        self.assertIsNone(
            reopened.get_untrusted(INCIDENT)
        )

        self.assertEqual(
            reopened.incident_ids(),
            (),
        )

    def test_missing_and_foreign_universe_denied(self):
        with self.assertRaises(ValueError):
            self.Archive.open(
                self.root / "missing.sqlite",
                universe_id=WORLD,
            )

        with self.assertRaises(ValueError):
            self.Archive.open(
                self.path,
                universe_id="foreign_world",
            )

        with self.assertRaises(ValueError):
            self.Archive.create(
                self.root / "invalid.sqlite",
                universe_id="",
                max_entries=4,
            )

    def test_capture_live_detached_untrusted_evidence(self):
        self.publish()

        before = (
            len(self.world.cronenbergs),
            len(self.world.entities),
            len(self.world.quantum_events),
        )

        expected = CanonicalSecurityPublicationEvidence.capture(
            universe=self.world,
            incident_id=INCIDENT,
            source_operation=OPERATION,
        )

        self.assertIs(
            self.capture(),
            True,
        )

        archived = self.store.get_untrusted(INCIDENT)

        self.assertIsInstance(
            archived,
            CanonicalSecurityPublicationEvidence,
        )

        self.assertEqual(
            archived.to_dict(),
            expected.to_dict(),
        )

        self.assertFalse(archived.is_authoritative)
        self.assertFalse(archived.is_restorable)

        self.assertTrue(
            archived.verify_live(self.world)
        )

        after = (
            len(self.world.cronenbergs),
            len(self.world.entities),
            len(self.world.quantum_events),
        )

        self.assertEqual(before, after)

    def test_idempotent_capture_preserves_one_identity(self):
        self.publish()

        self.assertIs(self.capture(), True)
        self.assertIs(self.capture(), False)

        self.assertEqual(
            self.store.incident_ids(),
            (INCIDENT,),
        )

        reopened = self.Archive.open(
            self.path,
            universe_id=WORLD,
        )

        self.assertEqual(
            reopened.incident_ids(),
            (INCIDENT,),
        )

    def test_local_witness_cannot_substitute_for_live_triad(self):
        witness = LocalDurablePublicationWitnessJournal.create(
            self.root / "witness.sqlite",
            universe_id=WORLD,
            max_entries=4,
        )

        self.assertTrue(
            witness.prepare(INCIDENT, OPERATION)
        )

        self.assertTrue(
            witness.observe(
                INCIDENT,
                "cronenberg_deadbeef",
                "a" * 64,
            )
        )

        self.assertFalse(
            witness.get(INCIDENT).is_authoritative
        )

        with self.assertRaises(ValueError):
            self.capture()

        self.assertEqual(
            self.store.incident_ids(),
            (),
        )

        self.assertEqual(
            len(self.world.cronenbergs),
            0,
        )

    def test_foreign_universe_and_operation_conflict_denied(self):
        self.publish()

        with redirect_stdout(io.StringIO()):
            foreign = Universe(
                universe_id="a44_foreign_archive"
            )

        with self.assertRaises(ValueError):
            self.capture(world=foreign)

        with self.assertRaises(ValueError):
            self.capture(operation="receipt_signature")

        self.assertEqual(
            self.store.incident_ids(),
            (),
        )

    def test_bounded_capacity_retains_history(self):
        limited = self.Archive.create(
            self.root / "limited.sqlite",
            universe_id=WORLD,
            max_entries=2,
        )

        ids = (
            "incident-capacity-01",
            "incident-capacity-02",
            "incident-capacity-03",
        )

        for incident_id in ids:
            self.publish(incident_id)

        self.assertTrue(
            self.capture(ids[0], store=limited)
        )

        self.assertTrue(
            self.capture(ids[1], store=limited)
        )

        with self.assertRaises(ValueError):
            self.capture(ids[2], store=limited)

        self.assertEqual(
            limited.incident_ids(),
            ids[:2],
        )

        reopened = self.Archive.open(
            self.root / "limited.sqlite",
            universe_id=WORLD,
        )

        self.assertEqual(
            reopened.incident_ids(),
            ids[:2],
        )

    def test_fifo_incident_ids_and_limit_validation(self):
        first = "incident-fifo-01"
        second = "incident-fifo-02"

        self.publish(first)
        self.publish(second)

        self.capture(first)
        self.capture(second)

        self.assertEqual(
            self.store.incident_ids(limit=1),
            (first,),
        )

        self.assertEqual(
            self.store.incident_ids(limit=2),
            (first, second),
        )

        for invalid in (0, 257, True, "1"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    self.store.incident_ids(limit=invalid)

    def test_cross_process_reopen_preserves_data(self):
        self.publish()
        self.capture()

        child = r"""
import json
import sys

from core.existence.history_receipt_trust_canonical_archive import (
    LocalDurableCanonicalEvidenceArchive,
)

path, universe_id, incident_id = sys.argv[1:]

archive = LocalDurableCanonicalEvidenceArchive.open(
    path,
    universe_id=universe_id,
)

evidence = archive.get_untrusted(incident_id)

print(json.dumps({
    "incident_id": evidence.incident_id,
    "cronenberg_id": evidence.cronenberg_id,
    "authoritative": evidence.is_authoritative,
    "restorable": evidence.is_restorable,
}, sort_keys=True))
"""

        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                child,
                str(self.path),
                WORLD,
                INCIDENT,
            ],
            cwd=str(Path.cwd()),
            capture_output=True,
            text=True,
            timeout=45,
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=result.stderr,
        )

        report = json.loads(
            result.stdout.strip()
        )

        self.assertEqual(
            report["incident_id"],
            INCIDENT,
        )

        self.assertEqual(
            report["cronenberg_id"],
            self.world.cronenbergs[0].id,
        )

        self.assertFalse(report["authoritative"])
        self.assertFalse(report["restorable"])

    def test_corrupt_stored_projection_rejected_on_open(self):
        self.publish()
        self.capture()

        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(
                "UPDATE canonical_evidence_records "
                "SET payload_json=? "
                "WHERE incident_id=?",
                ("{broken-json", INCIDENT),
            )

            self.assertEqual(
                connection.execute(
                    "PRAGMA quick_check"
                ).fetchone(),
                ("ok",),
            )

        with self.assertRaises(ValueError):
            self.Archive.open(
                self.path,
                universe_id=WORLD,
            )

    def test_rehashed_modified_projection_has_no_authority(self):
        self.publish()
        self.capture()

        original = self.store.get_untrusted(
            INCIDENT
        ).to_dict()

        changed = json.loads(
            json.dumps(original)
        )

        changed["manifestation"]["quantum_tick"] += 1

        changed["projection_sha256"] = (
            canonical_digest(changed)
        )

        # A correctly rehashed local claim may be
        # structurally valid. It is still not trusted.
        parsed = CanonicalSecurityPublicationEvidence.parse_untrusted(
            changed
        )

        self.assertFalse(parsed.is_authoritative)
        self.assertFalse(parsed.is_restorable)

        with self.assertRaises(ValueError):
            parsed.verify_live(self.world)

        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(
                "UPDATE canonical_evidence_records "
                "SET payload_json=? "
                "WHERE incident_id=?",
                (
                    json.dumps(
                        changed,
                        sort_keys=True,
                        ensure_ascii=True,
                        separators=(",", ":"),
                    ),
                    INCIDENT,
                ),
            )

        # An archive may reject modified local content.
        # If it accepts a structurally consistent claim,
        # that claim must remain non-authoritative.
        try:
            reopened = self.Archive.open(
                self.path,
                universe_id=WORLD,
            )

        except ValueError:
            pass

        else:
            recovered = reopened.get_untrusted(
                INCIDENT
            )

            self.assertFalse(
                recovered.is_authoritative
            )

            self.assertFalse(
                recovered.is_restorable
            )

            with self.assertRaises(ValueError):
                recovered.verify_live(
                    self.world
                )

        self.assertEqual(
            len(self.world.cronenbergs),
            1,
        )

    def test_parallel_same_incident_capture_idempotent(self):
        """Concurrent archive writes; no Universe mutation."""

        self.publish()

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(
                pool.map(
                    lambda _: self.capture(),
                    range(6),
                )
            )

        self.assertEqual(
            results.count(True),
            1,
        )

        self.assertEqual(
            results.count(False),
            5,
        )

        self.assertEqual(
            self.store.incident_ids(),
            (INCIDENT,),
        )

        archived = self.store.get_untrusted(INCIDENT)

        self.assertTrue(
            archived.verify_live(self.world)
        )


if __name__ == "__main__":
    unittest.main()
