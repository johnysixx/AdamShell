import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_serpent_returns_to_bar_state import (
    LilithGodContinueTalkingAtTableEvent,
    SerpentLeavesTableForBarEvent,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0SerpentReturnsToBarObjectStateTests(
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

    def test_serpent_move_is_object_state(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_serpent_at_bar_lilith_with_god()
        )

        event = result.serpent

        self.assertIsInstance(
            event,
            SerpentLeavesTableForBarEvent,
        )

        self.assertEqual(
            event.from_location,
            "table",
        )

        self.assertEqual(
            event.to_location,
            "bar_counter",
        )

        self.assertEqual(
            event.reason,
            "nothing_good_left_to_drink",
        )

        self.assertEqual(
            event.remaining_drink,
            "bad_beer",
        )

        self.assertEqual(
            scene.serpent
            .bar_state
            .location,
            "bar_counter",
        )

        self._assert_object_only(
            event,
            "to_location",
        )

    def test_private_table_talk_is_object_state(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_serpent_at_bar_lilith_with_god()
        )

        event = result.conversation

        self.assertIsInstance(
            event,
            LilithGodContinueTalkingAtTableEvent,
        )

        self.assertEqual(
            event.participants,
            (
                "lilith",
                "god",
            ),
        )

        self.assertFalse(
            event.serpent_present
        )

        self.assertIsNone(
            event.new_conclusion
        )

        self._assert_object_only(
            event,
            "participants",
        )

    def test_history_remains_serialized_boundary(
        self
    ):
        scene = self._scene()

        scene.advance_to_serpent_at_bar_lilith_with_god()

        move = next(
            event
            for event in scene.history
            if event["name"]
            == "serpent_leaves_table_for_bar"
        )

        talk = next(
            event
            for event in scene.history
            if event["name"]
            == (
                "lilith_and_god_continue_"
                "talking_at_table"
            )
        )

        self.assertIsInstance(
            move,
            dict,
        )

        self.assertEqual(
            move["from"],
            "table",
        )

        self.assertEqual(
            move["to"],
            "bar_counter",
        )

        self.assertIsInstance(
            talk,
            dict,
        )

        self.assertEqual(
            talk["participants"],
            [
                "lilith",
                "god",
            ],
        )


if __name__ == "__main__":
    unittest.main()
