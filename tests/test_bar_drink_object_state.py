import unittest
from types import SimpleNamespace

from meeting_place.bar_objects import (
    BarDrink,
    BarDrinkGarnish,
    BarDrinkPreparation,
    BarTabItem,
)
from meeting_place.bar_receipt_state import BarReceiptState
from meeting_place.bar_basic_drinks_on_tab_state import (
    BarBasicDrinksOnTabResult,
    BarOrderServedOnOpenTabEvent,
)
from meeting_place.meeting_place import MeetingPlace
from multiverse import UniverseRegistry
from universe.universe import Universe


class BarDrinkObjectStateTests(unittest.TestCase):

    def _meeting_place(self):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()
        return MeetingPlace(universe)

    def test_served_drinks_are_domain_objects(self):
        bar = self._meeting_place()
        guest = SimpleNamespace(
            name="guest",
            type="human",
        )

        result = bar.serve_basic_drinks_on_tab(
            entity=guest,
            drink_names=["wine", "beer"],
        )

        self.assertIsInstance(
            result,
            BarBasicDrinksOnTabResult,
        )
        self.assertFalse(hasattr(result, "__getitem__"))
        self.assertIsNone(result.payment)
        self.assertEqual(result.tab_status, "open")

        with self.assertRaises(TypeError):
            _ = result["drinks"]

        self.assertTrue(
            all(
                isinstance(drink, BarDrink)
                for drink in result.drinks
            )
        )

        self.assertEqual(
            [drink.name for drink in result.drinks],
            ["wine", "beer"],
        )

    def test_open_tab_event_is_immutable_object(self):
        bar = self._meeting_place()
        guest = SimpleNamespace(name="guest", type="human")

        result = bar.serve_basic_drinks_on_tab(
            entity=guest,
            drink_names=["wine", "beer"],
        )
        event = bar.events[-1]

        self.assertIsInstance(
            event, BarOrderServedOnOpenTabEvent
        )
        self.assertEqual(
            event.name, "bar_order_served_on_open_tab"
        )
        self.assertEqual(event.guest, "guest")
        self.assertEqual(event.drinks, ("wine", "beer"))
        self.assertEqual(
            event.receipt_number,
            result.receipt.receipt_number,
        )
        self.assertFalse(event.paid)
        self.assertIs(bar.bartender.event_memory[-1], event)
        self.assertIs(
            bar.back_room_black_box.entries[-1].data,
            event,
        )
        self.assertEqual(
            bar.back_room_black_box.entries[-1].event,
            event.name,
        )

        snapshot = event.to_dict()
        snapshot["drinks"].append("rum")
        self.assertEqual(event.drinks, ("wine", "beer"))

        with self.assertRaises(TypeError):
            _ = event["name"]

    def test_meeting_place_rejects_mapping_event_atomically(self):
        bar = self._meeting_place()

        before = (
            len(bar.events),
            len(bar.bartender.event_memory),
            len(bar.back_room_black_box.entries),
        )

        with self.assertRaises(TypeError):
            bar.emit_event({
                "name": "bar_order_served_on_open_tab",
            })

        self.assertEqual(
            (
                len(bar.events),
                len(bar.bartender.event_memory),
                len(bar.back_room_black_box.entries),
            ),
            before,
        )

    def test_drink_objects_have_no_mapping_api(self):
        drink = BarDrink(
            name="rum",
            type="basic_bar_drink",
            category="basic_drink",
        )

        for name in (
            "get",
            "keys",
            "items",
            "values",
            "__getitem__",
        ):
            self.assertFalse(
                hasattr(drink, name),
                name,
            )

        with self.assertRaises(TypeError):
            _ = drink["name"]

    def test_receipt_is_object_with_explicit_boundary_snapshot(self):
        bar = self._meeting_place()
        guest = SimpleNamespace(
            name="guest",
            type="human",
        )

        result = bar.serve_basic_drinks_on_tab(
            entity=guest,
            drink_names=["wine"],
        )

        receipt = result.receipt

        self.assertIsInstance(
            receipt,
            BarReceiptState,
        )
        self.assertIsInstance(
            receipt.items[0],
            BarTabItem,
        )

        snapshot = receipt.to_dict()

        self.assertIsInstance(
            snapshot,
            dict,
        )
        self.assertIsInstance(
            snapshot["items"][0],
            dict,
        )

    def test_public_snapshot_is_detached_from_drink(self):
        drink = BarDrink(
            name="lilith",
            type="learned_bar_drink",
            effects={"energy_j": 1.0},
            garnish=BarDrinkGarnish(ingredient="lemon"),
            preparation=BarDrinkPreparation(
                vodka=1,
                lemon="drop",
            ),
        )

        snapshot = drink.to_dict()
        snapshot["effects"]["energy_j"] = 9.0
        snapshot["garnish"]["ingredient"] = "lime"
        snapshot["preparation"]["lemon"] = "whole"

        self.assertEqual(
            drink.effects["energy_j"],
            1.0,
        )
        self.assertEqual(
            drink.garnish.ingredient,
            "lemon",
        )
        self.assertEqual(
            drink.preparation.lemon,
            "drop",
        )


    def test_garnish_requires_domain_object(self):
        with self.assertRaises(TypeError):
            BarDrink(
                name="water_with_lemon_slice",
                type="basic_bar_drink",
                garnish={
                    "ingredient": "lemon",
                },
            )

    def test_preparation_requires_domain_object(self):
        with self.assertRaises(TypeError):
            BarDrink(
                name="vodka_with_lemon",
                type="basic_bar_drink",
                preparation={
                    "vodka": 1,
                    "lemon": "drop",
                },
            )

    def test_preparation_is_domain_object(self):
        preparation = BarDrinkPreparation(
            vodka=1,
            lemon="drop",
        )
        drink = BarDrink(
            name="vodka_with_lemon",
            type="basic_bar_drink",
            preparation=preparation,
        )

        self.assertIs(
            drink.preparation,
            preparation,
        )
        self.assertEqual(
            drink.preparation.vodka,
            1,
        )
        self.assertEqual(
            drink.preparation.lemon,
            "drop",
        )

        for name in (
            "get",
            "keys",
            "items",
            "values",
            "__getitem__",
        ):
            self.assertFalse(
                hasattr(preparation, name),
                name,
            )

        with self.assertRaises(TypeError):
            _ = preparation["lemon"]


    def test_garnish_is_domain_object(self):
        garnish = BarDrinkGarnish(
            ingredient="lemon",
            amount="slice",
            price=0,
        )
        drink = BarDrink(
            name="water_with_lemon_slice",
            type="basic_bar_drink",
            garnish=garnish,
        )

        self.assertIs(
            drink.garnish,
            garnish,
        )
        self.assertEqual(
            drink.garnish.ingredient,
            "lemon",
        )
        self.assertEqual(
            drink.garnish.amount,
            "slice",
        )
        self.assertEqual(
            drink.garnish.price,
            0,
        )


if __name__ == "__main__":
    unittest.main()
