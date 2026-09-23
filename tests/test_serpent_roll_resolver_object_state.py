import unittest

from quantum.serpent_roll_resolver import (
    SerpentRollResolutionEvent,
    SerpentRollResolver,
)


class FixedResolverRng:

    def random(self):
        return 0.5

    def randint(
        self,
        minimum,
        maximum,
    ):
        return minimum

    def sample(
        self,
        values,
        count,
    ):
        return list(
            values
        )[:count]

    def choice(
        self,
        values,
    ):
        return list(
            values
        )[0]

    def shuffle(
        self,
        values,
    ):
        return None


class SerpentRollResolverObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.resolver = (
            SerpentRollResolver()
        )

    def test_history_uses_object_state(
        self
    ):
        result = self.resolver.resolve(
            public_roll={
                "name": "serpent_d20_rolled",
                "roll_id": "serpent_roll_test",
                "value": 7,
            },
            rng=FixedResolverRng(),
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            SerpentRollResolutionEvent,
        )

        self.assertEqual(
            event.roll_id,
            "serpent_roll_test",
        )

        self.assertEqual(
            event.value,
            7,
        )

        self.assertEqual(
            event.effect_count,
            1,
        )

        self.assertIsInstance(
            event.selected_effects,
            tuple,
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
            _ = event["value"]

        result["value"] = 99

        result[
            "selected_effects"
        ].append(
            "changed"
        )

        self.assertEqual(
            event.value,
            7,
        )

        self.assertNotIn(
            "changed",
            event.selected_effects,
        )

    def test_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(TypeError):
            self.resolver.record_resolution(
                {
                    "name": (
                        "serpent_roll_resolved"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
