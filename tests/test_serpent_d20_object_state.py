import unittest

from core.entity.serpent_d20 import (
    SerpentD20,
    SerpentD20HiddenResolutionEvent,
    SerpentD20PublicRollEvent,
    SerpentResolvedConsequence,
)
from quantum.serpent_consequence_executor import (
    SerpentConsequenceExecutor,
)


class FixedSerpentRng:

    def randint(
        self,
        minimum,
        maximum,
    ):
        if maximum == 20:
            return 7

        return minimum

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


class FakeSerpentUniverse:

    def tick_quantum(self):
        return {
            "tick": 1,
        }


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


    def test_hidden_history_uses_object_state(
        self
    ):
        die = SerpentD20()

        public = die.roll_publicly(
            rng=FixedSerpentRng(),
            universe_tick=12,
        )

        event = (
            die._hidden_history[-1]
        )

        self.assertIsInstance(
            event,
            SerpentD20HiddenResolutionEvent,
        )

        self.assertEqual(
            event.roll_id,
            public["roll_id"],
        )

        self.assertEqual(
            event.value,
            7,
        )

        self.assertIsInstance(
            event.possible_consequences,
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
            _ = event["roll_id"]

        snapshot = (
            die.hidden_resolution_for(
                public["roll_id"]
            )
        )

        snapshot[
            "possible_consequences"
        ].append(
            "changed"
        )

        self.assertNotIn(
            "changed",
            event.possible_consequences,
        )

    def test_hidden_history_rejects_mapping_event(
        self
    ):
        die = SerpentD20()

        with self.assertRaises(TypeError):
            die.record_hidden_resolution(
                {
                    "name": (
                        "serpent_d20_hidden_resolution"
                    ),
                }
            )

    def test_resolved_consequences_use_object_state(
        self
    ):
        die = SerpentD20()

        public = die.roll_publicly(
            rng=FixedSerpentRng(),
        )

        executor = (
            SerpentConsequenceExecutor(
                FakeSerpentUniverse()
            )
        )

        result = (
            executor.execute_hidden_plan(
                die,
                public["roll_id"],
            )
        )

        hidden = (
            die._hidden_history[-1]
        )

        consequence = (
            hidden
            .resolved_consequences[0]
        )

        self.assertIsInstance(
            consequence,
            SerpentResolvedConsequence,
        )

        self.assertEqual(
            consequence.consequence,
            "quantum_tick",
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    consequence,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = consequence[
                "consequence"
            ]

        result[
            "resolved_consequences"
        ][0][
            "result"
        ][
            "tick"
        ] = 99

        self.assertEqual(
            consequence.result["tick"],
            1,
        )

    def test_resolved_consequences_reject_mapping_state(
        self
    ):
        die = SerpentD20()

        public = die.roll_publicly(
            rng=FixedSerpentRng(),
        )

        with self.assertRaises(TypeError):
            die.record_resolved_consequences(
                public["roll_id"],
                [
                    {
                        "consequence": (
                            "quantum_tick"
                        ),
                        "result": {
                            "tick": 1,
                        },
                    },
                ],
            )


if __name__ == "__main__":
    unittest.main()
