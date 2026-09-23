import unittest

from core.entity.serpent_d20 import (
    SerpentD20,
    SerpentD20PublicRollEvent,
)


class FixedSerpentRng:

    def randint(
        self,
        minimum,
        maximum,
    ):
        return 7

    def random(self):
        return 0.5

    def sample(
        self,
        values,
        count,
    ):
        return list(values)[:count]

    def choice(
        self,
        values,
    ):
        return list(values)[0]

    def shuffle(
        self,
        values,
    ):
        return None


class SerpentD20ObjectStateTests(
    unittest.TestCase
):

    def test_public_history_uses_object_state(
        self
    ):
        die = SerpentD20()

        result = die.roll_publicly(
            rng=FixedSerpentRng(),
            universe_tick=12,
        )

        event = die.public_history[-1]

        self.assertIsInstance(
            event,
            SerpentD20PublicRollEvent,
        )
        self.assertEqual(
            event.value,
            7,
        )
        self.assertEqual(
            event.universe_tick,
            12,
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

        self.assertEqual(
            event.value,
            7,
        )

        state = die.public_state

        state[
            "public_history"
        ][0]["value"] = 99

        self.assertEqual(
            event.value,
            7,
        )

    def test_public_history_rejects_mapping_event(
        self
    ):
        die = SerpentD20()

        with self.assertRaises(TypeError):
            die.record_public_roll(
                {
                    "name": "serpent_d20_rolled",
                }
            )


if __name__ == "__main__":
    unittest.main()
