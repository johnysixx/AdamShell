import unittest
from types import SimpleNamespace

from meeting_place.bar_objects import (
    BarTabItem,
)
from meeting_place.bar_receipt_state import (
    BarReceiptState,
)
from meeting_place.cash_register import (
    CashRegister,
)


class BarReceiptObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.register = CashRegister()
        self.guest = SimpleNamespace(
            name="receipt_guest",
            type="human",
        )

    def test_state_has_no_mapping_api(self):
        receipt = BarReceiptState(
            receipt_number=1,
            type="bar_receipt",
            guest="receipt_guest",
            guest_type="human",
        )

        for name in (
            "get",
            "setdefault",
            "__getitem__",
            "__setitem__",
            "keys",
            "values",
            "update",
        ):
            self.assertFalse(
                hasattr(
                    receipt,
                    name,
                )
            )

        self.assertFalse(
            callable(
                receipt.items
            )
        )

    def test_open_tab_receipt_and_items_are_objects(self):
        self.register.add_to_tab(
            self.guest,
            {
                "name": "beer",
                "category": "basic_drink",
            },
        )

        receipt = (
            self.register
            .print_open_tab_receipt(
                self.guest
            )
        )

        self.assertIsInstance(
            receipt,
            BarReceiptState,
        )

        self.assertIsInstance(
            receipt.items[0],
            BarTabItem,
        )

        self.assertIs(
            self.register.receipts[0],
            receipt,
        )

        self.assertEqual(
            receipt.status,
            "open_unpaid",
        )

    def test_staff_receipt_items_are_objects(self):
        drink = SimpleNamespace(
            name="wine",
            category="basic_drink",
        )

        receipt = (
            self.register
            .print_staff_purchase_receipt(
                self.guest,
                [drink],
            )
        )

        self.assertEqual(
            receipt.receipt_kind,
            "staff_purchase",
        )

        self.assertIsInstance(
            receipt.items[0],
            BarTabItem,
        )

    def test_payment_remains_dynamic_payload_at_boundary(self):
        drink = SimpleNamespace(
            name="rum",
            category="basic_drink",
        )

        payment = {
            "payment_kind": "energy",
            "energy_paid_j": 1.25,
        }

        receipt = (
            self.register
            .print_receipt(
                entity=self.guest,
                drink=drink,
                payment=payment,
            )
        )

        self.assertIsInstance(
            receipt.payment,
            dict,
        )

        self.assertEqual(
            receipt.payment[
                "energy_paid_j"
            ],
            1.25,
        )

        snapshot = (
            receipt.to_dict()
        )

        self.assertIsInstance(
            snapshot,
            dict,
        )

        self.assertIsInstance(
            snapshot["payment"],
            dict,
        )

    def test_legacy_mapping_receipt_is_rejected(self):
        self.register.receipts.append({
            "receipt_number": 1,
            "type": "bar_receipt",
        })

        with self.assertRaises(
            TypeError
        ):
            self.register.receipt_records()


if __name__ == "__main__":
    unittest.main()
