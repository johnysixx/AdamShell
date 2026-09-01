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
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class BarServiceOrderObjectStateTests(
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

    def test_unserved_order_cannot_be_tasted(
        self
    ):
        order = BarDrinkOrder(
            guest="god",
            drink="wine",
            purpose="judge_wine_discussion",
        )

        with self.assertRaises(
            RuntimeError
        ):
            order.mark_tasted()

        self.assertFalse(
            order.served
        )
        self.assertFalse(
            order.tasted
        )
        self._assert_object_only(
            order,
            "served"
        )

    def test_wine_order_keeps_served_drink_identity(
        self
    ):
        scene = self._scene()
        result = scene.advance_to_god_receives_wine()
        order = scene.god.bar_state[
            "wine_order"
        ]

        self.assertIsInstance(
            order,
            BarDrinkOrder
        )
        self.assertIs(
            order.final_drink,
            result["service"]["drink"]
        )
        self.assertTrue(
            order.served
        )
        self.assertFalse(
            order.tasted
        )
        self.assertEqual(
            order.receipt_number,
            result["service"]["receipt"][
                "receipt_number"
            ]
        )
        self._assert_object_only(
            order,
            "drink"
        )

    def test_wine_order_is_mutated_when_tasted(
        self
    ):
        scene = self._scene()
        scene.advance_to_god_receives_wine()
        order = scene.god.bar_state[
            "wine_order"
        ]

        scene.god_tastes_existing_wine_and_rejects_it()

        self.assertIs(
            scene.god.bar_state[
                "wine_order"
            ],
            order
        )
        self.assertTrue(
            order.tasted
        )

    def test_water_order_keeps_served_drink_identity(
        self
    ):
        scene = self._scene()
        result = (
            scene
            .advance_to_everyone_at_bar_with_serpents_water()
        )
        order = scene.serpent.bar_state[
            "water_order"
        ]

        self.assertIsInstance(
            order,
            BarDrinkOrder
        )
        self.assertIsInstance(
            order.final_drink,
            BarDrink
        )
        self.assertIs(
            order.final_drink,
            result["water"]["drink"]
        )
        self.assertTrue(
            order.served
        )
        self.assertFalse(
            order.tasted
        )
        self._assert_object_only(
            order,
            "final_drink"
        )

    def test_order_events_remain_boundary_dicts(
        self
    ):
        scene = self._scene()
        result = scene.advance_to_god_receives_wine()
        order = scene.god.bar_state[
            "wine_order"
        ]
        event = result["order"]

        self.assertIsInstance(
            event,
            dict
        )
        event["drink"] = "changed"

        self.assertEqual(
            order.drink,
            "wine"
        )
        self.assertEqual(
            order.purpose,
            "judge_wine_discussion"
        )

    def test_lilith_order_snapshot_contract_is_unchanged(
        self
    ):
        scene = self._scene()
        scene.advance_to_lilith_entry()

        result = (
            scene
            .lilith_orders_vodka_with_lemon()
        )

        self.assertEqual(
            result["order"],
            {
                "guest": "lilith",
                "drink": "vodka_with_lemon",
                "base": "vodka",
                "garnish": "lemon",
                "served": False,
                "waiting_for": "lemon",
            }
        )


if __name__ == "__main__":
    unittest.main()
