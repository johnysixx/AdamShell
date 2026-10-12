import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_first_conversation_state import (
    FirstBarDrinkReactionState,
    LilithAcceptsDrinkWagerEvent,
    SerpentLilithAgreeOnTableEvent,
    SerpentLilithConversationStartedEvent,
    SerpentLilithFirstConversationResult,
    SerpentLilithFirstDrinksTastedEvent,
    SerpentMovesToExistingTableEvent,
    SerpentProposesDrinkWagerEvent,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0FirstConversationObjectStateTests(
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

        scene.advance_to_lilith_entry()

        scene.lilith_orders_vodka_with_lemon()

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

    def test_conversation_start_is_object_only(
        self
    ):
        scene = self._scene()

        event = (
            scene
            .serpent_and_lilith_begin_conversation()
        )

        self.assertIsInstance(
            event,
            SerpentLilithConversationStartedEvent,
        )

        self.assertFalse(
            event.bartender_present
        )

        self._assert_object_only(
            event,
            "bartender_present",
        )

    def test_first_tasting_keeps_typed_reactions(
        self
    ):
        scene = self._scene()

        scene.serpent_and_lilith_begin_conversation()

        event = (
            scene
            .serpent_and_lilith_taste_first_drinks()
        )

        self.assertIsInstance(
            event,
            SerpentLilithFirstDrinksTastedEvent,
        )

        self.assertIsInstance(
            event.serpent_reaction,
            FirstBarDrinkReactionState,
        )

        self.assertIs(
            scene.serpent.first_bar_drink_tasting,
            event.serpent_reaction,
        )

        self.assertIs(
            scene.lilith.first_bar_drink_tasting,
            event.lilith_reaction,
        )

        self._assert_object_only(
            event.serpent_reaction,
            "wine",
        )

    def test_wager_events_capture_detached_object_snapshots(
        self
    ):
        scene = self._scene()

        scene.serpent_and_lilith_begin_conversation()

        scene.serpent_and_lilith_taste_first_drinks()

        wager = (
            scene
            .serpent_proposes_drink_wager_to_lilith()
        )

        proposal = (
            scene.meeting_place.events[-1]
        )

        self.assertIsInstance(
            proposal,
            SerpentProposesDrinkWagerEvent,
        )

        self.assertFalse(
            proposal.wager.accepted
        )

        scene.lilith_accepts_drink_wager()

        accepted = (
            scene.meeting_place.events[-1]
        )

        self.assertIsInstance(
            accepted,
            LilithAcceptsDrinkWagerEvent,
        )

        self.assertFalse(
            proposal.wager.accepted
        )

        self.assertTrue(
            accepted.wager.accepted
        )

        self.assertTrue(
            wager.accepted
        )

        self._assert_object_only(
            proposal.wager,
            "accepted",
        )

    def test_first_conversation_result_is_object_only(
        self
    ):
        scene = self._scene()

        scene.serpent_and_lilith_begin_conversation()

        result = (
            scene
            .play_serpent_lilith_first_conversation()
        )

        self.assertIsInstance(
            result,
            SerpentLilithFirstConversationResult,
        )

        self.assertIs(
            result.wager,
            result.accepted,
        )

        self.assertTrue(
            result.wager.accepted
        )

        self._assert_object_only(
            result,
            "wager",
        )

    def test_table_agreement_and_move_are_objects(
        self
    ):
        scene = self._scene()

        scene.serpent_and_lilith_begin_conversation()

        scene.play_serpent_lilith_first_conversation()

        agreement = (
            scene
            .serpent_and_lilith_agree_on_table()
        )

        movement = (
            scene
            .serpent_moves_from_bar_to_existing_table()
        )

        self.assertIsInstance(
            agreement,
            SerpentLilithAgreeOnTableEvent,
        )

        self.assertIsInstance(
            movement,
            SerpentMovesToExistingTableEvent,
        )

        self.assertTrue(
            agreement.agreed
        )

        self.assertEqual(
            movement.source,
            "bar_counter",
        )

        self.assertEqual(
            scene.serpent.bar_state.location,
            "table",
        )

        self._assert_object_only(
            movement,
            "source",
        )


if __name__ == "__main__":
    unittest.main()
