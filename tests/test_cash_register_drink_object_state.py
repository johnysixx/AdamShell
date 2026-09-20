import unittest
from types import SimpleNamespace

from meeting_place.bar_objects import BarDrink
from meeting_place.bar_payment_state import BarPaymentState
from meeting_place.cash_register import CashRegister


class CashRegisterDrinkObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.register = CashRegister()
        self.guest = SimpleNamespace(name="guest", type="idea_entity")
        self.drink = BarDrink(
            name="rum", type="basic_bar_drink", category="basic_drink"
        )
        self.payment = BarPaymentState(
            name="idea_entity_basic_drink_payment",
            entity=self.guest.name,
            payment_kind="energy",
            energy_paid_j=1.25,
        )

    def test_mapping_drink_does_not_open_tab(self):
        with self.assertRaisesRegex(TypeError, "BarDrink"):
            self.register.add_to_tab(self.guest, self.drink.to_dict())

        self.assertEqual(self.register.open_tabs, {})
        tab = self.register.add_to_tab(self.guest, self.drink)
        self.assertEqual(len(tab.items), 1)
        self.assertEqual(tab.items[0].drink, "rum")
        self.assertEqual(tab.items[0].drink_category, "basic_drink")

    def test_mapping_drink_does_not_change_existing_tab(self):
        tab = self.register.add_to_tab(self.guest, self.drink)
        item = tab.items[0]

        with self.assertRaisesRegex(TypeError, "BarDrink"):
            self.register.add_to_tab(self.guest, self.drink.to_dict())

        self.assertIs(self.register.open_tab(self.guest), tab)
        self.assertEqual(tab.items, [item])
        self.assertIs(tab.items[0], item)

    def test_mapping_drink_does_not_consume_paid_receipt_number(self):
        first_receipt = self.register.print_receipt(
            self.guest, self.drink, self.payment
        )

        with self.assertRaisesRegex(TypeError, "BarDrink"):
            self.register.print_receipt(
                self.guest, self.drink.to_dict(), self.payment
            )

        self.assertEqual(self.register.receipt_count, 1)
        self.assertEqual(self.register.receipt_records(), (first_receipt,))
        next_receipt = self.register.print_receipt(
            self.guest, self.drink, self.payment
        )
        self.assertEqual(next_receipt.receipt_number, 2)
        self.assertEqual(next_receipt.drink, "rum")
        self.assertEqual(next_receipt.drink_category, "basic_drink")

    def test_mixed_staff_order_does_not_store_partial_receipt_or_consume_number(self):
        first_receipt = self.register.print_staff_purchase_receipt(
            self.guest, [self.drink]
        )

        with self.assertRaisesRegex(TypeError, "BarDrink"):
            self.register.print_staff_purchase_receipt(
                self.guest, iter([self.drink, self.drink.to_dict()])
            )

        self.assertEqual(self.register.receipt_count, 1)
        self.assertEqual(self.register.receipt_records(), (first_receipt,))
        next_receipt = self.register.print_staff_purchase_receipt(
            self.guest, iter([self.drink])
        )
        self.assertEqual(next_receipt.receipt_number, 2)
        self.assertEqual(len(next_receipt.items), 1)
        self.assertEqual(next_receipt.items[0].drink, "rum")
        self.assertEqual(next_receipt.items[0].drink_category, "basic_drink")

    def test_arbitrary_values_are_not_coerced_to_drinks(self):
        for value in (
            "rum",
            None,
            SimpleNamespace(name="rum", category="basic_drink"),
        ):
            with self.subTest(value=value):
                with self.assertRaisesRegex(TypeError, "BarDrink"):
                    self.register.add_to_tab(self.guest, value)

                self.assertEqual(self.register.open_tabs, {})


if __name__ == "__main__":
    unittest.main()
