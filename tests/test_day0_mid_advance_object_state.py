import unittest

from genesis.day0_advance_state import (
    AcidityWineIdeaAdvanceResult,
    BalancedAcidityAdvanceResult,
    BeerBitternessAdvanceResult,
    GodAtTableAdvanceResult,
    GodReceivesWineAdvanceResult,
    GodUnderstandsSweetnessAdvanceResult,
    ThreeWayDrinkWagerAdvanceResult,
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


class Day0MidAdvanceObjectStateTests(
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

    def test_god_at_table_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_god_at_table()
        )

        self.assertIsInstance(
            result,
            GodAtTableAdvanceResult,
        )

        self.assertEqual(
            result.joined.companions,
            (
                "serpent",
                "lilith",
            ),
        )

        self._assert_object_only(
            result,
            "joined",
        )

    def test_acidity_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_acidity_wine_idea()
        )

        self.assertIsInstance(
            result,
            AcidityWineIdeaAdvanceResult,
        )

        self.assertTrue(
            result
            .revised
            .idea
            .desired_property
            .acidity
        )

        self.assertEqual(
            result.tasted.taster,
            "serpent",
        )

        self._assert_object_only(
            result,
            "revised",
        )

    def test_god_wine_service_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_god_receives_wine()
        )

        self.assertIsInstance(
            result,
            GodReceivesWineAdvanceResult,
        )

        self.assertEqual(
            result.order.drink,
            "wine",
        )

        self.assertIs(
            scene.god
            .bar_state
            .wine_order
            .final_drink,
            result.service.drink,
        )

        self._assert_object_only(
            result,
            "service",
        )

    def test_balance_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_balanced_acidity_idea()
        )

        self.assertIsInstance(
            result,
            BalancedAcidityAdvanceResult,
        )

        self.assertEqual(
            result
            .balance
            .idea
            .qualification
            .acidity,
            "moderate",
        )

        self._assert_object_only(
            result,
            "balance",
        )

    def test_sweetness_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_god_understands_sweetness()
        )

        self.assertIsInstance(
            result,
            GodUnderstandsSweetnessAdvanceResult,
        )

        self.assertTrue(
            result.mead.understands.sweetness
        )

        self.assertEqual(
            result.explanation.principle,
            "sweetness",
        )

        self._assert_object_only(
            result,
            "mead",
        )

    def test_three_way_wager_wrapper_is_object(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_three_way_drink_wager()
        )

        self.assertIsInstance(
            result,
            ThreeWayDrinkWagerAdvanceResult,
        )

        self.assertTrue(
            result.offered.accepted
        )

        self.assertEqual(
            result.accepted.participant,
            "god",
        )

        self._assert_object_only(
            result,
            "offered",
        )

    def test_bitterness_wrapper_closes_object_chain(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_bitterness_split_between_wine_and_beer()
        )

        self.assertIsInstance(
            result,
            BeerBitternessAdvanceResult,
        )

        self.assertIsInstance(
            result.previous,
            ThreeWayDrinkWagerAdvanceResult,
        )

        self.assertIsInstance(
            result.previous.previous,
            GodUnderstandsSweetnessAdvanceResult,
        )

        self.assertIsInstance(
            result.previous.previous.previous,
            BalancedAcidityAdvanceResult,
        )

        self.assertIsInstance(
            result
            .previous
            .previous
            .previous
            .previous,
            GodReceivesWineAdvanceResult,
        )

        self.assertTrue(
            result
            .god_beer
            .understands
            .bitterness
        )

        self.assertTrue(
            result
            .lilith
            .beer_conclusion
            .bitterness_allowed
        )

        self._assert_object_only(
            result,
            "god_beer",
        )


if __name__ == "__main__":
    unittest.main()
