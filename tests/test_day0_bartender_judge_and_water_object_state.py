import unittest

from genesis.day0_bartender_judge_and_water_state import (
    BartenderServesSerpentWaterEvent,
    GodRejectsParticipantVoteEvent,
    LilithGodMoveToBarEvent,
    SerpentOrdersWaterEvent,
    SerpentWaterServiceResult,
    WagerDecisionMethodSnapshot,
)
from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    BarDrink,
    BarDrinkOrder,
    BarWagerDecisionMethod,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0BartenderJudgeAndWaterObjectStateTests(
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

    def test_water_order_event_is_object_only(
        self
    ):
        scene = self._scene()

        scene.advance_to_wager_vote_proposal()

        event = (
            scene.serpent_orders_water_at_bar()
        )

        order = (
            scene.serpent
            .bar_state
            .water_order
        )

        self.assertIsInstance(
            event,
            SerpentOrdersWaterEvent,
        )

        self.assertIsInstance(
            order,
            BarDrinkOrder,
        )

        self.assertEqual(
            event.drink,
            "water",
        )

        self.assertEqual(
            order.drink,
            "water",
        )

        self._assert_object_only(
            event,
            "drink",
        )

        self._assert_object_only(
            order,
            "drink",
        )

    def test_judge_rejection_uses_detached_snapshots(
        self
    ):
        scene = self._scene()

        scene.advance_to_wager_vote_proposal()

        scene.serpent_orders_water_at_bar()

        event = (
            scene
            .god_rejects_participant_vote_and_proposes_bartender()
        )

        wager = (
            scene.serpent_lilith_drink_wager
        )

        self.assertIsInstance(
            event,
            GodRejectsParticipantVoteEvent,
        )

        self.assertIsInstance(
            event.rejects,
            WagerDecisionMethodSnapshot,
        )

        self.assertIsInstance(
            event.proposes,
            WagerDecisionMethodSnapshot,
        )

        self.assertEqual(
            event.rejects.type,
            "participant_vote",
        )

        self.assertEqual(
            event.proposes.type,
            "bartender_judges",
        )

        self.assertEqual(
            event.proposes.judge,
            "bartender",
        )

        self.assertIsInstance(
            wager.bartender_judge_proposal,
            BarWagerDecisionMethod,
        )

        self.assertIsNot(
            event.proposes,
            wager.bartender_judge_proposal,
        )

        self._assert_object_only(
            event,
            "proposes",
        )

        self._assert_object_only(
            event.proposes,
            "type",
        )

    def test_move_to_bar_is_object_state(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_everyone_at_bar_with_serpents_water()
        )

        event = result[
            "move"
        ]

        self.assertIsInstance(
            event,
            LilithGodMoveToBarEvent,
        )

        self.assertEqual(
            event.guests,
            (
                "lilith",
                "god",
            ),
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
            scene.lilith
            .bar_state
            .location,
            "bar_counter",
        )

        self.assertEqual(
            scene.god
            .bar_state
            .location,
            "bar_counter",
        )

        self._assert_object_only(
            event,
            "guests",
        )

    def test_water_service_is_object_result(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_everyone_at_bar_with_serpents_water()
        )

        service = result[
            "water"
        ]

        order = (
            scene.serpent
            .bar_state
            .water_order
        )

        self.assertIsInstance(
            service,
            SerpentWaterServiceResult,
        )

        self.assertIsInstance(
            service.drink,
            BarDrink,
        )

        self.assertIsInstance(
            service.event,
            BartenderServesSerpentWaterEvent,
        )

        self.assertIs(
            order.final_drink,
            service.drink,
        )

        self.assertEqual(
            service.drink.name,
            "water_with_lemon_slice",
        )

        self.assertEqual(
            service.drink.garnish.ingredient,
            "lemon",
        )

        self.assertEqual(
            service.drink.garnish.price,
            0,
        )

        self.assertFalse(
            service.event.whole_lemon_consumed
        )

        self._assert_object_only(
            service,
            "drink",
        )

        self._assert_object_only(
            service.event,
            "lemon_slice",
        )

    def test_history_remains_serialized_boundary(
        self
    ):
        scene = self._scene()

        scene.advance_to_everyone_at_bar_with_serpents_water()

        judge = next(
            event
            for event in scene.history
            if event["name"]
            == (
                "god_rejects_participant_vote_"
                "and_proposes_bartender"
            )
        )

        water = next(
            event
            for event in scene.history
            if event["name"]
            == (
                "bartender_serves_serpent_water_"
                "with_free_lemon_slice"
            )
        )

        move = next(
            event
            for event in scene.history
            if event["name"]
            == "lilith_and_god_move_to_bar"
        )

        self.assertIsInstance(
            judge["rejects"],
            dict,
        )

        self.assertIsInstance(
            judge["proposes"],
            dict,
        )

        self.assertEqual(
            judge["proposes"]["judge"],
            "bartender",
        )

        self.assertTrue(
            water["lemon_slice"]
        )

        self.assertEqual(
            move["guests"],
            [
                "lilith",
                "god",
            ],
        )


if __name__ == "__main__":
    unittest.main()
