import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_god_library_state import (
    GodBeginsFirstUnnamedBookEvent,
    GodBornEvent,
    GodEnteredBarEvent,
    GodEnteredLibraryEvent,
    GodLeftLibraryEvent,
    GodLibraryDepartureResult,
    GodLibraryOpeningResult,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0GodLibraryObjectStateTests(
    unittest.TestCase
):

    def _scene(self):
        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

        return Day0FirstBarShift(
            universe=universe,
            meeting_place=MeetingPlace(
                universe
            ),
            library=Library(
                universe
            ),
            gods=Gods(
                universe
            ),
            idea_entities=IdeaEntities(
                universe
            ),
        )

    def _assert_object_only(
        self,
        value,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "setdefault",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[key]

    def _advance_to_god_birth(
        self,
        scene,
    ):
        scene.start_shift()
        scene.serpent_is_born_and_enters()
        scene.serpent_orders_first_drinks()
        scene.serpent_proposes_bet()

        return (
            scene
            .god_is_born_and_goes_to_library()
        )

    def test_library_opening_is_object_graph(
        self
    ):
        scene = self._scene()

        result = (
            self._advance_to_god_birth(
                scene
            )
        )

        self.assertIsInstance(
            result,
            GodLibraryOpeningResult,
        )

        self.assertIs(
            result.god,
            scene.god,
        )

        self.assertIs(
            result.book,
            scene.first_book,
        )

        self.assertIsInstance(
            result.born,
            GodBornEvent,
        )

        self.assertIsInstance(
            result.entered,
            GodEnteredLibraryEvent,
        )

        self.assertIsInstance(
            result.began_book,
            GodBeginsFirstUnnamedBookEvent,
        )

        self.assertEqual(
            result.entered.door_sign,
            "GOD IS: IN",
        )

        self.assertIsNone(
            result.began_book.title
        )

        self.assertEqual(
            result.began_book.state,
            "being_written",
        )

        self.assertEqual(
            result.began_book.location,
            "library_with_author",
        )

        self._assert_object_only(
            result,
            "book",
        )

        self._assert_object_only(
            result.born,
            "name",
        )

        self._assert_object_only(
            result.entered,
            "door_sign",
        )

        self._assert_object_only(
            result.began_book,
            "state",
        )

    def test_first_book_remains_real_object(
        self
    ):
        scene = self._scene()

        result = (
            self._advance_to_god_birth(
                scene
            )
        )

        self.assertIsNone(
            result.book.title
        )

        self.assertEqual(
            result.book.entries,
            [],
        )

        self.assertEqual(
            result.book.state,
            "being_written",
        )

        self.assertEqual(
            result.book.location,
            "library_with_author",
        )

        self.assertTrue(
            scene.library.god_present
        )

    def test_library_departure_is_object_graph(
        self
    ):
        scene = self._scene()

        self._advance_to_god_birth(
            scene
        )

        result = (
            scene
            .god_leaves_library_and_enters_bar()
        )

        self.assertIsInstance(
            result,
            GodLibraryDepartureResult,
        )

        self.assertIs(
            result.god,
            scene.god,
        )

        self.assertIs(
            result.book,
            scene.first_book,
        )

        self.assertIsInstance(
            result.left,
            GodLeftLibraryEvent,
        )

        self.assertIsInstance(
            result.entered_bar,
            GodEnteredBarEvent,
        )

        self.assertEqual(
            result.left.source,
            "library",
        )

        self.assertEqual(
            result.entered_bar.source,
            "library",
        )

        self.assertEqual(
            result.entered_bar.destination,
            "bar",
        )

        self.assertFalse(
            scene.library.god_present
        )

        self.assertIn(
            result.god,
            scene.meeting_place.entities,
        )

        self._assert_object_only(
            result,
            "god",
        )

        self._assert_object_only(
            result.left,
            "source",
        )

        self._assert_object_only(
            result.entered_bar,
            "destination",
        )

    def test_departure_leaves_empty_book_in_library(
        self
    ):
        scene = self._scene()

        self._advance_to_god_birth(
            scene
        )

        result = (
            scene
            .god_leaves_library_and_enters_bar()
        )

        self.assertEqual(
            result.book.entries,
            [],
        )

        self.assertIsNone(
            result.book.title
        )

        self.assertEqual(
            result.book.state,
            "being_written",
        )

        self.assertEqual(
            result.book.location,
            "library",
        )

        self.assertIn(
            result.book,
            scene.library.books,
        )

    def test_history_remains_serialized_boundary(
        self
    ):
        scene = self._scene()

        self._advance_to_god_birth(
            scene
        )

        scene.god_leaves_library_and_enters_bar()

        names = [
            event["name"]
            for event
            in scene.checkpoint()["history"]
        ]

        self.assertIn(
            "god_born",
            names,
        )

        self.assertIn(
            "god_entered_library",
            names,
        )

        self.assertIn(
            "god_begins_first_unnamed_book",
            names,
        )

        self.assertIn(
            "god_left_library",
            names,
        )

        self.assertIn(
            "god_entered_bar",
            names,
        )

        left = next(
            event
            for event
            in scene.checkpoint()["history"]
            if event["name"]
            == "god_left_library"
        )

        self.assertEqual(
            left,
            {
                "name":
                    "god_left_library",
            },
        )


if __name__ == "__main__":
    unittest.main()
