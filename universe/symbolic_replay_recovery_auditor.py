"""Cross-check durable symbolic inbox/outbox recovery.

Audit before publishing canonical outbox records.
Never repair, delete or rewrite checkpoint files.

Lock order is always outbox -> inbox, matching delivery.
"""

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from universe.symbolic_replay_file_lock import (
    exclusive_inbox_lock,
)
from universe.symbolic_replay_inbox import (
    DurableSymbolicReplayInbox,
)
from universe.symbolic_replay_outbox import (
    SymbolicReplayOutbox,
)
from universe.symbolic_replay_outbox_store import (
    SymbolicReplayOutboxStore,
)
from universe.symbolic_replay_receipt_witness import (
    SymbolicReplayReceiptWitness,
)
from universe.symbolic_replay_witness_authority import (
    SymbolicReplayWitnessAuthority,
    SymbolicReplayWitnessRevision,
)


@dataclass(frozen=True, slots=True)
class SymbolicReplayRecoveryAudit:
    universe_id: str
    status: str
    outbox_count: int
    inbox_count: int
    delivered_count: int
    pending_ack_ids: tuple[str, ...]
    pending_delivery_ids: tuple[str, ...]


class SymbolicReplayRecoveryAuditor:
    """Fail-closed verification of two durable checkpoints.

    Missing inboxes are rejected even if the outbox has
    no ACKs. Absence alone cannot prove that an earlier
    inbox checkpoint was never created.

    A pending event with a matching receipt is recoverable:
    the existing idempotent inbox can safely acknowledge
    the same ID on retry.

    Only cooperating writers and the receipt-ledger effect
    are covered. External effects and power-loss durability
    require their own guarantees.
    """

    @staticmethod
    def _validate_pair(universe, events, receipts):
        events_by_id = {
            event.id: event
            for event in events
        }

        receipt_ids = set()

        for receipt in receipts:
            event = events_by_id.get(receipt.id)

            if event is None:
                raise ValueError(
                    "Unknown inbox receipt event ID."
                )

            if (
                receipt.word_id != event.word_id
                or receipt.sequence != event.sequence
                or receipt.message != event.message
            ):
                raise ValueError(
                    "Inbox/outbox event payload conflict."
                )

            receipt_ids.add(receipt.id)

        for event in events:
            if (
                event.delivered
                and event.id not in receipt_ids
            ):
                raise ValueError(
                    "Durable ACK without matching "
                    "inbox receipt."
                )

        pending_ack = tuple(
            event.id
            for event in events
            if (
                not event.delivered
                and event.id in receipt_ids
            )
        )

        pending_delivery = tuple(
            event.id
            for event in events
            if (
                not event.delivered
                and event.id not in receipt_ids
            )
        )

        return SymbolicReplayRecoveryAudit(
            universe_id=str(universe.id),
            status=(
                "RECOVERABLE_PENDING_ACK"
                if pending_ack
                else "CONSISTENT"
            ),
            outbox_count=len(events),
            inbox_count=len(receipts),
            delivered_count=sum(
                event.delivered
                for event in events
            ),
            pending_ack_ids=pending_ack,
            pending_delivery_ids=pending_delivery,
        )

    @classmethod
    @contextmanager
    def _checked_pair(
        cls, universe, outbox_path, inbox_path,
    ):
        outbox_path = Path(outbox_path)
        inbox_path = Path(inbox_path)

        if outbox_path.resolve() == inbox_path.resolve():
            raise ValueError(
                "Inbox and outbox paths must differ."
            )

        # A20 delivery acquires outbox first, then inbox.
        # Matching that order prevents lock inversion.
        with exclusive_inbox_lock(outbox_path):
            with exclusive_inbox_lock(inbox_path):
                events = SymbolicReplayOutboxStore.read(
                    universe,
                    outbox_path,
                )

                # A missing inbox must not be silently
                # interpreted as a fresh empty ledger.
                if not inbox_path.is_file():
                    raise FileNotFoundError(
                        "Durable inbox checkpoint missing: "
                        f"{inbox_path}"
                    )

                receiver = DurableSymbolicReplayInbox(
                    path=inbox_path,
                    universe_id=str(universe.id),
                )

                report = cls._validate_pair(
                    universe,
                    events,
                    receiver.receipts,
                )

                yield report, events, receiver

    @classmethod
    def inspect(
        cls, universe, *, outbox_path, inbox_path,
    ):
        """Read-only consistency audit of both checkpoints.

        The lock mechanism may create stable .lock files,
        but checkpoint contents are never modified.
        """
        with cls._checked_pair(
            universe,
            outbox_path,
            inbox_path,
        ) as (report, _events, _receiver):
            return report

    @classmethod
    def restore(
        cls, universe, *, outbox_path, inbox_path,
        expected_batch_sha256=None,
        required_receipt_ids=None,
        trusted_witness=None,
        witness_authority=None,
    ):
        """Restore delivery state only after full audit.

        Returns (immutable audit report, inbox receiver).
        The target outbox must be empty. Quantum and
        symbolic runtime state is never replayed here.
        """
        if (
            trusted_witness is not None
            and type(trusted_witness)
            is not SymbolicReplayReceiptWitness
        ):
            raise TypeError(
                "Trusted witness must be a canonical "
                "SymbolicReplayReceiptWitness."
            )

        if (
            witness_authority is not None
            and not isinstance(
                witness_authority,
                SymbolicReplayWitnessAuthority,
            )
        ):
            raise TypeError(
                "Witness authority must implement "
                "SymbolicReplayWitnessAuthority."
            )

        if (
            witness_authority is not None
            and trusted_witness is not None
        ):
            raise ValueError(
                "Provide trusted_witness or "
                "witness_authority, not both."
            )

        if expected_batch_sha256 is not None and (
            type(expected_batch_sha256) is not str
            or len(expected_batch_sha256) != 64
            or any(
                char not in "0123456789abcdef"
                for char in expected_batch_sha256
            )
        ):
            raise ValueError(
                "Invalid expected batch lineage digest."
            )

        # Optional evidence supplied by the caller.
        # It must come from storage that cannot be
        # rolled back with this checkpoint pair.
        if required_receipt_ids is None:
            required_receipts = None
        else:
            if type(required_receipt_ids) not in (
                tuple, frozenset,
            ):
                raise TypeError(
                    "Required receipt IDs must be an "
                    "immutable tuple or frozenset."
                )

            if any(
                type(identity) is not str or not identity
                for identity in required_receipt_ids
            ):
                raise ValueError(
                    "Invalid required receipt identity."
                )

            required_receipts = frozenset(
                required_receipt_ids
            )

            if (
                len(required_receipts)
                != len(required_receipt_ids)
            ):
                raise ValueError(
                    "Duplicate required receipt identity."
                )

        records = universe.symbolic_replay_outbox

        if not isinstance(records, list):
            raise TypeError(
                "Recovery target outbox must be a list."
            )

        if records:
            raise ValueError(
                "Recovery requires an empty target outbox."
            )

        if getattr(
            universe,
            "_symbolic_replay_dispatching",
            False,
        ):
            raise RuntimeError(
                "Cannot restore during delivery."
            )

        with cls._checked_pair(
            universe,
            outbox_path,
            inbox_path,
        ) as (report, events, receiver):

            # Both checkpoint locks are held here.
            # Compute identity from the audited events,
            # not from the caller's in-memory registry.
            if (
                expected_batch_sha256 is not None
                or trusted_witness is not None
                or witness_authority is not None
            ):
                actual_batch_sha256 = (
                    SymbolicReplayOutboxStore
                    .lineage_digest(
                        universe.id,
                        events,
                    )
                )

                if (
                    expected_batch_sha256 is not None
                    and actual_batch_sha256
                    != expected_batch_sha256
                ):
                    raise ValueError(
                        "Bootstrap outbox batch lineage mismatch."
                    )

            # The authority is queried inside the
            # outbox/inbox lock scope, after checkpoint
            # audit and before runtime publication.
            # Failure must never fall back silently.
            if witness_authority is not None:
                current_revision = (
                    witness_authority.read_current(
                        universe_id=str(universe.id),
                        batch_sha256=actual_batch_sha256,
                    )
                )

                if (
                    type(current_revision)
                    is not SymbolicReplayWitnessRevision
                ):
                    raise TypeError(
                        "Witness authority returned "
                        "a noncanonical revision."
                    )

                trusted_witness = current_revision.witness

            if trusted_witness is not None:
                if (
                    trusted_witness.universe_id
                    != str(universe.id)
                ):
                    raise ValueError(
                        "Trusted witness universe mismatch."
                    )

                if (
                    trusted_witness.batch_sha256
                    != actual_batch_sha256
                ):
                    raise ValueError(
                        "Trusted witness batch lineage mismatch."
                    )

                persisted_receipt_ids = frozenset(
                    receipt.id
                    for receipt in receiver.receipts
                )

                witnessed_ids = frozenset(
                    trusted_witness.receipt_ids
                )

                if not witnessed_ids.issubset(
                    persisted_receipt_ids
                ):
                    raise ValueError(
                        "Trusted witness missing confirmed receipt."
                    )

                # A31 strict mode is enabled only when
                # recovery queries the current authority.
                # Preserve caller-supplied A27 witness
                # semantics for legacy integrations.
                if witness_authority is not None:
                    delivered_ids = frozenset(
                        event.id
                        for event in events
                        if event.delivered
                    )

                    if not delivered_ids.issubset(
                        witnessed_ids
                    ):
                        raise ValueError(
                            "Durable ACK missing trusted "
                            "authority witness."
                        )

            # Both checkpoint locks are held here.
            # A trusted external witness may establish
            # that particular receipt IDs existed
            # before a suspected local rollback.
            if required_receipts is not None:
                current_receipts = frozenset(
                    receipt.id
                    for receipt in receiver.receipts
                )

                if not required_receipts.issubset(
                    current_receipts
                ):
                    raise ValueError(
                        "Trusted receipt witness mismatch: "
                        "required durable receipt missing."
                    )

            # All checkpoint, lineage and optional
            # witness checks have succeeded before
            # memory publication.
            SymbolicReplayOutbox.restore(
                universe,
                [
                    event.to_dict()
                    for event in events
                ],
            )

            return report, receiver
