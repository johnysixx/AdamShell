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


class Day0GodArrivesDuringWineDiscussionTests(
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

        self.scene.advance_to_good_drink_discussion()

        self.scene.lilith_and_serpent_take_first_table_drinks()

        self.scene.lilith_and_serpent_make_first_wine_observation()

    def test_god_is_still_in_library_before_arrival(
        self
    ):
        self.assertTrue(
            self.scene.library.god_present
        )

        self.assertNotIn(
            self.scene.god,
            self.bar.entities
        )

    def test_god_arrives_after_first_wine_observation(
        self
    ):
        god = (
            self.scene
            .god_arrives_after_first_wine_observation()
        )

        self.assertIn(
            god,
            self.bar.entities
        )

        self.assertFalse(
            self.scene.library.god_present
        )

        self.assertEqual(
            self.scene.first_book[
                "location"
            ],
            "library"
        )

        self.assertEqual(
            self.scene.first_book[
                "entries"
            ],
            []
        )

    def test_god_arrival_is_after_fuller_flavor_observation(
        self
    ):
        self.scene.god_arrives_after_first_wine_observation()

        names = [
            event[
                "name"
            ]
            for event
            in self.scene.history
        ]

        observation_index = names.index(
            "first_good_wine_observation"
        )

        arrival_index = names.index(
            "god_arrives_during_wine_discussion"
        )

        self.assertLess(
            observation_index,
            arrival_index
        )


if __name__ == "__main__":
    unittest.main()
