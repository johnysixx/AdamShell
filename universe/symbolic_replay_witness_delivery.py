"""Witness-gated durable symbolic replay delivery.

Order for each event:
1. Read and validate current external witness.
2. Persist or deduplicate the local inbox receipt.
3. Publish the monotonic external witness using CAS.
4. Only then allow the durable outbox ACK.

This is an opt-in delivery path, not an atomic
transaction between local and external storage.

Crash after inbox commit but before witness publication
remains a possible rollback/redelivery window.
The remote authority must independently guarantee
durability, current reads, and atomic CAS.
"""

from pathlib import Path

from universe.symbolic_replay_file_lock import (
    exclusive_inbox_lock,
)
from universe.symbolic_replay_inbox import (
    DurableSymbolicReplayInbox,
    SymbolicReplayInboxReceipt,
)
from universe.symbolic_replay_outbox import (
    SymbolicReplayOutboxEvent,
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


class SymbolicReplayWitnessDelivery:
    """Durable dispatch with witness publication before ACK.

    The supplied authority must already have a canonical
    initial revision for the exact universe and batch.

    A failed authority read or publish leaves the outbox
    event pending. Retry is safe for the receipt ledger,
    but arbitrary external side effects are not made
    exactly-once by this class.
    """

    def __init__(
        self,
        universe,
        *,
        outbox_path,
        receiver,
        witness_authority,
    ):
        if not isinstance(
            receiver,
            DurableSymbolicReplayInbox,
        ):
            raise TypeError(
                "Witness delivery requires durable inbox."
            )

        if not isinstance(
            witness_authority,
            SymbolicReplayWitnessAuthority,
        ):
            raise TypeError(
                "Witness delivery requires witness authority."
            )

        self.universe = universe
        self.receiver = receiver
        self.authority = witness_authority
        self.outbox_path = Path(outbox_path).resolve()
        self.universe_id = str(universe.id)

        if receiver.universe_id != self.universe_id:
            raise ValueError(
                "Witness delivery inbox universe mismatch."
            )

        if receiver.path.resolve() == self.outbox_path:
            raise ValueError(
                "Witness delivery paths must differ."
            )

        self._registry = universe.symbolic_replay_outbox
        self._events = SymbolicReplayOutboxStore._records(
            self._registry
        )

        self.batch_sha256 = (
            SymbolicReplayOutboxStore.lineage_digest(
                self.universe_id,
                self._events,
            )
        )

        self._by_id = {
            event.id: event
            for event in self._events
        }

        self._receipt_by_id = {
            event.id: SymbolicReplayInboxReceipt.from_event(
                event
            )
            for event in self._events
        }

    def _current(self):
        revision = self.authority.read_current(
            universe_id=self.universe_id,
            batch_sha256=self.batch_sha256,
        )

        if type(revision) is not SymbolicReplayWitnessRevision:
            raise TypeError(
                "Witness authority returned noncanonical revision."
            )

        witness = revision.witness

        if witness.universe_id != self.universe_id:
            raise ValueError(
                "Witness authority universe mismatch."
            )

        if witness.batch_sha256 != self.batch_sha256:
            raise ValueError(
                "Witness authority batch mismatch."
            )

        if not set(witness.receipt_ids).issubset(
            self._by_id
        ):
            raise ValueError(
                "Witness authority contains unknown receipt."
            )

        return revision

    def _receipts(self):
        # Read under inbox lock, without retaining a
        # potentially stale receiver cache.
        with exclusive_inbox_lock(self.receiver.path):
            if not self.receiver.path.is_file():
                raise FileNotFoundError(
                    "Witness delivery inbox checkpoint missing."
                )

            receipts = self.receiver._read()

        for receipt in receipts:
            expected = self._receipt_by_id.get(receipt.id)

            if expected is None or receipt != expected:
                raise ValueError(
                    "Witness delivery inbox batch mismatch."
                )

        return receipts

    @staticmethod
    def _require_receipts(revision, receipts):
        persisted = {
            receipt.id
            for receipt in receipts
        }

        if not set(
            revision.witness.receipt_ids
        ).issubset(persisted):
            raise ValueError(
                "Witness authority ahead of local inbox."
            )

    def _accept(self, event):
        # This callback is invoked only by durable
        # SymbolicReplayOutboxStore.dispatch().
        if (
            type(event) is not SymbolicReplayOutboxEvent
            or event.delivered
            or self._by_id.get(event.id) != event
        ):
            raise ValueError(
                "Witness delivery event identity mismatch."
            )

        if (
            self.universe.symbolic_replay_outbox
            is not self._registry
        ):
            raise RuntimeError(
                "Witness delivery registry replaced."
            )

        # Preflight before any local write. A remote
        # witness already ahead of the inbox is unsafe.
        current = self._current()
        before = self._receipts()
        self._require_receipts(current, before)

        # This is the local persistence boundary.
        # Existing identical receipts are deduplicated.
        if self.receiver.accept(event) is not True:
            raise RuntimeError(
                "Witness delivery receipt not acknowledged."
            )

        persisted = self._receipts()
        self._require_receipts(current, persisted)

        ids = {
            receipt.id
            for receipt in persisted
        }

        # Use canonical batch order rather than
        # filesystem insertion or set iteration order.
        confirmed_ids = tuple(
            item.id
            for item in self._events
            if item.id in ids
        )

        previous = frozenset(
            current.witness.receipt_ids
        )

        if frozenset(confirmed_ids) == previous:
            # Authority already has all these receipts.
            # The pending outbox ACK can now be persisted.
            return True

        proposed = SymbolicReplayReceiptWitness(
            universe_id=self.universe_id,
            batch_sha256=self.batch_sha256,
            receipt_ids=confirmed_ids,
        )

        published = self.authority.publish(
            proposed,
            expected_revision=current.revision,
        )

        if (
            type(published)
            is not SymbolicReplayWitnessRevision
        ):
            raise TypeError(
                "Witness authority returned noncanonical publication."
            )

        if (
            published.revision != current.revision + 1
            or not set(
                published.witness.receipt_ids
            ).issubset(ids)
            or published.witness.universe_id
            != self.universe_id
            or published.witness.batch_sha256
            != self.batch_sha256
            or not set(confirmed_ids).issubset(
                published.witness.receipt_ids
            )
        ):
            raise ValueError(
                "Witness authority publication not confirmed."
            )

        # Only now may SymbolicReplayOutbox.dispatch
        # persist the ACK and update canonical memory.
        return True

    def dispatch(self):
        """Run witnessed delivery through durable outbox.

        SymbolicReplayOutboxStore holds the outbox lock
        across the receiver and authority operations.
        The nested inbox lock uses the existing lock order.
        """
        if (
            self.universe.symbolic_replay_outbox
            is not self._registry
        ):
            raise RuntimeError(
                "Witness delivery registry replaced."
            )

        current_digest = (
            SymbolicReplayOutboxStore.lineage_digest(
                self.universe_id,
                self._registry,
            )
        )

        if current_digest != self.batch_sha256:
            raise ValueError(
                "Witness delivery batch changed."
            )

        return SymbolicReplayOutboxStore.dispatch(
            self.universe,
            self.outbox_path,
            sink=self._accept,
        )
