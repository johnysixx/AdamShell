"""Atomic SQLite publication of data-only history records."""

from .history_record_snapshot import (
    RestoredHistoryRecord,
    encode_snapshot,
    decode_snapshot,
)


class SQLiteHistoryRecordArchive:

    def __init__(self, journal):
        self.journal = journal

        with journal._connection() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS "
                "history_record_snapshots ("
                "cycle_id TEXT NOT NULL, "
                "branch_id TEXT NOT NULL, "
                "snapshot_json TEXT NOT NULL, "
                "PRIMARY KEY (cycle_id, branch_id))"
            )
            connection.commit()

    def load_records(self):
        with self.journal._connection() as connection:
            rows = connection.execute(
                "SELECT a.cycle_id, a.branch_id, "
                "a.status, s.snapshot_json "
                "FROM history_attempts AS a "
                "LEFT JOIN history_record_snapshots AS s "
                "ON a.cycle_id = s.cycle_id "
                "AND a.branch_id = s.branch_id "
                "ORDER BY a.rowid"
            ).fetchall()

            orphan_count = connection.execute(
                "SELECT COUNT(*) "
                "FROM history_record_snapshots AS s "
                "LEFT JOIN history_attempts AS a "
                "ON a.cycle_id = s.cycle_id "
                "AND a.branch_id = s.branch_id "
                "WHERE a.cycle_id IS NULL"
            ).fetchone()[0]

        if orphan_count:
            raise RuntimeError(
                "History archive has orphan snapshots."
            )

        restored = []

        for cycle_id, branch_id, status, payload in rows:
            if status == "completed":
                if payload is None:
                    raise RuntimeError(
                        "Completed history attempt lacks "
                        "a durable record snapshot."
                    )

                record = RestoredHistoryRecord(
                    decode_snapshot(payload)
                )

                if (
                    record.cycle_id != cycle_id
                    or record.branch_id != branch_id
                ):
                    raise RuntimeError(
                        "History snapshot identity mismatch."
                    )

                restored.append(record)

            elif payload is not None:
                raise RuntimeError(
                    "Uncompleted history attempt "
                    "has a record snapshot."
                )

        return restored

    def complete_attempt(self, attempt, record):
        if (
            attempt.cycle_id != record.cycle_id
            or attempt.branch_id != record.branch_id
        ):
            raise RuntimeError(
                "History attempt/record identity mismatch."
            )

        # Validate and encode before opening the write transaction.
        # Unsupported objects never become durable COMPLETED records.
        snapshot_json = encode_snapshot(
            record.public_state
        )

        with self.journal._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")

            status = connection.execute(
                "SELECT status FROM history_attempts "
                "WHERE cycle_id = ? AND branch_id = ?",
                (attempt.cycle_id, attempt.branch_id),
            ).fetchone()

            if status != ("running",):
                raise RuntimeError(
                    "Unknown or non-running history attempt."
                )

            connection.execute(
                "INSERT INTO history_record_snapshots "
                "(cycle_id, branch_id, snapshot_json) "
                "VALUES (?, ?, ?)",
                (
                    attempt.cycle_id,
                    attempt.branch_id,
                    snapshot_json,
                ),
            )

            cursor = connection.execute(
                "UPDATE history_attempts "
                "SET status = 'completed' "
                "WHERE cycle_id = ? AND branch_id = ? "
                "AND status = 'running'",
                (attempt.cycle_id, attempt.branch_id),
            )

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "History attempt changed during publication."
                )

            connection.commit()
