import unittest

from quantum.event_bus import QuantumEvent
from quantum.death_ripple import (
    QuantumDeathRipple,
    QuantumDeathRippleEvent,
)
from quantum.d20_registry import (
    D20RotationEvent,
)


class FixedRng:

    def random(self):
        return 0.5


class FakeD20Registry:

    def rotate_random(
        self,
        rng=None,
    ):
        return D20RotationEvent(
            scope="random",
            rotated_count=1,
            artifact_names=("random_die",),
            results=(None,),
        )

    def rotate_layer(
        self,
        layer,
    ):
        return D20RotationEvent(
            scope="layer",
            layer=layer,
            rotated_count=2,
            artifact_names=(
                "layer_die_1",
                "layer_die_2",
            ),
            results=(None, None),
        )

    def rotate_all(
        self,
        rng=None,
    ):
        return D20RotationEvent(
            scope="all",
            rotated_count=3,
            artifact_names=(
                "die_1",
                "die_2",
                "die_3",
            ),
            results=(None, None, None),
        )


class QuantumDeathRippleObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.ripple = QuantumDeathRipple(
            FakeD20Registry()
        )

    def test_history_uses_object_state(
        self
    ):
        result = (
            self.ripple
            .on_cronenberg_hunted(
                QuantumEvent(
                    name="cronenberg_hunted",
                    payload={
                        "predator": "cat",
                        "prey": "cronenberg",
                    },
                ),
                rng=FixedRng(),
            )
        )

        event = (
            self.ripple
            .history[-1]
        )

        self.assertIsInstance(
            event,
            QuantumDeathRippleEvent,
        )

        self.assertEqual(
            event.predator,
            "cat",
        )
        self.assertEqual(
            event.prey,
            "cronenberg",
        )
        self.assertEqual(
            event.result_scope,
            "none",
        )
        self.assertEqual(
            event.rotated_count,
            0,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = event["predator"]

        self.assertIs(
            result,
            event,
        )

        snapshot = result.to_dict()
        snapshot[
            "rotated_count"
        ] = 99

        self.assertEqual(
            event.rotated_count,
            0,
        )

    def test_public_state_serializes_history(
        self
    ):
        self.ripple.on_cronenberg_hunted(
            QuantumEvent(
                name="cronenberg_hunted",
                payload={},
            ),
            rng=FixedRng(),
        )

        event = (
            self.ripple
            .history[-1]
        )

        state = (
            self.ripple
            .public_state
        )

        state[
            "history"
        ][0][
            "rotated_count"
        ] = 99

        self.assertEqual(
            event.rotated_count,
            0,
        )

    def test_handler_rejects_mapping_event(self):
        with self.assertRaisesRegex(
            TypeError,
            "QuantumEvent",
        ):
            self.ripple.on_cronenberg_hunted(
                {
                    "name": "cronenberg_hunted",
                    "payload": {},
                },
                rng=FixedRng(),
            )

        self.assertEqual(self.ripple.history, [])

    def test_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(TypeError):
            self.ripple.record_event(
                {
                    "event_name": (
                        "legacy_mapping"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
