import unittest
from dataclasses import FrozenInstanceError
from types import SimpleNamespace

from meeting_place.bar_service_effect_state import (
    BarEnergyDrinkUnavailableResult,
    BarEntropyDrinkUnavailableResult,
    BarGodEnergyDrinkEffect,
    BarGodEntropyDrinkEffect,
    BarIdeaEntityEnergyDrinkEffect,
    BarIdeaEntityEntropyDrinkEffect,
)
from meeting_place.service_rules import (
    BarServiceRules,
)


class BarServiceEffectObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.rules = (
            BarServiceRules()
        )

    def assert_object_only(
        self,
        result,
    ):
        for name in (
            "get",
            "keys",
            "items",
            "values",
            "update",
            "setdefault",
            "__getitem__",
            "__setitem__",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    name,
                ),
                name,
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "name"
            ]

        with self.assertRaises(
            FrozenInstanceError
        ):
            result.entity = (
                "changed"
            )

    def test_god_energy_drink_effect_is_object(
        self
    ):
        god = SimpleNamespace(
            name="god",
            type="god",
            creative_will=1.0,
            existence_pct=100.0,
        )

        result = (
            self.rules
            .apply_energy_drink(
                god
            )
        )

        self.assertIsInstance(
            result,
            BarGodEnergyDrinkEffect,
        )

        self.assertEqual(
            result.name,
            "god_energy_drink_effect",
        )

        self.assertEqual(
            result.entity,
            "god",
        )

        self.assertEqual(
            result.existence_cost_pct,
            0.0,
        )

        self.assertGreater(
            result.creative_will_gain,
            0.0,
        )

        self.assertGreater(
            god.creative_will,
            1.0,
        )

        self.assert_object_only(
            result
        )

    def test_idea_entity_energy_drink_effect_is_object(
        self
    ):
        entity = SimpleNamespace(
            name="serpent",
            type="idea_entity",
            existence_pct=100.0,
            will=1.0,
        )

        result = (
            self.rules
            .apply_energy_drink(
                entity
            )
        )

        self.assertIsInstance(
            result,
            BarIdeaEntityEnergyDrinkEffect,
        )

        self.assertEqual(
            result.name,
            "idea_entity_energy_drink_effect",
        )

        self.assertEqual(
            result.entity,
            "serpent",
        )

        self.assertGreater(
            result.existence_cost_pct,
            0.0,
        )

        self.assertGreater(
            result.will_gain,
            0.0,
        )

        self.assertLess(
            entity.existence_pct,
            100.0,
        )

        self.assertGreater(
            entity.will,
            1.0,
        )

        self.assert_object_only(
            result
        )

    def test_energy_drink_unavailable_is_object(
        self
    ):
        entity = SimpleNamespace(
            name="guest",
            type="human",
        )

        result = (
            self.rules
            .apply_energy_drink(
                entity
            )
        )

        self.assertIsInstance(
            result,
            BarEnergyDrinkUnavailableResult,
        )

        self.assertEqual(
            result.name,
            "energy_drink_not_available",
        )

        self.assertEqual(
            result.entity,
            "guest",
        )

        self.assertEqual(
            result.entity_type,
            "human",
        )

        self.assert_object_only(
            result
        )

    def test_god_entropy_drink_effect_is_object(
        self
    ):
        god = SimpleNamespace(
            name="god",
            type="god",
            energy_j=10.0,
            existence_pct=90.0,
            creative_will=1.0,
        )

        result = (
            self.rules
            .apply_entropy_drink(
                god,
                entity_energy_gain_j=2.5,
            )
        )

        self.assertIsInstance(
            result,
            BarGodEntropyDrinkEffect,
        )

        self.assertEqual(
            result.name,
            "god_entropy_drink_effect",
        )

        self.assertEqual(
            result.entity,
            "god",
        )

        self.assertEqual(
            result.entity_energy_gain_j,
            2.5,
        )

        self.assertEqual(
            result.payment_pct,
            0.0,
        )

        self.assertEqual(
            god.energy_j,
            12.5,
        )

        self.assertGreater(
            god.existence_pct,
            90.0,
        )

        self.assert_object_only(
            result
        )

    def test_idea_entity_entropy_drink_effect_is_object(
        self
    ):
        entity = SimpleNamespace(
            name="serpent",
            type="idea_entity",
            energy_j=5.0,
            existence_pct=80.0,
            will=2.0,
        )

        result = (
            self.rules
            .apply_entropy_drink(
                entity,
                entity_energy_gain_j=3.0,
            )
        )

        self.assertIsInstance(
            result,
            BarIdeaEntityEntropyDrinkEffect,
        )

        self.assertEqual(
            result.name,
            "idea_entity_entropy_drink_effect",
        )

        self.assertEqual(
            result.entity,
            "serpent",
        )

        self.assertEqual(
            result.entity_energy_gain_j,
            3.0,
        )

        self.assertEqual(
            result.payment_pct,
            0.0,
        )

        self.assertEqual(
            entity.energy_j,
            8.0,
        )

        self.assert_object_only(
            result
        )

    def test_entropy_drink_unavailable_is_object(
        self
    ):
        entity = SimpleNamespace(
            name="guest",
            type="human",
        )

        result = (
            self.rules
            .apply_entropy_drink(
                entity,
                entity_energy_gain_j=4.0,
            )
        )

        self.assertIsInstance(
            result,
            BarEntropyDrinkUnavailableResult,
        )

        self.assertEqual(
            result.name,
            "entropy_drink_not_available",
        )

        self.assertEqual(
            result.entity,
            "guest",
        )

        self.assertEqual(
            result.entity_type,
            "human",
        )

        self.assert_object_only(
            result
        )


if __name__ == "__main__":
    unittest.main()
