import unittest

from meeting_place.service_rules import BarServiceRules


class BasicDrinkPaymentTests(unittest.TestCase):

    def setUp(self):
        self.rules = BarServiceRules()

    def test_god_pays_no_existence_for_basic_drink(
        self
    ):
        god = {
            "name": "god",
            "type": "god",
            "existence_pct": 100.0,
            "energy_j": 10.0
        }

        result = (
            self.rules
            .apply_basic_drink_payment(
                god
            )
        )

        self.assertEqual(
            god["existence_pct"],
            100.0
        )

        self.assertEqual(
            result["payment_kind"],
            "god_rule"
        )

    def test_idea_entity_pays_small_energy_cost_for_basic_drink(
        self
    ):
        entity = {
            "name": "serpent",
            "type": "idea_entity",
            "energy_j": 10.0
        }

        result = (
            self.rules
            .apply_basic_drink_payment(
                entity
            )
        )

        self.assertLess(
            entity["energy_j"],
            10.0
        )

        self.assertGreater(
            result["energy_paid_j"],
            0.0
        )

    def test_root_entity_pays_twenty_five_percent_existence(
        self
    ):
        entity = {
            "name": "root_guest",
            "type": "root_entity",
            "existence_by_world": {
                "root_universe": 100.0
            }
        }

        result = (
            self.rules
            .apply_basic_drink_payment(
                entity
            )
        )

        self.assertEqual(
            entity[
                "existence_by_world"
            ][
                "root_universe"
            ],
            75.0
        )

        self.assertEqual(
            result[
                "existence_paid_pct"
            ],
            25.0
        )

    def test_physical_entity_pays_ninety_percent_and_gains_idea_existence(
        self
    ):
        entity = {
            "name": "physical_guest",
            "type": "physical_entity",
            "existence_by_world": {
                "physical_universe": 100.0,
                "idea_universe": 0.0
            }
        }

        result = (
            self.rules
            .apply_basic_drink_payment(
                entity
            )
        )

        self.assertEqual(
            entity[
                "existence_by_world"
            ][
                "physical_universe"
            ],
            10.0
        )

        self.assertEqual(
            entity[
                "existence_by_world"
            ][
                "idea_universe"
            ],
            40.0
        )

        self.assertEqual(
            result[
                "existence_paid_pct"
            ],
            90.0
        )

        self.assertEqual(
            result[
                "idea_existence_gain_pct"
            ],
            40.0
        )

        self.assertEqual(
            result[
                "existence_converted_to_energy_pct"
            ],
            50.0
        )

        self.assertGreater(
            result[
                "generated_energy_j"
            ],
            0.0
        )

        self.assertGreater(
            result[
                "bar_energy_j"
            ],
            0.0
        )

        self.assertLess(
            result[
                "bar_energy_j"
            ],
            result[
                "generated_energy_j"
            ]
        )




    def test_physical_entity_basic_drink_payment_adds_only_bar_share_to_reservoir(
        self
    ):
        from universe.universe import Universe
        from multiverse import UniverseRegistry
        from meeting_place.meeting_place import MeetingPlace

        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.refresh_basic_drinks()

        entity = {
            "name": "physical_guest",
            "type": "physical_entity",
            "existence_by_world": {
                "physical_universe": 100.0,
                "idea_universe": 0.0
            }
        }

        before = (
            meeting_place
            .energy_reservoir
            .energy_j
        )

        result = (
            meeting_place
            .serve_basic_drink(
                entity=entity,
                drink_name="rum"
            )
        )

        after = (
            meeting_place
            .energy_reservoir
            .energy_j
        )

        self.assertEqual(
            result["drink"]["name"],
            "rum"
        )

        self.assertGreater(
            result["payment"]["bar_energy_j"],
            0.0
        )

        self.assertEqual(
            after - before,
            result["payment"]["bar_energy_j"]
        )




    def test_god_receives_free_drink_note_from_cash_register(
        self
    ):
        from universe.universe import Universe
        from multiverse import UniverseRegistry
        from meeting_place.meeting_place import MeetingPlace

        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.refresh_basic_drinks()

        god = {
            "name": "god",
            "type": "god",
            "existence_pct": 100.0,
            "energy_j": 10.0
        }

        result = (
            meeting_place
            .serve_basic_drink(
                entity=god,
                drink_name="rum"
            )
        )

        receipt = result[
            "receipt"
        ]

        self.assertEqual(
            receipt[
                "receipt_kind"
            ],
            "god_free_drink_note"
        )

        self.assertEqual(
            receipt[
                "message"
            ],
            "BOHOV? ZDE PIJ? ZDARMA."
        )

        self.assertEqual(
            receipt["guest"],
            "god"
        )

        self.assertEqual(
            receipt["drink"],
            "rum"
        )

        self.assertEqual(
            receipt[
                "payment"
            ][
                "existence_paid_pct"
            ],
            0.0
        )

        self.assertIn(
            receipt,
            meeting_place
            .bar_counter
            .cash_register
            .receipts
        )


if __name__ == "__main__":
    unittest.main()
