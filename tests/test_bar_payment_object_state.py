import unittest
from types import SimpleNamespace

from meeting_place.bar_objects import BarDrink
from meeting_place.bar_payment_state import BarPaymentState
from meeting_place.bar_receipt_state import BarReceiptState
from meeting_place.cash_register import CashRegister
from meeting_place.meeting_place import MeetingPlace
from meeting_place.service_rules import BarServiceRules
from multiverse import UniverseRegistry
from universe.universe import Universe


class BarPaymentObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.rules = BarServiceRules()

    def test_payment_has_no_mapping_api(self):
        payment = self.rules.apply_basic_drink_payment(
            SimpleNamespace(name="god", type="god")
        )

        for name in (
            "get", "setdefault", "keys", "items", "values", "update",
            "__getitem__", "__setitem__", "__delitem__", "__iter__",
        ):
            self.assertFalse(hasattr(payment, name), name)

        with self.assertRaises(TypeError):
            _ = payment["payment_kind"]

        self.assertEqual(payment.to_dict(), {
            "name": "god_basic_drink_payment",
            "entity": "god",
            "payment_kind": "god_rule",
            "existence_paid_pct": 0.0,
            "energy_paid_j": 0.0,
        })

    def test_root_payment_is_limited_to_remaining_existence(self):
        guest = SimpleNamespace(
            name="root_guest", type="root_entity",
            existence_by_world={"root_universe": 10.0},
        )

        payment = self.rules.apply_basic_drink_payment(guest)

        self.assertIsInstance(payment, BarPaymentState)
        self.assertEqual(payment.existence_paid_pct, 10.0)
        self.assertEqual(guest.existence_by_world["root_universe"], 0.0)
        self.assertEqual(payment.to_dict(), {
            "name": "root_entity_basic_drink_payment",
            "entity": "root_guest",
            "payment_kind": "root_existence",
            "existence_paid_pct": 10.0,
            "energy_paid_j": 0.0,
        })

    def test_small_physical_payment_generates_no_energy(self):
        guest = SimpleNamespace(
            name="physical_guest", type="physical_entity",
            existence_by_world={
                "physical_universe": 20.0,
                "idea_universe": 0.0,
            },
        )

        payment = self.rules.apply_basic_drink_payment(guest)

        self.assertIsInstance(payment, BarPaymentState)
        self.assertEqual(guest.existence_by_world["physical_universe"], 0.0)
        self.assertEqual(guest.existence_by_world["idea_universe"], 20.0)
        self.assertEqual(payment.to_dict(), {
            "name": "physical_entity_basic_drink_payment",
            "entity": "physical_guest",
            "payment_kind": "reality_exchange",
            "existence_paid_pct": 20.0,
            "idea_existence_gain_pct": 20.0,
            "existence_converted_to_energy_pct": 0.0,
            "generated_energy_j": 0.0,
            "bar_energy_j": 0.0,
        })

    def test_unsupported_payment_is_an_object_without_entity_changes(self):
        guest = SimpleNamespace(name="guest", type="human", energy_j=12.0)

        payment = self.rules.apply_basic_drink_payment(guest)

        self.assertIsInstance(payment, BarPaymentState)
        self.assertEqual(payment.payment_kind, "unsupported")
        self.assertEqual(guest.energy_j, 12.0)
        self.assertEqual(payment.to_dict(), {
            "name": "basic_drink_payment_not_available",
            "entity": "guest",
            "entity_type": "human",
            "payment_kind": "unsupported",
        })

    def test_unsupported_guest_does_not_credit_bar_or_receive_receipt(self):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()
        bar = MeetingPlace(universe)
        guest = SimpleNamespace(name="guest", type="human")
        energy_before = bar.energy_reservoir.energy_j

        with self.assertRaisesRegex(ValueError, "cannot pay"):
            bar.serve_basic_drink(guest, "rum")

        self.assertEqual(bar.energy_reservoir.energy_j, energy_before)
        self.assertEqual(bar.bar_counter.cash_register.receipt_count, 0)
        self.assertEqual(bar.bar_counter.cash_register.receipt_records(), ())

    def test_cash_register_rejects_mapping_payment_without_advancing_number(self):
        register = CashRegister()
        guest = SimpleNamespace(name="god", type="god")
        drink = BarDrink(
            name="rum", type="basic_bar_drink", category="basic_drink"
        )

        with self.assertRaisesRegex(TypeError, "BarPaymentState"):
            register.print_receipt(
                guest, drink, {"payment_kind": "god_rule"}
            )

        self.assertEqual(register.receipt_count, 0)
        self.assertEqual(register.receipt_records(), ())
        payment = self.rules.apply_basic_drink_payment(guest)
        receipt = register.print_receipt(guest, drink, payment)
        self.assertEqual(receipt.receipt_number, 1)

    def test_receipt_rejects_mapping_payment(self):
        with self.assertRaisesRegex(TypeError, "BarPaymentState"):
            BarReceiptState(
                receipt_number=1,
                type="bar_receipt",
                guest="guest",
                guest_type="human",
                payment={"payment_kind": "energy", "energy_paid_j": 1.0},
            )


if __name__ == "__main__":
    unittest.main()
