from universe.logger import UniverseLogger


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
        event = {
            "name": event_name,
            "payload": dict(payload)
        }

        self.event_history.append(event)

        results = []

        for handler in list(
            self.subscribers.get(
                event_name,
                []
            )
        ):
            results.append(
                handler(event)
            )

        return {
            "event": event,
            "subscriber_count": len(results),
            "results": results
        }

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
