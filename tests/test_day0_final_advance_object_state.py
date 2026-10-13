import unittest

from genesis.day0_advance_state import (
    BartenderBouncerPanelAdvanceResult,
    BouncerAcceptsJudgeAdvanceResult,
    BouncerInsideAdvanceResult,
    BouncerKnowsWagerAdvanceResult,
    CatD20ArrivalAdvanceResult,
    EveryoneAtBarWithWaterAdvanceResult,
    FirstPrivateConversationAdvanceResult,
    GarfieldArrivalAdvanceResult,
    SerpentAtBarAdvanceResult,
    WagerVoteProposalAdvanceResult,
)
from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0FinalAdvanceObjectStateTests(
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

    def test_first_private_conversation_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_first_private_conversation()
        )

        self.assertIsInstance(
            result,
            FirstPrivateConversationAdvanceResult,
        )

        self.assertIsInstance(
            result.previous_checkpoint,
            dict,
        )

        self.assertIsInstance(
            result.current,
            dict,
        )

        self.assertEqual(
            result.conversation.participants,
            (
                "serpent",
                "lilith",
            ),
        )

        self.assertFalse(
            result.conversation.bartender_present
        )

        self._assert_object_only(
            result,
            "conversation",
        )

    def test_serpent_return_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_serpent_at_bar_lilith_with_god()
        )

        self.assertIsInstance(
            result,
            SerpentAtBarAdvanceResult,
        )

        self.assertEqual(
            result.serpent.to_location,
            "bar_counter",
        )

        self.assertEqual(
            result.conversation.participants,
            (
                "lilith",
                "god",
            ),
        )

        self._assert_object_only(
            result,
            "serpent",
        )

    def test_vote_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_wager_vote_proposal()
        )

        self.assertIsInstance(
            result,
            WagerVoteProposalAdvanceResult,
        )

        self.assertEqual(
            result.question.question,
            "who_decides_winner",
        )

        self.assertEqual(
            result
            .proposal
            .decision_method
            .type,
            "participant_vote",
        )

        self._assert_object_only(
            result,
            "proposal",
        )

    def test_water_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_everyone_at_bar_with_serpents_water()
        )

        self.assertIsInstance(
            result,
            EveryoneAtBarWithWaterAdvanceResult,
        )

        self.assertEqual(
            result.water_order.drink,
            "water",
        )

        self.assertEqual(
            result.water.drink.name,
            "water_with_lemon_slice",
        )

        self._assert_object_only(
            result,
            "water",
        )

    def test_panel_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_bartender_bouncer_panel_proposal()
        )

        self.assertIsInstance(
            result,
            BartenderBouncerPanelAdvanceResult,
        )

        self.assertEqual(
            result
            .panel
            .proposal
            .type,
            "tasting_panel",
        )

        self._assert_object_only(
            result,
            "panel",
        )

    def test_cat_d20_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_cat_d20_arrival()
        )

        self.assertIsInstance(
            result,
            CatD20ArrivalAdvanceResult,
        )

        self.assertIs(
            result.cat_d20.cat,
            scene.cat_d20,
        )

        self._assert_object_only(
            result,
            "cat_d20",
        )

    def test_garfield_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_garfield_arrival()
        )

        self.assertIsInstance(
            result,
            GarfieldArrivalAdvanceResult,
        )

        self.assertEqual(
            result.prepared.target_name,
            "garfield",
        )

        self.assertIs(
            result.garfield.garfield,
            scene.garfield,
        )

        self.assertIsInstance(
            result.scratches,
            tuple,
        )

        self._assert_object_only(
            result,
            "garfield",
        )

    def test_bouncer_entry_and_knowledge_are_objects(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_bouncer_knows_wager()
        )

        self.assertIsInstance(
            result,
            BouncerKnowsWagerAdvanceResult,
        )

        self.assertIsInstance(
            result.previous,
            BouncerInsideAdvanceResult,
        )

        self.assertEqual(
            result.explanation.speaker,
            "serpent",
        )

        self._assert_object_only(
            result,
            "explanation",
        )

    def test_judge_wrapper_closes_advance_chain(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_bouncer_accepts_judge_role()
        )

        self.assertIsInstance(
            result,
            BouncerAcceptsJudgeAdvanceResult,
        )

        self.assertIsInstance(
            result.previous,
            BouncerKnowsWagerAdvanceResult,
        )

        self.assertIsInstance(
            result
            .previous
            .previous
            .previous,
            GarfieldArrivalAdvanceResult,
        )

        self.assertTrue(
            result.tasting.accepted.accepted
        )

        self.assertIs(
            result.tasting.receipt,
            result.service.receipt,
        )

        self.assertIsInstance(
            result.garfield_scratches,
            tuple,
        )

        self._assert_object_only(
            result,
            "tasting",
        )


if __name__ == "__main__":
    unittest.main()
