import os
import sqlite3

from contextlib import contextmanager
from dataclasses import replace

from .history_attempt_state import (
    HistoryAttempt,
    HistoryAttemptStatus,
)


class SQLiteHistoryAttemptJournal:
    """Durable attempt reservations, not durable History records."""

    def __init__(self, path):
        if not isinstance(path, (str, os.PathLike)):
            raise TypeError(
                "Journal path must be a filesystem path."
            )

        self.path = os.fspath(path)

        if not self.path or not os.path.isabs(self.path):
            raise ValueError(
                "Journal path must be absolute."
            )

        with self._connection() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS history_attempts ("
                "cycle_id TEXT NOT NULL, "
                "branch_id TEXT NOT NULL, "
                "status TEXT NOT NULL "
                "CHECK (status IN "
                "('running', 'in_doubt', 'completed')), "
                "PRIMARY KEY (cycle_id, branch_id))"
            )
            connection.commit()

    @contextmanager
    def _connection(self):
        connection = sqlite3.connect(
            self.path,
            timeout=30.0,
        )

        try:
            yield connection
        finally:
            connection.close()

    @staticmethod
    def _key(cycle_id, branch_id):
        if not isinstance(cycle_id, str) or not cycle_id:
            raise TypeError(
                "Durable cycle_id must be a non-empty string."
            )

        if not isinstance(branch_id, str) or not branch_id:
            raise TypeError(
                "Durable branch_id must be a non-empty string."
            )

        return cycle_id, branch_id

    def _status(self, cycle_id, branch_id):
        with self._connection() as connection:
            row = connection.execute(
                "SELECT status FROM history_attempts "
                "WHERE cycle_id = ? AND branch_id = ?",
                (cycle_id, branch_id),
            ).fetchone()

        return (
            HistoryAttemptStatus(row[0])
            if row is not None
            else None
        )

    def begin_attempt(self, cycle_id, branch_id="root"):
        cycle_id, branch_id = self._key(
            cycle_id,
            branch_id,
        )

        try:
            with self._connection() as connection:
                connection.execute(
                    "INSERT INTO history_attempts "
                    "(cycle_id, branch_id, status) "
                    "VALUES (?, ?, ?)",
                    (
                        cycle_id,
                        branch_id,
                        HistoryAttemptStatus.RUNNING.value,
                    ),
                )
                connection.commit()

        except sqlite3.IntegrityError:
            if (
                self._status(cycle_id, branch_id)
                is HistoryAttemptStatus.COMPLETED
            ):
                raise ValueError(
                    "Cycle is already recorded "
                    "in this history branch."
                ) from None

            raise RuntimeError(
                "Cycle attempt is in doubt or still running; "
                "manual reconciliation required."
            ) from None

        return HistoryAttempt(
            cycle_id=cycle_id,
            branch_id=branch_id,
            status=HistoryAttemptStatus.RUNNING,
        )

    def find_attempt(self, cycle_id, branch_id="root"):
        cycle_id, branch_id = self._key(
            cycle_id,
            branch_id,
        )

        status = self._status(cycle_id, branch_id)

        if status not in (
            HistoryAttemptStatus.RUNNING,
            HistoryAttemptStatus.IN_DOUBT,
        ):
            return None

        return HistoryAttempt(
            cycle_id=cycle_id,
            branch_id=branch_id,
            status=status,
        )

    def unresolved_attempts(self):
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT cycle_id, branch_id, status "
                "FROM history_attempts "
                "WHERE status IN ('running', 'in_doubt') "
                "ORDER BY rowid"
            ).fetchall()

        return tuple(
            HistoryAttempt(
                cycle_id=cycle_id,
                branch_id=branch_id,
                status=HistoryAttemptStatus(status),
            )
            for cycle_id, branch_id, status in rows
        )

    def mark_attempt_in_doubt(self, attempt):
        cycle_id, branch_id = self._key(
            attempt.cycle_id,
            attempt.branch_id,
        )

        with self._connection() as connection:
            cursor = connection.execute(
                "UPDATE history_attempts SET status = ? "
                "WHERE cycle_id = ? AND branch_id = ? "
                "AND status = ?",
                (
                    HistoryAttemptStatus.IN_DOUBT.value,
                    cycle_id,
                    branch_id,
                    HistoryAttemptStatus.RUNNING.value,
                ),
            )

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "Unknown or non-running history attempt."
                )

            connection.commit()

        return replace(
            attempt,
            status=HistoryAttemptStatus.IN_DOUBT,
        )

    def complete_attempt(self, attempt):
        cycle_id, branch_id = self._key(
            attempt.cycle_id,
            attempt.branch_id,
        )

        with self._connection() as connection:
            cursor = connection.execute(
                "UPDATE history_attempts "
                "SET status = 'completed' "
                "WHERE cycle_id = ? AND branch_id = ? "
                "AND status = 'running'",
                (cycle_id, branch_id),
            )

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "Unknown or non-running history attempt."
                )

            connection.commit()
