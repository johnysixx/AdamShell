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


class Day0GodLilithLemonCronenbergTests(
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

    def test_lemon_is_gone_after_liliths_drink(
        self
    ):
        self.scene.advance_to_third_wine_idea()

        lemon = (
            self.bar
            .back_room
            .bar_ingredients[
                "lemon"
            ]
        )

        self.assertEqual(
            lemon[
                "shots"
            ],
            0
        )

    def test_gods_lilith_attempt_creates_cronenberg(
        self
    ):
        self.scene.advance_to_third_wine_idea()

        result = (
            self.scene
            .bartender_attempts_gods_lilith_without_lemon()
        )

        self.assertTrue(
            result[
                "event"
            ][
                "cronenberg_created"
            ]
        )

        self.assertIsNotNone(
            result[
                "cronenberg"
            ]
        )

    def test_bartender_runs_to_yard_after_failure(
        self
    ):
        self.scene.advance_to_third_wine_idea()

        self.scene.bartender_attempts_gods_lilith_without_lemon()

        result = (
            self.scene
            .bartender_runs_to_yard_for_more_lemons(
                amount=6
            )
        )

        self.assertEqual(
            result[
                "returned"
            ][
                "amount"
            ],
            6
        )

        self.assertGreater(
            result[
                "stock"
            ][
                "shots"
            ],
            1
        )

    def test_bartender_returns_with_six_lemons_in_stock(
        self
    ):
        self.scene.advance_to_lemon_restock_after_god_order()

        lemon = (
            self.bar
            .back_room
            .bar_ingredients[
                "lemon"
            ]
        )

        self.assertEqual(
            lemon[
                "shots"
            ],
            6
        )

        self.assertTrue(
            lemon[
                "available"
            ]
        )

        self.assertEqual(
            self.bar
            .bartender
            .current_location,
            "bar"
        )

    def test_cronenberg_happens_before_restock(
        self
    ):
        self.scene.advance_to_lemon_restock_after_god_order()

        names = [
            event[
                "name"
            ]
            for event
            in self.scene.history
        ]

        failure = names.index(
            "gods_lilith_fails_without_lemon"
        )

        restock = names.index(
            "bartender_returns_with_lemon_stock"
        )

        self.assertLess(
            failure,
            restock
        )


if __name__ == "__main__":
    unittest.main()
