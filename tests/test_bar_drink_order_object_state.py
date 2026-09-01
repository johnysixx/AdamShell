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


class BarDrinkOrderObjectStateTests(
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

    def test_order_is_object_only(
        self
    ):
        order = BarDrinkOrder(
            guest="lilith",
            drink="vodka_with_lemon",
            base="vodka",
            garnish="lemon",
            waiting_for="lemon",
        )

        self.assertEqual(
            order.drink,
            "vodka_with_lemon"
        )
        self.assertFalse(
            order.served
        )
        self._assert_object_only(
            order,
            "drink"
        )

    def test_order_transitions_keep_drink_identity(
        self
    ):
        order = BarDrinkOrder(
            guest="lilith",
            drink="vodka_with_lemon",
            base="vodka",
            garnish="lemon",
        )
        attempt = BarDrink(
            name="vodka_with_lemon",
            type="basic_bar_drink",
        )
        final = BarDrink(
            name="lilith",
            type="learned_bar_drink",
        )

        self.assertIs(
            order.record_attempt(attempt),
            attempt
        )
        self.assertIs(
            order.bartender_attempt,
            attempt
        )
        self.assertFalse(
            order.served
        )

        self.assertIs(
            order.complete(final),
            final
        )
        self.assertIs(
            order.final_drink,
            final
        )
        self.assertTrue(
            order.served
        )

    def test_snapshot_is_detached_boundary_dict(
        self
    ):
        order = BarDrinkOrder(
            guest="lilith",
            drink="vodka_with_lemon",
            base="vodka",
            garnish="lemon",
        )
        final = order.complete(
            BarDrink(
                name="lilith",
                type="learned_bar_drink",
                effects={
                    "energy_j": 1.0,
                },
            )
        )

        snapshot = order.to_dict()
        snapshot["served"] = False
        snapshot["final_drink"][
            "effects"
        ]["energy_j"] = 9.0

        self.assertTrue(
            order.served
        )
        self.assertEqual(
            final.effects["energy_j"],
            1.0
        )
        self.assertIsInstance(
            snapshot,
            dict
        )

    def test_scene_keeps_order_object_and_returns_snapshot(
        self
    ):
        scene = self._scene()
        scene.advance_to_lilith_entry()

        result = (
            scene
            .lilith_orders_vodka_with_lemon()
        )
        order = scene.lilith_order

        self.assertIsInstance(
            order,
            BarDrinkOrder
        )
        self.assertIsInstance(
            result["order"],
            dict
        )
        result["order"]["served"] = True

        self.assertFalse(
            order.served
        )
        self._assert_object_only(
            order,
            "served"
        )

    def test_scene_mutates_same_order_through_service(
        self
    ):
        scene = self._scene()
        scene.advance_to_good_drink_discussion()
        order = scene.lilith_order

        self.assertIsInstance(
            order,
            BarDrinkOrder
        )
        self.assertIsInstance(
            order.bartender_attempt,
            BarDrink
        )
        self.assertIsInstance(
            order.final_drink,
            BarDrink
        )
        self.assertTrue(
            order.served
        )
        self.assertIsNotNone(
            order.receipt_number
        )
        self._assert_object_only(
            order,
            "final_drink"
        )


if __name__ == "__main__":
    unittest.main()
