import unittest
from dataclasses import FrozenInstanceError
from types import SimpleNamespace

from meeting_place.bar_basic_drink_service_state import (
    BarBasicDrinkServiceResult,
)
from meeting_place.bar_objects import BarDrink
from meeting_place.bar_payment_state import BarPaymentState
from meeting_place.bar_receipt_state import BarReceiptState
from meeting_place.meeting_place import MeetingPlace
from multiverse import UniverseRegistry
from universe.universe import Universe


class BarBasicDrinkServiceObjectStateTests(
    unittest.TestCase
):

    def _service(self):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        bar = MeetingPlace(universe)

        god = SimpleNamespace(
            name="god",
            type="god",
            existence_pct=100.0,
            energy_j=10.0,
        )

        result = bar.serve_basic_drink(
            entity=god,
            drink_name="rum",
        )

        return bar, result

    def test_service_returns_typed_result(self):
        bar, result = self._service()

        self.assertIsInstance(
            result,
            BarBasicDrinkServiceResult,
        )
        self.assertIsInstance(result.drink, BarDrink)
        self.assertIsInstance(
            result.payment,
            BarPaymentState,
        )
        self.assertIsInstance(
            result.receipt,
            BarReceiptState,
        )

        self.assertEqual(result.drink.name, "rum")

        self.assertIs(
            result.receipt,
            bar.bar_counter.cash_register.receipts[-1],
        )

        self.assertIsNot(
            result.receipt.payment,
            result.payment,
        )

        with self.assertRaises(TypeError):
            _ = result["drink"]

        with self.assertRaises(FrozenInstanceError):
            result.drink = None

    def test_receipt_payment_remains_detached(self):
        _, result = self._service()

        original = result.receipt.payment.existence_paid_pct

        result.payment.existence_paid_pct = 99.0

        self.assertEqual(
            result.receipt.payment.existence_paid_pct,
            original,
        )

        self.assertEqual(
            result.payment.existence_paid_pct,
            99.0,
        )

    def test_rejects_mapping_components(self):
        _, result = self._service()

        cases = (
            {
                "drink": {},
                "payment": result.payment,
                "receipt": result.receipt,
            },
            {
                "drink": result.drink,
                "payment": {},
                "receipt": result.receipt,
            },
            {
                "drink": result.drink,
                "payment": result.payment,
                "receipt": {},
            },
        )

        for values in cases:
            with self.subTest(fields=tuple(values)):
                with self.assertRaises(TypeError):
                    BarBasicDrinkServiceResult(**values)


if __name__ == "__main__":
    unittest.main()
