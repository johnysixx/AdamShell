import random
from dataclasses import dataclass

from quantum.d20_registry import D20RotationEvent


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
            result_scope = "none"
            rotated_count = 0

        elif roll < 0.95:
            result = (
                self.d20_registry
                .rotate_random(
                    rng=rng
                )
            )

            result_scope, rotated_count = (
                self._rotation_result(
                    result
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

            result_scope, rotated_count = (
                self._rotation_result(
                    result
                )
            )

        else:
            result = (
                self.d20_registry
                .rotate_all(
                    rng=rng
                )
            )

            result_scope, rotated_count = (
                self._rotation_result(
                    result
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
            result_scope=result_scope,
            rotated_count=rotated_count,
        )

        self.record_event(
            record
        )

        return record

    def _rotation_result(
        self,
        result,
    ):
        if not isinstance(
            result,
            D20RotationEvent,
        ):
            raise TypeError(
                "Quantum death ripple requires "
                "D20RotationEvent results."
            )

        return (
            result.scope,
            result.rotated_count,
        )

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
