import unittest
from types import SimpleNamespace

from meeting_place.bar_hex_geometry import BarHexGeometry
from meeting_place.glass_shelf import GlassShelf
from meeting_place.bottle_shelf import BottleShelf
from meeting_place.cash_register import CashRegister
from meeting_place.bar_receipt_state import BarReceiptState
from meeting_place.fridge import BarFridge
from meeting_place.bar_objects import (
    BarDrink,
    BarGlass,
    BarHexCell,
    BarInventoryItem,
    BarTab,
    BarTabItem,
    DarkEnergyBottle,
)


class BarObjectStateSecondCutTests(unittest.TestCase):

    def _assert_object_only(self, value):
        self.assertFalse(hasattr(value, "get"))
        self.assertFalse(hasattr(value, "keys"))
        with self.assertRaises(TypeError):
            _ = value["name"]

    def test_hex_cells_are_domain_objects(self):
        cell = BarHexGeometry().find_cell(name="center_table")
        self.assertIsInstance(cell, BarHexCell)
        self.assertEqual(cell.name, "center_table")
        self._assert_object_only(cell)

    def test_glasses_are_domain_objects(self):
        glass = GlassShelf().appear_shared_glass("beer_mug")
        self.assertIsInstance(glass, BarGlass)
        self.assertEqual(glass.capacity_litres, 0.5)
        self._assert_object_only(glass)

    def test_fridge_items_are_domain_objects(self):
        fridge = BarFridge()
        milk = fridge.get_item("milk")
        self.assertIsInstance(milk, BarInventoryItem)
        self.assertEqual(milk.name, "milk")
        self._assert_object_only(milk)
        self.assertIsInstance(fridge.public_state["items"]["milk"], dict)

    def test_dark_energy_bottle_is_domain_object(self):
        bottle = BottleShelf().add_dark_energy(2.5)
        self.assertIsInstance(bottle, DarkEnergyBottle)
        self.assertEqual(bottle.dark_energy_j, 2.5)
        self._assert_object_only(bottle)

    def test_open_tab_and_items_are_domain_objects(self):
        register = CashRegister()
        guest = SimpleNamespace(name="guest", type="human")
        tab = register.add_to_tab(
            guest,
            BarDrink(
                name="beer", type="basic_bar_drink", category="basic_drink"
            ),
        )
        self.assertIsInstance(tab, BarTab)
        self.assertIsInstance(tab.items[0], BarTabItem)
        self.assertEqual(tab.items[0].drink, "beer")
        self._assert_object_only(tab.items[0])
        self.assertFalse(hasattr(tab, "get"))
        self.assertFalse(hasattr(tab, "keys"))
        with self.assertRaises(TypeError):
            _ = tab["guest"]

    def test_receipt_is_domain_object_with_snapshot_boundary(self):
        register = CashRegister()
        guest = SimpleNamespace(name="guest", type="human")
        register.add_to_tab(
            guest,
            BarDrink(
                name="beer", type="basic_bar_drink", category="basic_drink"
            ),
        )
        receipt = register.print_open_tab_receipt(guest)
        self.assertIsInstance(
            receipt,
            BarReceiptState,
        )
        self.assertIsInstance(
            receipt.items[0],
            BarTabItem,
        )
        self._assert_object_only(
            receipt
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
