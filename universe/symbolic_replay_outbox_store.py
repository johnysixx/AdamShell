import hashlib
import json
import os
import tempfile
from dataclasses import replace
from pathlib import Path

from universe.symbolic_replay_outbox import (
    SymbolicReplayOutbox,
    SymbolicReplayOutboxEvent,
)


_FORMAT = "adamshell.symbolic_replay_outbox"
_VERSION = 1


class SymbolicReplayOutboxStore:
    """Single-writer durable symbolic delivery checkpoint.

    Uses atomic file replacement. Concurrent writers and
    whole-runtime persistence are outside this boundary.
    """

    @staticmethod
    def _records(records):
        if not isinstance(records, (list, tuple)):
            raise TypeError(
                "Outbox records must be a list or tuple."
            )

        frozen = tuple(records)

        if not all(
            isinstance(item, SymbolicReplayOutboxEvent)
            for item in frozen
        ):
            raise TypeError("Noncanonical outbox record.")

        if len({item.id for item in frozen}) != len(frozen):
            raise ValueError(
                "Duplicate outbox event identities."
            )

        if any(
            item.sequence != position
            for position, item in enumerate(frozen)
        ):
            raise ValueError(
                "Outbox event sequence is not consecutive."
            )

        return frozen

    @staticmethod
    def _payload(universe_id, records):
        return {
            "format": _FORMAT,
            "version": _VERSION,
            "universe_id": str(universe_id),
            "events": [
                item.to_dict()
                for item in records
            ],
        }

    @staticmethod
    def _checksum(payload):
        canonical = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical).hexdigest()

    @classmethod
    def _document(cls, universe_id, records):
        payload = cls._payload(
            universe_id,
            cls._records(records),
        )

        return {
            **payload,
            "sha256": cls._checksum(payload),
        }

    @staticmethod
    def prepare_new(path):
        path = Path(path)

        if path.exists():
            raise FileExistsError(
                f"Durable outbox already exists: {path}"
            )

        if not path.parent.is_dir():
            raise FileNotFoundError(
                f"Outbox directory missing: {path.parent}"
            )

        return path

    @staticmethod
    def _write(path, document):
        path = Path(path)

        if not path.parent.is_dir():
            raise FileNotFoundError(
                f"Outbox directory missing: {path.parent}"
            )

        temporary = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=path.parent,
                prefix=f".{path.name}.",
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

            os.replace(temporary, path)
            temporary = None

            if os.name == "posix":
                descriptor = os.open(
                    path.parent,
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

    @classmethod
    def read(cls, universe, path):
        with Path(path).open(
            "r",
            encoding="utf-8",
        ) as stream:
            document = json.load(stream)

        expected = {
            "format",
            "version",
            "universe_id",
            "events",
            "sha256",
        }

        if type(document) is not dict:
            raise ValueError(
                "Invalid durable outbox envelope."
            )

        if set(document) != expected:
            raise ValueError(
                "Invalid durable outbox envelope."
            )

        if (
            document["format"] != _FORMAT
            or type(document["version"]) is not int
            or document["version"] != _VERSION
        ):
            raise ValueError(
                "Unsupported durable outbox version."
            )

        if (
            type(document["universe_id"]) is not str
            or document["universe_id"] != str(universe.id)
        ):
            raise ValueError(
                "Durable outbox belongs to another universe."
            )

        if type(document["events"]) is not list:
            raise TypeError(
                "Invalid outbox event payload."
            )

        payload = {
            key: document[key]
            for key in (
                "format",
                "version",
                "universe_id",
                "events",
            )
        }

        if document["sha256"] != cls._checksum(payload):
            raise ValueError(
                "Durable outbox checksum mismatch."
            )

        records = tuple(
            SymbolicReplayOutboxEvent.from_dict(item)
            for item in document["events"]
        )

        return cls._records(records)

    @classmethod
    def save(cls, universe, path, *, require_new=False):
        path = Path(path)

        records = cls._records(
            universe.symbolic_replay_outbox
        )

        if require_new:
            cls.prepare_new(path)

        elif path.exists():
            previous = cls.read(universe, path)

            if len(previous) != len(records):
                raise ValueError(
                    "Cannot rewrite a different durable outbox."
                )

            for old, new in zip(previous, records):
                if replace(
                    old,
                    delivered=new.delivered,
                ) != new:
                    raise ValueError(
                        "Cannot change persisted event identity."
                    )

                if old.delivered and not new.delivered:
                    raise ValueError(
                        "Cannot revoke durable acknowledgement."
                    )

        cls._write(
            path,
            cls._document(universe.id, records),
        )

        return records

    @classmethod
    def restore(cls, universe, path):
        records = cls.read(universe, path)

        return SymbolicReplayOutbox.restore(
            universe,
            [event.to_dict() for event in records],
        )

    @classmethod
    def ensure_current(cls, universe, path):
        stored = cls.read(universe, path)

        actual = cls._records(
            universe.symbolic_replay_outbox
        )

        if stored != actual:
            raise ValueError(
                "In-memory outbox differs from durable checkpoint."
            )

        return stored

    @classmethod
    def persist_ack(
        cls,
        universe,
        path,
        index,
        acknowledged,
    ):
        records = cls.ensure_current(universe, path)

        old = records[index]

        if (
            old.delivered
            or acknowledged != replace(
                old,
                delivered=True,
            )
        ):
            raise ValueError(
                "Invalid durable acknowledgement."
            )

        updated = (
            records[:index]
            + (acknowledged,)
            + records[index + 1:]
        )

        cls._write(
            path,
            cls._document(universe.id, updated),
        )
