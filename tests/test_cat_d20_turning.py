import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from universe.bootstraps.entity_bootstrap import (
    EntityBootstrap
)
from meeting_place.bar_objects import (
    CatD20TurnEvent,
)
from meeting_place.cat_d20_turn_state import (
    CatD20TurnResult,
    CatD20ValueInterpretation,
)


class FixedD20:

    def __init__(self, value):
        self.value = value

    def randint(self, minimum, maximum):
        return self.value


class CatD20TurningTests(unittest.TestCase):

    def setUp(self):
        registry = UniverseRegistry()
        self.universe = Universe()

        (
            root_transition,
            layers,
            idea_universe
        ) = UniverseBootstrap(
            registry,
            self.universe
        ).run()

        EntityBootstrap(
            self.universe,
            idea_universe,
            root_transition
        ).run()

        self.bar = layers.get(
            "meeting"
        )

        self.arrival = (
            self.bar.welcome_cat_d20()
        )

        self.cat = self.arrival.cat

    def test_cat_d20_turn_is_secret(self):
        bar_events_before = len(
            self.bar.events
        )

        stories_before = len(
            self.bar
            .bar_counter
            .hidden_story_book
            .entries
        )

        bartender_memory_before = len(
            self.bar.bartender.event_memory
        )

        turn = self.bar.turn_cat_d20_in_box(
            rng=FixedD20(17)
        )

        self.assertIsInstance(
            turn,
            CatD20TurnResult,
        )

        self.assertEqual(
            turn.value,
            17
        )

        self.assertFalse(
            turn.was_thrown
        )

        self.assertIsInstance(
            turn.interpretation,
            CatD20ValueInterpretation,
        )

        self.assertEqual(
            turn.interpretation.meaning,
            "decline_navigation_offer",
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    turn,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = turn[
                "value"
            ]

        self.assertEqual(
            len(self.bar.events),
            bar_events_before
        )

        self.assertEqual(
            len(
                self.bar
                .bar_counter
                .hidden_story_book
                .entries
            ),
            stories_before
        )

        self.assertEqual(
            len(
                self.bar
                .bartender
                .event_memory
            ),
            bartender_memory_before
        )

        self.assertEqual(
            len(
                self.bar
                .cat_d20_secret_history
            ),
            1
        )

        secret = (
            self.bar
            .cat_d20_secret_history[-1]
        )

        quantum = (
            self.universe
            .quantum_events[-1]
        )

        self.assertIsInstance(
            secret,
            CatD20TurnEvent,
        )

        self.assertIsInstance(
            quantum,
            CatD20TurnEvent,
        )

        self.assertEqual(
            secret.value,
            17
        )

        with self.assertRaises(
            TypeError
        ):
            _ = secret[
                "value"
            ]

    def test_cat_d20_value_meanings(self):
        expected = {
            1: "accept_navigation_offer",
            14: "accept_navigation_offer",
            15: "decline_navigation_offer",
            18: "decline_navigation_offer",
            19: "cat_does_something_else",
            20: "cat_d20_surge"
        }

        for value, meaning in expected.items():
            with self.subTest(
                value=value
            ):
                result = (
                    self.bar
                    .interpret_cat_d20_value(
                        value
                    )
                )

                self.assertIsInstance(
                    result,
                    CatD20ValueInterpretation,
                )

                self.assertEqual(
                    result.meaning,
                    meaning
                )

                self.assertFalse(
                    hasattr(
                        result,
                        "to_dict",
                    )
                )

                with self.assertRaises(
                    TypeError
                ):
                    _ = result[
                        "meaning"
                    ]

    def test_invalid_cat_d20_value_is_rejected(self):
        for value in (
            0,
            21
        ):
            with self.subTest(
                value=value
            ):
                with self.assertRaises(
                    ValueError
                ):
                    self.bar.interpret_cat_d20_value(
                        value
                    )


if __name__ == "__main__":
    unittest.main()
