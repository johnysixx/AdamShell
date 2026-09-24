from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType

from universe.logger import UniverseLogger


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

        event_snapshot = (
            event.to_dict()
        )

        results = []

        for handler in list(
            self.subscribers.get(
                event_name,
                []
            )
        ):
            results.append(
                handler(
                    event_snapshot
                )
            )

        return {
            "event": event_snapshot,
            "subscriber_count": len(results),
            "results": results
        }

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
