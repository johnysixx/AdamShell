import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from universe.bootstraps.entity_bootstrap import (
    EntityBootstrap
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

        self.cat = self.arrival["cat"]

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

        self.assertEqual(
            turn["value"],
            17
        )

        self.assertFalse(
            turn["was_thrown"]
        )

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

                self.assertEqual(
                    result["meaning"],
                    meaning
                )

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