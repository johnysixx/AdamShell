import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift
)


class Day0LilithLemonConservationTests(
    unittest.TestCase
):

    def setUp(
        self
    ):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.bar = MeetingPlace(
            self.universe
        )

        self.scene = Day0FirstBarShift(
            universe=self.universe,
            meeting_place=self.bar,
            library=Library(
                self.universe
            ),
            gods=Gods(
                self.universe
            ),
            idea_entities=IdeaEntities(
                self.universe
            )
        )

        self.scene.advance_to_lilith_entry()

        self.scene.lilith_orders_vodka_with_lemon()

        self.scene.serpent_and_lilith_begin_conversation()

        self.scene.play_serpent_lilith_first_conversation()

        self.scene.serpent_and_lilith_agree_on_table()

        self.scene.serpent_moves_from_bar_to_existing_table()

        self.scene.bartender_returns_with_lemon()

    def test_lemon_drop_does_not_consume_whole_fruit(
        self
    ):
        stock = (
            self.bar
            .back_room
            .bar_ingredients[
                "lemon"
            ]
        )

        self.assertEqual(
            stock.shots,
            1
        )

        self.scene.bartender_makes_vodka_with_lemon()

        # A drop of lemon is not the whole lemon.
        self.assertEqual(
            stock.shots,
            1
        )

    def test_final_lilith_consumes_whole_lemon(
        self
    ):
        stock = (
            self.bar
            .back_room
            .bar_ingredients[
                "lemon"
            ]
        )

        self.scene.bartender_makes_vodka_with_lemon()

        self.scene.lilith_corrects_vodka_with_lemon()

        self.scene.bartender_learns_lilith_drink()

        drink = (
            self.scene
            .bartender_mixes_final_lilith()
        )

        self.assertEqual(
            drink[
                "name"
            ],
            "lilith"
        )

        self.assertEqual(
            stock.shots,
            0
        )


if __name__ == "__main__":
    unittest.main()
