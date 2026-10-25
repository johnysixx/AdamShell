from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType

from universe.logger import UniverseLogger


def _serialize_quantum_value(value):
    to_dict = getattr(
        value,
        "to_dict",
        None,
    )

    if callable(to_dict):
        return to_dict()

    return deepcopy(value)


@dataclass(slots=True, frozen=True)
class QuantumEvent:

    name: str
    payload: object = field(
        default_factory=dict
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "name",
            str(self.name),
        )

        object.__setattr__(
            self,
            "payload",
            MappingProxyType(
                deepcopy(
                    dict(
                        self.payload
                    )
                )
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "payload": deepcopy(
                dict(
                    self.payload
                )
            ),
        }


@dataclass(slots=True, frozen=True)
class QuantumEventPublicationResult:

    event: QuantumEvent
    subscriber_count: int
    results: tuple[object, ...]

    def __post_init__(self):
        if not isinstance(
            self.event,
            QuantumEvent,
        ):
            raise TypeError(
                "Quantum event publication requires "
                "a QuantumEvent object."
            )

        object.__setattr__(
            self,
            "subscriber_count",
            int(self.subscriber_count),
        )

        object.__setattr__(
            self,
            "results",
            tuple(self.results),
        )

        if (
            self.subscriber_count
            != len(self.results)
        ):
            raise ValueError(
                "Quantum event subscriber count must "
                "match the result count."
            )

    def to_dict(self):
        return {
            "event": self.event.to_dict(),
            "subscriber_count": (
                self.subscriber_count
            ),
            "results": [
                _serialize_quantum_value(
                    result
                )
                for result
                in self.results
            ],
        }


class QuantumEventBus:

    def __init__(self):
        self.name = "quantum_event_bus"
        self.subscribers = {}
        self.event_history = []

        UniverseLogger.boot(
            "QUANTUM EVENT BUS CREATED"
        )

    def subscribe(
        self,
        event_name,
        handler
    ):
        if not callable(handler):
            raise TypeError(
                "Event handler must be callable."
            )

        handlers = self.subscribers.setdefault(
            event_name,
            []
        )

        if handler not in handlers:
            handlers.append(handler)

        return handler

    def unsubscribe(
        self,
        event_name,
        handler
    ):
        handlers = self.subscribers.get(
            event_name,
            []
        )

        if handler not in handlers:
            return False

        handlers.remove(handler)

        if not handlers:
            del self.subscribers[event_name]

        return True

    def publish(
        self,
        event_name,
        **payload
    ):
        event = QuantumEvent(
            name=event_name,
            payload=payload,
        )

        self.record_event(
            event
        )

        results = []

        for handler in list(
            self.subscribers.get(
                event_name,
                []
            )
        ):
            # Each subscriber gets its own domain object.
            # The recorded event remains untouched.
            subscriber_event = QuantumEvent(
                name=event.name,
                payload=event.payload,
            )

            results.append(
                handler(subscriber_event)
            )

        return QuantumEventPublicationResult(
            event=event,
            subscriber_count=len(results),
            results=tuple(results),
        )

    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            QuantumEvent,
        ):
            raise TypeError(
                "Quantum event history requires "
                "a QuantumEvent object."
            )

        self.event_history.append(
            event
        )

        return event

    @property
    def public_state(self):
        return {
            "name": self.name,
            "subscriber_counts": {
                event_name: len(handlers)
                for event_name, handlers
                in self.subscribers.items()
            },
            "event_count": len(
                self.event_history
            )
        }
