import unittest

from quantum.death_ripple import (
    QuantumDeathRipple,
    QuantumDeathRippleEvent,
)


class FixedRng:

    def random(self):
        return 0.5


class FakeD20Registry:

    def rotate_random(
        self,
        rng=None,
    ):
        return {
            "scope": "random",
            "rotated_count": 1,
        }

    def rotate_layer(
        self,
        layer,
    ):
        return {
            "scope": layer,
            "rotated_count": 2,
        }

    def rotate_all(
        self,
        rng=None,
    ):
        return {
            "scope": "all",
            "rotated_count": 3,
        }


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
                {
                    "name": (
                        "cronenberg_hunted"
                    ),
                    "payload": {
                        "predator": "cat",
                        "prey": "cronenberg",
                    },
                },
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

        result[
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
            {
                "name": (
                    "cronenberg_hunted"
                ),
                "payload": {},
            },
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
