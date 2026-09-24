import random
from dataclasses import dataclass




@dataclass(slots=True, frozen=True)
class QuantumDeathRippleEvent:
    event_name: str | None
    predator: str | None
    prey: str | None
    result_scope: str | None
    rotated_count: int

    def __post_init__(self):
        for field_name in (
            "event_name",
            "predator",
            "prey",
            "result_scope",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    str(value),
                )

        object.__setattr__(
            self,
            "rotated_count",
            int(self.rotated_count),
        )

    def to_dict(self):
        return {
            "event_name": self.event_name,
            "predator": self.predator,
            "prey": self.prey,
            "result_scope": self.result_scope,
            "rotated_count": self.rotated_count,
        }


class QuantumDeathRipple:

    def __init__(
        self,
        d20_registry
    ):
        self.d20_registry = d20_registry
        self.history = []

    def on_cronenberg_hunted(
        self,
        event,
        rng=None
    ):
        rng = rng or random

        roll = rng.random()

        if roll < 0.80:
            result = {
                "scope": "none",
                "rotated_count": 0
            }

        elif roll < 0.95:
            result = (
                self.d20_registry
                .rotate_random(
                    rng=rng
                )
            )

        elif roll < 0.99:
            payload = event.get(
                "payload",
                {}
            )

            layer = payload.get(
                "layer",
                "meeting_place"
            )

            result = (
                self.d20_registry
                .rotate_layer(
                    layer
                )
            )

        else:
            result = (
                self.d20_registry
                .rotate_all(
                    rng=rng
                )
            )

        record = QuantumDeathRippleEvent(
            event_name=event.get("name"),
            predator=event.get(
                "payload",
                {}
            ).get("predator"),
            prey=event.get(
                "payload",
                {}
            ).get("prey"),
            result_scope=result.get(
                "scope"
            ),
            rotated_count=result.get(
                "rotated_count",
                0
            ),
        )

        self.record_event(
            record
        )

        return {
            "scope": result.get("scope"),
            "rotated_count": result.get(
                "rotated_count",
                0
            )
        }

    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            QuantumDeathRippleEvent,
        ):
            raise TypeError(
                "Quantum death ripple history "
                "requires a "
                "QuantumDeathRippleEvent object."
            )

        self.history.append(
            event
        )

        return event

    @property
    def public_state(self):
        return {
            "event_count": len(
                self.history
            ),
            "history": [
                event.to_dict()
                for event in self.history
            ]
        }
