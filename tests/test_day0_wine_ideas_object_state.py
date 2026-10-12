import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_wine_ideas_state import (
    BartenderAsksGodForOrderEvent,
    GodOrdersLilithEvent,
    GodStillChoosingEvent,
    LilithSweetnessWineIdeaResult,
    LilithTastesMeadEvent,
    SerpentMeadBeerTastingResult,
    SerpentTastesBeerEvent,
    SerpentTastesMeadEvent,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0WineIdeasObjectStateTests(
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

    def test_order_question_and_answer_are_objects(
        self
    ):
        scene = self._scene()

        scene.advance_to_god_browsing_menu()

        asked = (
            scene.bartender_asks_god_for_order()
        )

        answer = (
            scene.god_says_still_choosing()
        )

        self.assertIsInstance(
            asked,
            BartenderAsksGodForOrderEvent,
        )

        self.assertIsInstance(
            answer,
            GodStillChoosingEvent,
        )

        self.assertEqual(
            asked.question,
            "what_will_you_have",
        )

        self.assertFalse(
            answer.ordered
        )

        self._assert_object_only(
            asked,
            "question",
        )

        self._assert_object_only(
            answer,
            "ordered",
        )

    def test_lilith_sweetness_result_is_object_only(
        self
    ):
        scene = self._scene()

        scene.advance_to_god_browsing_menu()

        scene.bartender_asks_god_for_order()
        scene.god_says_still_choosing()

        result = (
            scene
            .lilith_tastes_mead_and_adds_sweetness_idea()
        )

        self.assertIsInstance(
            result,
            LilithSweetnessWineIdeaResult,
        )

        self.assertIsInstance(
            result.tasting,
            LilithTastesMeadEvent,
        )

        self.assertEqual(
            result.tasting.drink,
            "mead",
        )

        self.assertEqual(
            result.idea.subject,
            "wine",
        )

        self.assertTrue(
            result
            .idea
            .desired_property
            .sweetness
        )

        self._assert_object_only(
            result,
            "idea",
        )

    def test_god_order_is_object_only(
        self
    ):
        scene = self._scene()

        scene.advance_to_second_wine_idea()

        event = (
            scene
            .god_finishes_browsing_and_orders_lilith()
        )

        self.assertIsInstance(
            event,
            GodOrdersLilithEvent,
        )

        self.assertEqual(
            event.drink,
            "lilith",
        )

        self.assertEqual(
            scene.god.bar_state.activity,
            "ordered_lilith",
        )

        self._assert_object_only(
            event,
            "drink",
        )

    def test_serpent_mead_beer_tasting_is_object_only(
        self
    ):
        scene = self._scene()

        scene.advance_to_second_wine_idea()

        scene.god_finishes_browsing_and_orders_lilith()

        result = (
            scene
            .serpent_tastes_mead_then_beer()
        )

        self.assertIsInstance(
            result,
            SerpentMeadBeerTastingResult,
        )

        self.assertIsInstance(
            result.mead,
            SerpentTastesMeadEvent,
        )

        self.assertIsInstance(
            result.beer,
            SerpentTastesBeerEvent,
        )

        self.assertEqual(
            result.mead.drink,
            "mead",
        )

        self.assertEqual(
            result.beer.drink,
            "beer",
        )

        self._assert_object_only(
            result,
            "mead",
        )

    def test_third_wine_idea_remains_domain_object(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_third_wine_idea()
        )

        idea = result[
            "wine_idea"
        ]

        self.assertEqual(
            idea.assessment.sweetness,
            "good",
        )

        self.assertEqual(
            idea.assessment.full_body,
            "still_missing",
        )

        self.assertTrue(
            idea.proposal.bitterness
        )

        self._assert_object_only(
            idea,
            "proposal",
        )


if __name__ == "__main__":
    unittest.main()
