"""Read-only reconciliation audit for the durable History journal.

Classification is not permission to rerun an action or change a reservation.
A completed archive proves a persisted history record, not an external effect.
"""

import os
import sqlite3

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from pathlib import Path

from .history_record_snapshot import (
    RestoredHistoryRecord,
    decode_snapshot,
)


class ReconciliationFinding(str, Enum):
    ARCHIVED_COMPLETED = "archived_completed"
    HOLD_UNKNOWN_OUTCOME = "hold_unknown_outcome"
    HOLD_MISSING_SNAPSHOT = "hold_missing_snapshot"
    HOLD_INVALID_SNAPSHOT = "hold_invalid_snapshot"
    HOLD_UNCOMPLETED_SNAPSHOT = "hold_uncompleted_snapshot"
    HOLD_ORPHAN_SNAPSHOT = "hold_orphan_snapshot"
    HOLD_UNKNOWN_STATUS = "hold_unknown_status"


@dataclass(frozen=True, slots=True)
class ReconciliationAuditEntry:
    cycle_id: str
    branch_id: str
    journal_status: str
    finding: ReconciliationFinding
    snapshot_sha256: str | None = None

    @property
    def retry_allowed(self):
        # Evidence classification never authorizes an action.
        return False


def _fingerprint(payload):
    if type(payload) is not str:
        return None

    return sha256(payload.encode("utf-8")).hexdigest()


def _classify(cycle_id, branch_id, status, present, payload):
    fingerprint = _fingerprint(payload) if present else None

    if status == "completed":
        if not present:
            finding = ReconciliationFinding.HOLD_MISSING_SNAPSHOT
        else:
            try:
                if type(payload) is not str:
                    raise ValueError("Invalid snapshot payload.")

                state = decode_snapshot(payload)
                record = RestoredHistoryRecord(state)

                if (
                    record.cycle_id != cycle_id
                    or record.branch_id != branch_id
                ):
                    raise ValueError(
                        "History snapshot identity mismatch."
                    )

            except (TypeError, ValueError, OverflowError, RecursionError):
                finding = ReconciliationFinding.HOLD_INVALID_SNAPSHOT
            else:
                finding = ReconciliationFinding.ARCHIVED_COMPLETED

    elif status in ("running", "in_doubt"):
        finding = (
            ReconciliationFinding.HOLD_UNCOMPLETED_SNAPSHOT
            if present
            else ReconciliationFinding.HOLD_UNKNOWN_OUTCOME
        )

    else:
        finding = ReconciliationFinding.HOLD_UNKNOWN_STATUS

    return ReconciliationAuditEntry(
        cycle_id=cycle_id,
        branch_id=branch_id,
        journal_status=status,
        finding=finding,
        snapshot_sha256=fingerprint,
    )


def audit_history_database(path):
    """Inspect one consistent SQLite snapshot without writing to it.

    Never creates missing databases/tables and never mutates attempt status.
    Returns immutable findings; no case grants retry permission.
    """

    if not isinstance(path, (str, os.PathLike)):
        raise TypeError("Audit database path must be a filesystem path.")

    path = Path(path)

    if not path.is_absolute():
        raise ValueError("Audit database path must be absolute.")

    if not path.is_file():
        raise FileNotFoundError(
            "Audit requires an existing SQLite database."
        )

    # as_uri() encodes Windows drives, spaces and special characters.
    # mode=ro prevents SQLite from creating or changing the database.
    connection = sqlite3.connect(
        path.as_uri() + "?mode=ro",
        uri=True,
        timeout=30.0,
    )

    try:
        connection.execute("PRAGMA query_only = ON")
        connection.execute("BEGIN")

        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' "
                "AND name IN "
                "('history_attempts', 'history_record_snapshots')"
            )
        }

        if "history_attempts" not in tables:
            raise RuntimeError(
                "History attempt journal table is missing."
            )

        attempts = connection.execute(
            "SELECT cycle_id, branch_id, status "
            "FROM history_attempts ORDER BY rowid"
        ).fetchall()

        if "history_record_snapshots" in tables:
            snapshot_rows = connection.execute(
                "SELECT cycle_id, branch_id, snapshot_json "
                "FROM history_record_snapshots "
                "ORDER BY rowid"
            ).fetchall()
        else:
            # Legacy journal-only database.
            snapshot_rows = []

        connection.rollback()

    finally:
        connection.close()

    snapshots = {
        (cycle_id, branch_id): payload
        for cycle_id, branch_id, payload in snapshot_rows
    }

    if len(snapshots) != len(snapshot_rows):
        raise RuntimeError(
            "Duplicate history snapshot identities."
        )

    findings = []

    for cycle_id, branch_id, status in attempts:
        key = (cycle_id, branch_id)
        present = key in snapshots
        payload = snapshots.pop(key, None)

        findings.append(
            _classify(
                cycle_id,
                branch_id,
                status,
                present,
                payload,
            )
        )

    # Orphan snapshots must not be treated as completed attempts.
    for cycle_id, branch_id in sorted(snapshots):
        findings.append(
            ReconciliationAuditEntry(
                cycle_id=cycle_id,
                branch_id=branch_id,
                journal_status="missing",
                finding=ReconciliationFinding.HOLD_ORPHAN_SNAPSHOT,
                snapshot_sha256=_fingerprint(
                    snapshots[(cycle_id, branch_id)]
                ),
            )
        )

    return tuple(findings)
