import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_table_wine_state import (
    FirstGoodWineObservationEvent,
    FirstTableDrinksResult,
    GodArrivesDuringWineDiscussionEvent,
    GodBrowsesDrinkMenuEvent,
    GodLooksAroundBarEvent,
    LilithTakesFirstTableSipEvent,
    SerpentFinishesWineAtTableEvent,
    SerpentLilithContinueWineDiscussionEvent,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0TableWineObjectStateTests(
    unittest.TestCase
):

    def _scene(self):
        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

        scene = Day0FirstBarShift(
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

        scene.advance_to_good_drink_discussion()

        return scene

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

    def test_first_table_drinks_are_object_only(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .lilith_and_serpent_take_first_table_drinks()
        )

        self.assertIsInstance(
            result,
            FirstTableDrinksResult,
        )

        self.assertIsInstance(
            result.lilith,
            LilithTakesFirstTableSipEvent,
        )

        self.assertIsInstance(
            result.serpent,
            SerpentFinishesWineAtTableEvent,
        )

        self.assertTrue(
            result.serpent.finished
        )

        self._assert_object_only(
            result,
            "serpent",
        )

    def test_first_wine_observation_emits_object_event(
        self
    ):
        scene = self._scene()

        scene.lilith_and_serpent_take_first_table_drinks()

        observation = (
            scene
            .lilith_and_serpent_make_first_wine_observation()
        )

        event = (
            scene.meeting_place.events[-1]
        )

        self.assertIsInstance(
            event,
            FirstGoodWineObservationEvent,
        )

        self.assertEqual(
            observation
            .serpent
            .proposal,
            "flavor_should_be_fuller",
        )

        self.assertEqual(
            event.desired_flavor,
            "fuller",
        )

        self._assert_object_only(
            event,
            "desired_flavor",
        )

    def test_god_arrival_emits_object_event(
        self
    ):
        scene = self._scene()

        scene.lilith_and_serpent_take_first_table_drinks()

        scene.lilith_and_serpent_make_first_wine_observation()

        god = (
            scene
            .god_arrives_after_first_wine_observation()
        )

        event = (
            scene.meeting_place.events[-1]
        )

        self.assertIsInstance(
            event,
            GodArrivesDuringWineDiscussionEvent,
        )

        self.assertIs(
            god,
            scene.god,
        )

        self.assertEqual(
            event.source,
            "library",
        )

        self.assertEqual(
            event.destination,
            "bar",
        )

        self._assert_object_only(
            event,
            "source",
        )

    def test_god_menu_flow_uses_object_events(
        self
    ):
        scene = self._scene()

        scene.lilith_and_serpent_take_first_table_drinks()

        scene.lilith_and_serpent_make_first_wine_observation()

        scene.god_arrives_after_first_wine_observation()

        looked = (
            scene.god_looks_around_bar()
        )

        continued = (
            scene
            .serpent_and_lilith_continue_wine_discussion()
        )

        browsed = (
            scene.god_moves_to_drink_menu()
        )

        self.assertIsInstance(
            looked,
            GodLooksAroundBarEvent,
        )

        self.assertIsInstance(
            continued,
            SerpentLilithContinueWineDiscussionEvent,
        )

        self.assertIsInstance(
            browsed,
            GodBrowsesDrinkMenuEvent,
        )

        self.assertEqual(
            looked.activity,
            "looking_around",
        )

        self.assertEqual(
            continued.subject,
            "wine",
        )

        self.assertIsNone(
            continued.new_idea
        )

        self.assertIsInstance(
            browsed.available_drinks,
            tuple,
        )

        self._assert_object_only(
            looked,
            "activity",
        )

        self._assert_object_only(
            continued,
            "subject",
        )

        self._assert_object_only(
            browsed,
            "available_drinks",
        )


if __name__ == "__main__":
    unittest.main()
