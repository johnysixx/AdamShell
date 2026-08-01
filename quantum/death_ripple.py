import random


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

        record = {
            "event_name": event.get("name"),
            "predator": event.get(
                "payload",
                {}
            ).get("predator"),
            "prey": event.get(
                "payload",
                {}
            ).get("prey"),
            "result_scope": result.get(
                "scope"
            ),
            "rotated_count": result.get(
                "rotated_count",
                0
            )
        }

        self.history.append(record)

        return {
            "scope": result.get("scope"),
            "rotated_count": result.get(
                "rotated_count",
                0
            )
        }

    @property
    def public_state(self):
        return {
            "event_count": len(
                self.history
            ),
            "history": list(
                self.history
            )
        }
