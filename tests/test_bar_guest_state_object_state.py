import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    BarDrink,
    BarDrinkOrder,
    BarGuestBet,
    BarGuestState,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class BarGuestStateObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value,
        key
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[key]

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

    def test_guest_state_and_bet_are_object_only(
        self
    ):
        bet = BarGuestBet(
            offered=True,
            accepted=False,
        )
        state = BarGuestState(
            seat="at_bar",
            activity="tasting_ordered_drinks",
            bet=bet,
        )

        self.assertEqual(
            state.seat,
            "at_bar"
        )
        self.assertIs(
            state.bet,
            bet
        )
        self.assertTrue(
            bet.offered
        )
        self._assert_object_only(
            state,
            "activity"
        )
        self._assert_object_only(
            bet,
            "offered"
        )

    def test_snapshot_detaches_nested_state(
        self
    ):
        drink = BarDrink(
            name="water_with_lemon_slice",
            type="basic_bar_drink",
            garnish={
                "ingredient": "lemon",
            },
        )
        order = BarDrinkOrder(
            guest="serpent",
            drink="water",
        )
        order.complete(
            drink
        )
        state = BarGuestState(
            drinks=[
                "wine",
                "beer",
            ],
            table_with=[
                "lilith",
                "god",
            ],
            bet=BarGuestBet(
                offered=True,
            ),
            drink=drink,
            water_order=order,
        )

        snapshot = state.to_dict()
        snapshot["drinks"].append(
            "mead"
        )
        snapshot["table_with"].append(
            "bartender"
        )
        snapshot["bet"]["accepted"] = True
        snapshot["drink"]["garnish"][
            "ingredient"
        ] = "lime"
        snapshot["water_order"][
            "served"
        ] = False

        self.assertEqual(
            state.drinks,
            [
                "wine",
                "beer",
            ]
        )
        self.assertEqual(
            state.table_with,
            [
                "lilith",
                "god",
            ]
        )
        self.assertFalse(
            state.bet.accepted
        )
        self.assertEqual(
            drink.garnish["ingredient"],
            "lemon"
        )
        self.assertTrue(
            order.served
        )

    def test_checkpoint_remains_detached_boundary_dict(
        self
    ):
        scene = self._scene()
        checkpoint = scene.advance_to_lilith_entry()
        state = scene.serpent.bar_state
        snapshot = checkpoint[
            "serpent"
        ]["bar_state"]

        self.assertIsInstance(
            state,
            BarGuestState
        )
        self.assertIsInstance(
            snapshot,
            dict
        )
        snapshot["activity"] = "changed"
        snapshot["bet"]["accepted"] = True

        self.assertEqual(
            state.activity,
            "tasting_ordered_drinks"
        )
        self.assertFalse(
            state.bet.accepted
        )
        self._assert_object_only(
            state,
            "activity"
        )

    def test_serpent_state_identity_survives_movement(
        self
    ):
        scene = self._scene()
        scene.advance_to_lilith_entry()
        state = scene.serpent.bar_state
        scene.lilith_orders_vodka_with_lemon()
        scene.serpent_and_lilith_begin_conversation()
        scene.play_serpent_lilith_first_conversation()
        scene.serpent_and_lilith_agree_on_table()

        scene.serpent_moves_from_bar_to_existing_table()

        self.assertIs(
            scene.serpent.bar_state,
            state
        )
        self.assertEqual(
            state.location,
            "table"
        )
        self.assertEqual(
            state.activity,
            "waiting_for_lilith"
        )

    def test_all_late_scene_guest_states_are_objects(
        self
    ):
        scene = self._scene()
        result = (
            scene
            .advance_to_everyone_at_bar_with_serpents_water()
        )

        for guest in (
            scene.serpent,
            scene.lilith,
            scene.god,
        ):
            self.assertIsInstance(
                guest.bar_state,
                BarGuestState
            )
            self._assert_object_only(
                guest.bar_state,
                "location"
            )

        self.assertIs(
            scene.serpent.bar_state.water_order.final_drink,
            result["water"]["drink"]
        )
        self.assertIsInstance(
            scene.god.bar_state.wine_order,
            BarDrinkOrder
        )


if __name__ == "__main__":
    unittest.main()
