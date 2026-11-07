"""Explicit, fail-closed symbolic replay bootstrap.

The manifest is written before the two checkpoints.
A PREPARING manifest is never silently completed.
Recovery requires READY and a successful A22 audit.

Only cooperative writers and the receipt-ledger effect
are covered. This is not a power-loss guarantee.
"""

import hashlib
import json
import os
import tempfile
from pathlib import Path

from universe.symbolic_replay_file_lock import (
    exclusive_inbox_lock,
)
from universe.symbolic_replay_inbox import (
    DurableSymbolicReplayInbox,
)
from universe.symbolic_replay_outbox_store import (
    SymbolicReplayOutboxStore,
)
from universe.symbolic_replay_recovery_auditor import (
    SymbolicReplayRecoveryAuditor,
)


_FORMAT = "adamshell.symbolic_replay_bootstrap"
_VERSION = 1


class SymbolicReplayBootstrap:
    """Explicit creation and audited recovery of a checkpoint pair.

    All three files must share one existing directory.
    Lock order: manifest -> outbox -> inbox.

    initialize(): only for a new, empty checkpoint pair.
    recover(): only for a READY manifest and valid pair.

    No automatic deletion, repair or overwrite.
    """

    @staticmethod
    def _paths(outbox_path, inbox_path, manifest_path):
        paths = tuple(
            Path(path).resolve()
            for path in (
                outbox_path,
                inbox_path,
                manifest_path,
            )
        )

        if len(set(paths)) != 3:
            raise ValueError(
                "Bootstrap paths must be distinct."
            )

        if len({path.parent for path in paths}) != 1:
            raise ValueError(
                "Bootstrap files must be in the same directory."
            )

        if any(
            path.with_name(path.name + ".lock") in paths
            for path in paths
        ):
            raise ValueError(
                "Bootstrap paths must not overlap lockfiles."
            )

        if not paths[0].parent.is_dir():
            raise FileNotFoundError(
                "Bootstrap directory does not exist."
            )

        return paths

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
    def _document(
        cls, universe, outbox, inbox, *, state,
    ):
        payload = {
            "format": _FORMAT,
            "version": _VERSION,
            "universe_id": str(universe.id),
            "outbox_name": outbox.name,
            "inbox_name": inbox.name,
            "state": state,
        }

        return {
            **payload,
            "sha256": cls._checksum(payload),
        }

    @staticmethod
    def _write(path, document):
        """Atomic manifest replacement with flushed content."""
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
    def _read(cls, universe, outbox, inbox, manifest):
        with manifest.open(
            "r", encoding="utf-8",
        ) as stream:
            document = json.load(stream)

        expected = {
            "format",
            "version",
            "universe_id",
            "outbox_name",
            "inbox_name",
            "state",
            "sha256",
        }

        if (
            type(document) is not dict
            or set(document) != expected
        ):
            raise ValueError(
                "Invalid bootstrap manifest envelope."
            )

        if (
            document["format"] != _FORMAT
            or type(document["version"]) is not int
            or document["version"] != _VERSION
            or type(document["universe_id"]) is not str
            or type(document["outbox_name"]) is not str
            or type(document["inbox_name"]) is not str
            or type(document["state"]) is not str
        ):
            raise ValueError(
                "Invalid bootstrap manifest fields."
            )

        payload = {
            key: document[key]
            for key in (
                "format",
                "version",
                "universe_id",
                "outbox_name",
                "inbox_name",
                "state",
            )
        }

        if document["sha256"] != cls._checksum(payload):
            raise ValueError(
                "Bootstrap manifest checksum mismatch."
            )

        if document["universe_id"] != str(universe.id):
            raise ValueError(
                "Bootstrap belongs to another universe."
            )

        if (
            document["outbox_name"] != outbox.name
            or document["inbox_name"] != inbox.name
        ):
            raise ValueError(
                "Bootstrap checkpoint path mismatch."
            )

        if document["state"] not in ("PREPARING", "READY"):
            raise ValueError(
                "Invalid bootstrap lifecycle state."
            )

        return document["state"]

    @classmethod
    def initialize(
        cls,
        universe,
        *,
        outbox_path,
        inbox_path,
        manifest_path,
    ):
        """Create a new empty checkpoint pair explicitly.

        Write PREPARING first. If a later operation fails,
        preserve all completed files for inspection.
        Only a fully created pair becomes READY.

        Returns (immutable audit report, inbox receiver).
        """
        outbox, inbox, manifest = cls._paths(
            outbox_path, inbox_path, manifest_path,
        )

        with exclusive_inbox_lock(manifest):
            with exclusive_inbox_lock(outbox):
                with exclusive_inbox_lock(inbox):
                    if any(
                        path.exists()
                        for path in (manifest, outbox, inbox)
                    ):
                        raise FileExistsError(
                            "Bootstrap storage already exists."
                        )

                    if not isinstance(
                        universe.symbolic_replay_outbox, list
                    ):
                        raise TypeError(
                            "Bootstrap requires canonical outbox list."
                        )

                    records = SymbolicReplayOutboxStore._records(
                        universe.symbolic_replay_outbox
                    )

                    if any(event.delivered for event in records):
                        raise ValueError(
                            "Initial outbox events must be pending."
                        )

                    if getattr(
                        universe,
                        "_symbolic_replay_dispatching",
                        False,
                    ):
                        raise RuntimeError(
                            "Cannot bootstrap during dispatch."
                        )

                    # A persistent marker must predate
                    # every newly created checkpoint.
                    cls._write(
                        manifest,
                        cls._document(
                            universe, outbox, inbox,
                            state="PREPARING",
                        ),
                    )

                    # Locks are already held, so do not
                    # reacquire the non-reentrant lock.
                    SymbolicReplayOutboxStore._save_locked(
                        universe,
                        outbox,
                        require_new=True,
                    )

                    receiver = DurableSymbolicReplayInbox(
                        path=inbox,
                        universe_id=str(universe.id),
                    )

                    # Explicit empty ledger initialization.
                    receiver._write(())

                    cls._write(
                        manifest,
                        cls._document(
                            universe, outbox, inbox,
                            state="READY",
                        ),
                    )

                    report = (
                        SymbolicReplayRecoveryAuditor
                        ._validate_pair(
                            universe, records, (),
                        )
                    )

                    return report, receiver

    @classmethod
    def recover(
        cls,
        universe,
        *,
        outbox_path,
        inbox_path,
        manifest_path,
    ):
        """Restore only after READY and successful A22 audit.

        PREPARING, missing or corrupted manifests are
        rejected without modifying the canonical runtime.
        """
        outbox, inbox, manifest = cls._paths(
            outbox_path, inbox_path, manifest_path,
        )

        with exclusive_inbox_lock(manifest):
            state = cls._read(
                universe, outbox, inbox, manifest,
            )

            if state != "READY":
                raise RuntimeError(
                    "Bootstrap manifest is not READY; "
                    "manual recovery required."
                )

            return SymbolicReplayRecoveryAuditor.restore(
                universe,
                outbox_path=outbox,
                inbox_path=inbox,
            )
