import unittest

from genesis.day0_advance_state import (
    GodBrowsingMenuAdvanceResult,
    GodFirstLilithTasteAdvanceResult,
    GodHoldingLilithAdvanceResult,
    GoodDrinkDiscussionAdvanceResult,
    LemonRestockAdvanceResult,
    LilithDrinkLearnedAdvanceResult,
    SecondWineIdeaAdvanceResult,
    ThirdWineIdeaAdvanceResult,
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


class Day0AdvanceObjectStateTests(
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

    def test_lilith_drink_learned_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_lilith_drink_learned()
        )

        self.assertIsInstance(
            result,
            LilithDrinkLearnedAdvanceResult,
        )

        self.assertEqual(
            result.vodka_with_lemon.name,
            "vodka_with_lemon",
        )

        self._assert_object_only(
            result,
            "learned",
        )

    def test_good_drink_discussion_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_good_drink_discussion()
        )

        self.assertIsInstance(
            result,
            GoodDrinkDiscussionAdvanceResult,
        )

        self.assertIs(
            result.discussion,
            scene
            .serpent_lilith_good_drink_discussion,
        )

        self._assert_object_only(
            result,
            "discussion",
        )

    def test_god_browsing_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_god_browsing_menu()
        )

        self.assertIsInstance(
            result,
            GodBrowsingMenuAdvanceResult,
        )

        self.assertEqual(
            result.looked.activity,
            "looking_around",
        )

        self.assertEqual(
            result.browsed.available_drinks,
            tuple(
                result.browsed.available_drinks
            ),
        )

        self._assert_object_only(
            result,
            "browsed",
        )

    def test_second_wine_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_second_wine_idea()
        )

        self.assertIsInstance(
            result,
            SecondWineIdeaAdvanceResult,
        )

        self.assertFalse(
            result.god.ordered
        )

        self.assertTrue(
            result
            .wine_idea
            .idea
            .desired_property
            .sweetness
        )

        self._assert_object_only(
            result,
            "wine_idea",
        )

    def test_third_wine_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_third_wine_idea()
        )

        self.assertIsInstance(
            result,
            ThirdWineIdeaAdvanceResult,
        )

        self.assertEqual(
            result.god_order.drink,
            "lilith",
        )

        self.assertTrue(
            result.wine_idea.proposal.bitterness
        )

        self._assert_object_only(
            result,
            "wine_idea",
        )

    def test_god_lilith_service_chain_is_object_only(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_god_first_lilith_taste()
        )

        self.assertIsInstance(
            result,
            GodFirstLilithTasteAdvanceResult,
        )

        self.assertIsInstance(
            result.previous,
            GodHoldingLilithAdvanceResult,
        )

        self.assertIsInstance(
            result.previous.previous,
            LemonRestockAdvanceResult,
        )

        self.assertIsInstance(
            result
            .previous
            .previous
            .previous,
            ThirdWineIdeaAdvanceResult,
        )

        self.assertTrue(
            result.tasting.effects_applied
        )

        self.assertFalse(
            result.previous.service.receipt.paid
        )

        self._assert_object_only(
            result,
            "previous",
        )

        self._assert_object_only(
            result.previous,
            "service",
        )

        self._assert_object_only(
            result.previous.previous,
            "restock",
        )


if __name__ == "__main__":
    unittest.main()
