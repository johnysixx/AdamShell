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
_VERSION = 2


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
        cls, universe, outbox, inbox, *,
        state, batch_sha256,
    ):
        payload = {
            "format": _FORMAT,
            "version": _VERSION,
            "universe_id": str(universe.id),
            "outbox_name": outbox.name,
            "inbox_name": inbox.name,
            "state": state,
            "batch_sha256": batch_sha256,
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

        # V1 has no immutable batch identity.
        # Never silently treat it as a V2 manifest.
        if (
            type(document) is dict
            and document.get("format") == _FORMAT
            and type(document.get("version")) is int
            and document["version"] == 1
        ):
            raise ValueError(
                "Legacy bootstrap manifest v1 lacks batch "
                "lineage; manual migration required."
            )

        expected = {
            "format",
            "version",
            "universe_id",
            "outbox_name",
            "inbox_name",
            "state",
            "batch_sha256",
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
            or type(document["batch_sha256"]) is not str
            or len(document["batch_sha256"]) != 64
            or any(
                char not in "0123456789abcdef"
                for char in document["batch_sha256"]
            )
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
                "batch_sha256",
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

        return (
            document["state"],
            document["batch_sha256"],
        )

    @staticmethod
    def _assert_initial_snapshot(
        universe, registry, records,
    ):
        """Reject canonical registry drift during bootstrap."""
        if (
            universe.symbolic_replay_outbox is not registry
            or tuple(registry) != records
        ):
            raise RuntimeError(
                "Bootstrap outbox changed during initialization."
            )

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

                    registry = universe.symbolic_replay_outbox
                    records = SymbolicReplayOutboxStore._records(
                        registry
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

                    # Capture immutable event identity
                    # once, before the PREPARING marker.
                    batch_sha256 = (
                        SymbolicReplayOutboxStore
                        .lineage_digest(
                            universe.id,
                            records,
                        )
                    )

                    # A persistent marker must predate
                    # every newly created checkpoint.
                    cls._write(
                        manifest,
                        cls._document(
                            universe, outbox, inbox,
                            state="PREPARING",
                            batch_sha256=batch_sha256,
                        ),
                    )

                    # Reject changes before writing the
                    # first checkpoint. Leave PREPARING intact
                    # when canonical memory has drifted.
                    cls._assert_initial_snapshot(
                        universe, registry, records,
                    )

                    # Locks are already held. Save exactly
                    # the immutable snapshot captured above;
                    # do not reread the live registry.
                    SymbolicReplayOutboxStore.prepare_new(
                        outbox
                    )
                    SymbolicReplayOutboxStore._write(
                        outbox,
                        SymbolicReplayOutboxStore._document(
                            universe.id,
                            records,
                        ),
                    )

                    cls._assert_initial_snapshot(
                        universe, registry, records,
                    )

                    receiver = DurableSymbolicReplayInbox(
                        path=inbox,
                        universe_id=str(universe.id),
                    )

                    # Explicit empty ledger initialization.
                    receiver._write(())

                    cls._assert_initial_snapshot(
                        universe, registry, records,
                    )

                    # Ensure the immutable disk checkpoint
                    # matches the captured canonical records.
                    persisted = SymbolicReplayOutboxStore.read(
                        universe,
                        outbox,
                    )

                    if persisted != records:
                        raise ValueError(
                            "Bootstrap checkpoint differs "
                            "from initial snapshot."
                        )

                    report = (
                        SymbolicReplayRecoveryAuditor
                        ._validate_pair(
                            universe, persisted, (),
                        )
                    )

                    # READY is published only after all
                    # checks have passed. A later mutation
                    # cannot alter the persisted snapshot.
                    cls._write(
                        manifest,
                        cls._document(
                            universe, outbox, inbox,
                            state="READY",
                            batch_sha256=batch_sha256,
                        ),
                    )

                    # Detect a mutation injected while
                    # the READY manifest was being written.
                    # READY remains valid for recovery from
                    # a fresh Universe, but no misleading
                    # report is returned to this caller.
                    cls._assert_initial_snapshot(
                        universe, registry, records,
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
        required_receipt_ids=None,
        trusted_witness=None,
        witness_authority=None,
        trusted_floor=None,
    ):
        """Restore only after READY and successful A22 audit.

        PREPARING, missing or corrupted manifests are
        rejected without modifying the canonical runtime.
        """
        outbox, inbox, manifest = cls._paths(
            outbox_path, inbox_path, manifest_path,
        )

        with exclusive_inbox_lock(manifest):
            state, batch_sha256 = cls._read(
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
                expected_batch_sha256=batch_sha256,
                required_receipt_ids=required_receipt_ids,
                trusted_witness=trusted_witness,
                witness_authority=witness_authority,
                trusted_floor=trusted_floor,
            )
