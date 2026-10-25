import unittest

from meeting_place.dice_vial import (
    DiceVial,
    DiceVialSecretRotationEvent,
)
from quantum.d20_registry import (
    D20Registry,
    D20RotationEvent,
)


class FakeArtifact:

    def __init__(
        self,
        name,
        layer=None,
    ):
        self.name = name
        self.layer = layer

    def roll(
        self,
        rng=None,
    ):
        return {
            "artifact": self.name,
            "nested": {
                "value": 7,
            },
        }


class FirstChoiceRng:

    def choice(
        self,
        values,
    ):
        return list(
            values
        )[0]


class D20RegistryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.registry = D20Registry()

        self.first = FakeArtifact(
            "first_die",
            layer="eden",
        )

        self.second = FakeArtifact(
            "second_die",
            layer="history",
        )

        self.registry.register(
            self.first
        )

        self.registry.register(
            self.second
        )

    def test_random_rotation_history_uses_object_state(
        self
    ):
        result = (
            self.registry
            .rotate_random(
                rng=FirstChoiceRng()
            )
        )

        event = (
            self.registry
            .rotation_history[-1]
        )

        self.assertIsInstance(
            event,
            D20RotationEvent,
        )

        self.assertEqual(
            event.scope,
            "random",
        )

        self.assertEqual(
            event.artifact_names,
            (
                "first_die",
            ),
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
            _ = event["scope"]

        snapshot = result.to_dict()

        snapshot[
            "results"
        ][0][
            "nested"
        ][
            "value"
        ] = 99

        self.assertEqual(
            event.results[0][
                "nested"
            ][
                "value"
            ],
            7,
        )

        with self.assertRaises(
            TypeError
        ):
            event.results[0][
                "nested"
            ][
                "value"
            ] = 99

    def test_layer_rotation_returns_object_state(
        self
    ):
        result = (
            self.registry
            .rotate_layer(
                "eden"
            )
        )

        event = (
            self.registry
            .rotation_history[-1]
        )

        self.assertIsInstance(
            event,
            D20RotationEvent,
        )

        self.assertEqual(
            event.scope,
            "layer",
        )

        self.assertEqual(
            event.layer,
            "eden",
        )

        self.assertIs(
            result,
            event,
        )

        self.assertEqual(
            result.layer,
            "eden",
        )

        self.assertEqual(
            result.artifact_names,
            (
                "first_die",
            ),
        )

    def test_all_rotation_history_uses_object_state(
        self
    ):
        result = (
            self.registry
            .rotate_all()
        )

        event = (
            self.registry
            .rotation_history[-1]
        )

        self.assertIsInstance(
            event,
            D20RotationEvent,
        )

        self.assertEqual(
            event.scope,
            "all",
        )

        self.assertEqual(
            event.rotated_count,
            2,
        )

        self.assertIs(
            result,
            event,
        )

        self.assertEqual(
            result.rotated_count,
            2,
        )

    def test_vial_rotation_keeps_object_result(self):
        registry = D20Registry()
        vial = DiceVial()
        registry.register(vial)

        class FixedRng:
            def randint(self, minimum, maximum):
                return 7

            def choice(self, values):
                return list(values)[0]

        result = registry.rotate_random(
            rng=FixedRng()
        )

        self.assertIsInstance(
            result,
            D20RotationEvent,
        )
        self.assertIsInstance(
            result.results[0],
            DiceVialSecretRotationEvent,
        )
        self.assertIs(
            result.results[0],
            vial.secret_event,
        )

        snapshot = result.to_dict()
        self.assertIsInstance(
            snapshot["results"][0],
            dict,
        )
        self.assertEqual(
            snapshot["results"][0]["roll"],
            7,
        )

        snapshot["results"][0]["roll"] = 99

        self.assertEqual(
            result.results[0].roll,
            7,
        )

    def test_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(TypeError):
            self.registry.record_rotation(
                {
                    "scope": "all",
                }
            )


if __name__ == "__main__":
    unittest.main()
