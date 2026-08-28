import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe

from meeting_place.meeting_place import (
    MeetingPlace
)
from library import Library
from gods import Gods
from idea_entities import IdeaEntities

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift
)


class Day0GodLilithSerpentCheckpointTests(
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

        self.library = Library(
            self.universe
        )

        self.gods = Gods(
            self.universe
        )

        self.idea_entities = IdeaEntities(
            self.universe
        )

        self.scene = Day0FirstBarShift(
            universe=self.universe,
            meeting_place=self.bar,
            library=self.library,
            gods=self.gods,
            idea_entities=self.idea_entities
        )

    def test_god_first_book_is_empty_and_unnamed(
        self
    ):
        self.scene.start_shift()
        self.scene.serpent_is_born_and_enters()
        self.scene.serpent_orders_first_drinks()
        self.scene.serpent_proposes_bet()

        result = (
            self.scene
            .god_is_born_and_goes_to_library()
        )

        book = result[
            "book"
        ]

        self.assertIsNone(
            book[
                "title"
            ]
        )

        self.assertEqual(
            book[
                "entries"
            ],
            []
        )

    def test_lilith_order_sends_bartender_to_lemon_tree(
        self
    ):
        self.scene.advance_to_lilith_entry()

        result = (
            self.scene
            .lilith_orders_vodka_with_lemon()
        )

        self.assertEqual(
            result[
                "order"
            ][
                "drink"
            ],
            "vodka_with_lemon"
        )

        self.assertFalse(
            result[
                "order"
            ][
                "served"
            ]
        )

        self.assertEqual(
            self.bar.bartender.current_location,
            "bar_yard"
        )

        self.assertEqual(
            self.bar.bartender.regular_drinks[
                "lilith"
            ],
            "vodka_with_lemon"
        )

    def test_god_leaves_empty_book_and_enters_bar(
        self
    ):
        self.scene.advance_to_lilith_entry()

        god = (
            self.scene
            .god_leaves_library_and_enters_bar()
        )

        self.assertFalse(
            self.library.god_present
        )

        self.assertIn(
            god,
            self.bar.entities
        )

        self.assertEqual(
            self.scene.first_book[
                "entries"
            ],
            []
        )

        self.assertIsNone(
            self.scene.first_book[
                "title"
            ]
        )

        self.assertEqual(
            self.scene.first_book[
                "location"
            ],
            "library"
        )

    def test_serpent_and_lilith_start_talking_while_bartender_is_away(
        self
    ):
        self.scene.advance_to_lilith_entry()

        self.scene.lilith_orders_vodka_with_lemon()

        event = (
            self.scene
            .serpent_and_lilith_begin_conversation()
        )

        self.assertTrue(
            self.scene
            .serpent_lilith_conversation[
                "started"
            ]
        )

        self.assertEqual(
            self.scene
            .serpent_lilith_conversation[
                "participants"
            ],
            [
                "serpent",
                "lilith"
            ]
        )

        self.assertEqual(
            self.scene
            .serpent_lilith_conversation[
                "content"
            ],
            []
        )

        self.assertFalse(
            event[
                "bartender_present"
            ]
        )


if __name__ == "__main__":
    unittest.main()
