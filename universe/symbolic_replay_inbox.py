"""Durable, single-writer inbox for symbolic replay messages.

The receiver's effect is its immutable receipt ledger, stored
with message identities in one checkpoint. Arbitrary external
side effects are not made transactional by this module.
"""

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from universe.symbolic_replay_outbox import (
    SymbolicReplayOutboxEvent,
)
from universe.symbolic_replay_file_lock import (
    exclusive_inbox_lock,
)

_FORMAT = "adamshell.symbolic_replay_inbox"
_VERSION = 1


@dataclass(frozen=True, slots=True)
class SymbolicReplayInboxReceipt:
    id: str
    word_id: str
    sequence: int
    message: str

    def __post_init__(self):
        if type(self.id) is not str or not self.id:
            raise ValueError("Inbox receipt requires event ID.")

        if type(self.word_id) is not str or not self.word_id:
            raise ValueError("Inbox receipt requires Word ID.")

        if type(self.sequence) is not int or self.sequence < 0:
            raise ValueError("Invalid inbox receipt sequence.")

        if type(self.message) is not str:
            raise TypeError("Invalid inbox receipt message.")

    @classmethod
    def from_event(cls, event):
        if not isinstance(event, SymbolicReplayOutboxEvent):
            raise TypeError(
                "Inbox requires canonical outbox event."
            )

        return cls(
            id=event.id,
            word_id=event.word_id,
            sequence=event.sequence,
            message=event.message,
        )

    def to_dict(self):
        """Serialization boundary only."""
        return {
            "id": self.id,
            "word_id": self.word_id,
            "sequence": self.sequence,
            "message": self.message,
        }

    @classmethod
    def from_dict(cls, record):
        """Serialization boundary only."""
        if type(record) is not dict or set(record) != {
            "id",
            "word_id",
            "sequence",
            "message",
        }:
            raise ValueError("Invalid inbox receipt fields.")

        return cls(**record)


class DurableSymbolicReplayInbox:
    """Persist and deduplicate received symbolic events.

    A successful accept() means that the immutable receipt
    was durably stored, or already exists with identical
    content.

    Concurrent acceptance is serialized by a stable
    cross-process lock. A stale receiver cannot overwrite
    a newer checkpoint. Identical already-persisted events
    are acknowledged without another write.

    Only cooperating writers on a filesystem supporting
    the required OS file locks are protected.
    """

    def __init__(self, *, path, universe_id):
        if type(universe_id) is not str or not universe_id:
            raise ValueError("Inbox requires universe ID.")

        self.path = Path(path)
        self.universe_id = universe_id

        if not self.path.parent.is_dir():
            raise FileNotFoundError(
                f"Inbox directory missing: {self.path.parent}"
            )

        self._receipts = self._read()

    @property
    def receipts(self):
        return self._receipts

    @staticmethod
    def _checksum(payload):
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _validate(receipts):
        if any(
            not isinstance(item, SymbolicReplayInboxReceipt)
            for item in receipts
        ):
            raise TypeError("Noncanonical inbox receipt.")

        if len({item.id for item in receipts}) != len(receipts):
            raise ValueError(
                "Duplicate inbox receipt identities."
            )

        return receipts

    def _read(self):
        if not self.path.exists():
            return ()

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as stream:
            document = json.load(stream)

        expected = {
            "format",
            "version",
            "universe_id",
            "receipts",
            "sha256",
        }

        if (
            type(document) is not dict
            or set(document) != expected
        ):
            raise ValueError(
                "Invalid durable inbox envelope."
            )

        if (
            document["format"] != _FORMAT
            or type(document["version"]) is not int
            or document["version"] != _VERSION
        ):
            raise ValueError(
                "Unsupported durable inbox version."
            )

        if document["universe_id"] != self.universe_id:
            raise ValueError(
                "Durable inbox belongs to another universe."
            )

        if type(document["receipts"]) is not list:
            raise TypeError(
                "Invalid durable inbox receipts."
            )

        payload = {
            key: document[key]
            for key in (
                "format",
                "version",
                "universe_id",
                "receipts",
            )
        }

        if document["sha256"] != self._checksum(payload):
            raise ValueError(
                "Durable inbox checksum mismatch."
            )

        receipts = tuple(
            SymbolicReplayInboxReceipt.from_dict(row)
            for row in document["receipts"]
        )

        return self._validate(receipts)

    def _write(self, receipts):
        self._validate(receipts)

        payload = {
            "format": _FORMAT,
            "version": _VERSION,
            "universe_id": self.universe_id,
            "receipts": [
                item.to_dict()
                for item in receipts
            ],
        }

        document = {
            **payload,
            "sha256": self._checksum(payload),
        }

        temporary = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temporary = Path(stream.name)

                json.dump(
                    document,
                    stream,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )

                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())

            os.replace(temporary, self.path)
            temporary = None

            if os.name == "posix":
                descriptor = os.open(
                    self.path.parent,
                    os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0),
                )

                try:
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)

        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def accept(self, event):
        """Safely accept a new or previously persisted event.

        The OS lock covers the whole read-check-write cycle.
        A duplicate ID is acknowledged without another write.
        A stale writer with a different new event must reopen.
        """
        receipt = SymbolicReplayInboxReceipt.from_event(
            event
        )

        with exclusive_inbox_lock(self.path):
            current = self._read()

            # Check duplicate identities first. A receiver
            # created before another process's commit can
            # still acknowledge the same exact event.
            for stored in current:
                if stored.id == receipt.id:
                    if stored != receipt:
                        raise ValueError(
                            "Inbox event identity collision."
                        )

                    self._receipts = current
                    return True

            # Preserve A18 stale-writer protection for a
            # different newly received event.
            if current != self._receipts:
                raise ValueError(
                    "Inbox checkpoint changed; "
                    "reopen the receiver."
                )

            updated = current + (receipt,)

            # Commit the canonical receipt ledger before
            # acknowledging the sender. A failed write
            # leaves the event eligible for safe retry.
            self._write(updated)

            self._receipts = updated

            return True
