from dataclasses import dataclass, replace
from uuid import NAMESPACE_URL, uuid5

from universe.logger import UniverseLogger


@dataclass(frozen=True, slots=True)
class SymbolicReplayOutboxEvent:
    id: str
    word_id: str
    sequence: int
    message: str
    delivered: bool = False

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("Outbox event requires an ID.")

        if not isinstance(self.word_id, str) or not self.word_id:
            raise ValueError("Outbox event requires Word ID.")

        if type(self.sequence) is not int or self.sequence < 0:
            raise ValueError("Invalid outbox sequence.")

        if not isinstance(self.message, str):
            raise TypeError("Invalid outbox message.")

        if type(self.delivered) is not bool:
            raise TypeError("Outbox delivery flag must be bool.")

    def to_dict(self):
        """Serialization boundary only."""
        return {
            "id": self.id,
            "word_id": self.word_id,
            "sequence": self.sequence,
            "message": self.message,
            "delivered": self.delivered,
        }

    @classmethod
    def from_dict(cls, payload):
        """Serialization boundary only."""
        expected = {
            "id",
            "word_id",
            "sequence",
            "message",
            "delivered",
        }

        if not isinstance(payload, dict):
            raise TypeError("Outbox record must be a dict.")

        if set(payload) != expected:
            raise ValueError("Invalid outbox record fields.")

        return cls(
            id=payload["id"],
            word_id=payload["word_id"],
            sequence=payload["sequence"],
            message=payload["message"],
            delivered=payload["delivered"],
        )


class SymbolicReplayOutbox:
    """Replay event history and retryable delivery state.

    Successful sink return acknowledges an event.
    A raised exception or explicit False leaves it pending.

    Delivery is at-least-once, not exactly-once.
    """

    @staticmethod
    def new_event(
        *,
        universe_id,
        word_id,
        word_position,
        sequence,
        message,
    ):
        identity = (
            f"adamshell:symbolic-replay:"
            f"{universe_id}:{word_position}:"
            f"{sequence}:{word_id}"
        )

        return SymbolicReplayOutboxEvent(
            id=str(uuid5(NAMESPACE_URL, identity)),
            word_id=word_id,
            sequence=sequence,
            message=message,
        )

    @staticmethod
    def pending(universe):
        return tuple(
            event
            for event in universe.symbolic_replay_outbox
            if not event.delivered
        )

    @staticmethod
    def dispatch(
        universe, *, sink=None, persist_ack=None,
    ):
        records = universe.symbolic_replay_outbox

        if not isinstance(records, list):
            raise TypeError("Outbox registry must be a list.")

        if sink is not None and not callable(sink):
            raise TypeError("Delivery sink must be callable.")

        if persist_ack is not None and not callable(
            persist_ack
        ):
            raise TypeError(
                "Ack persistence hook must be callable."
            )

        if getattr(
            universe,
            "_symbolic_replay_dispatching",
            False,
        ):
            raise RuntimeError(
                "Symbolic replay dispatch already running."
            )

        snapshot = tuple(records)

        if not all(
            isinstance(event, SymbolicReplayOutboxEvent)
            for event in snapshot
        ):
            raise TypeError("Invalid canonical outbox records.")

        object.__setattr__(
            universe,
            "_symbolic_replay_dispatching",
            True,
        )

        completed = 0

        try:
            for index, event in enumerate(snapshot):
                if event.delivered:
                    continue

                if sink is None:
                    UniverseLogger.event(event.message)
                else:
                    acknowledgement = sink(event)

                    if acknowledgement is False:
                        raise RuntimeError(
                            "Outbox delivery not acknowledged."
                        )

                # Do not acknowledge a record if a callback
                # changed the registry during dispatch.
                if (
                    len(records) != len(snapshot)
                    or records[index] is not event
                ):
                    raise RuntimeError(
                        "Outbox changed during delivery."
                    )

                acknowledged = replace(
                    event,
                    delivered=True,
                )

                if persist_ack is not None:
                    # Persist before updating canonical memory.
                    # The recipient must deduplicate by ID
                    # if its acknowledgement is ambiguous.
                    persist_ack(index, acknowledged)

                records[index] = acknowledged
                completed += 1

        finally:
            object.__setattr__(
                universe,
                "_symbolic_replay_dispatching",
                False,
            )

        return completed

    @staticmethod
    def restore(universe, serialized_records):
        """Restore an outbox at a serialization boundary."""
        records = universe.symbolic_replay_outbox

        if not isinstance(records, list):
            raise TypeError("Outbox registry must be a list.")

        if records:
            raise ValueError(
                "Restore requires an empty target outbox."
            )

        if getattr(
            universe,
            "_symbolic_replay_dispatching",
            False,
        ):
            raise RuntimeError(
                "Cannot restore during delivery."
            )

        try:
            payloads = tuple(serialized_records)
        except TypeError as error:
            raise TypeError(
                "Outbox snapshot must be iterable."
            ) from error

        staged = tuple(
            SymbolicReplayOutboxEvent.from_dict(payload)
            for payload in payloads
        )

        identities = [event.id for event in staged]

        if len(identities) != len(set(identities)):
            raise ValueError(
                "Duplicate outbox event identities."
            )

        # All records were validated before publication.
        list.extend(records, staged)

        return staged
