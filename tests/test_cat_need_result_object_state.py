import unittest
from dataclasses import FrozenInstanceError

from cats.cat_need_state import (
    CatNeedsAdvancedResult,
    CatNeedsSnapshot,
)
from cats.cat_need_system import (
    CatNeedRate,
    CatNeedSystem,
)
from cats.cats import Cats
from core.entity.components import (
    SpatialVector3,
)
from core.entity.domain_object import (
    DomainObject,
)
from universe.universe import Universe


class CatNeedResultObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = (
            self.cats.create_cat(
                name="needcat",
                color="black",
                fur_length="short",
            )
        )

    def test_need_rates_are_typed_immutable_records(self):
        rates = CatNeedSystem.RATES

        self.assertIsInstance(rates, tuple)
        self.assertEqual(
            tuple(
                (rate.need, rate.increment)
                for rate in rates
            ),
            (
                ("hunger", 0.025),
                ("thirst", 0.035),
                ("fatigue", 0.02),
                ("safety", 0.0),
                ("social", 0.018),
                ("curiosity", 0.015),
            ),
        )

        for rate in rates:
            self.assertIsInstance(rate, CatNeedRate)
            self.assertFalse(hasattr(rate, "get"))
            self.assertFalse(hasattr(rate, "items"))

            with self.assertRaises(TypeError):
                _ = rate["increment"]

    def test_need_rate_objects_reject_invalid_state(self):
        rate = CatNeedRate(
            need="hunger",
            increment=0.025,
        )

        with self.assertRaises(FrozenInstanceError):
            rate.increment = 9.0

        with self.assertRaises(TypeError):
            CatNeedRate("", 0.1)

        with self.assertRaises(TypeError):
            CatNeedRate("hunger", True)

        with self.assertRaises(ValueError):
            CatNeedRate("hunger", -0.1)

        with self.assertRaises(ValueError):
            CatNeedRate("hunger", float("nan"))

    def test_need_rate_order_preserves_dominant_selection(self):
        for rate in CatNeedSystem.RATES:
            setattr(
                self.cat.needs,
                rate.need,
                0.0,
            )

        result = CatNeedSystem.advance(self.cat)

        for rate in CatNeedSystem.RATES:
            self.assertAlmostEqual(
                getattr(self.cat.needs, rate.need),
                rate.increment,
            )

        self.assertEqual(result.dominant, "thirst")
        self.assertEqual(
            self.cat.needs.dominant,
            "thirst",
        )

        for rate in CatNeedSystem.RATES:
            setattr(
                self.cat.needs,
                rate.need,
                1.0,
            )

        tied = CatNeedSystem.advance(self.cat)

        self.assertEqual(tied.dominant, "hunger")
        self.assertEqual(
            self.cat.needs.dominant,
            "hunger",
        )

    def assert_not_mapping(
        self,
        value,
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
                    mapping_method,
                )
            )

        self.assertFalse(
            hasattr(
                value,
                "to_dict",
            )
        )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                "hunger"
            ]

    def test_live_needs_use_pure_domain_object(
        self
    ):
        self.assertIsInstance(
            self.cat.needs,
            DomainObject,
        )

        self.assertFalse(
            hasattr(
                self.cat.needs,
                "to_dict",
            )
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    self.cat.needs,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = self.cat.needs[
                "hunger"
            ]

    def test_advance_returns_object_result(
        self
    ):
        result = (
            CatNeedSystem.advance(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatNeedsAdvancedResult,
        )

        self.assertEqual(
            result.name,
            "cat_needs_advanced",
        )

        self.assertEqual(
            result.cat,
            self.cat.name,
        )

        self.assertEqual(
            result.dominant,
            self.cat.needs.dominant,
        )

        self.assertIsInstance(
            result.needs,
            CatNeedsSnapshot,
        )

        self.assertEqual(
            result.needs.tick,
            1,
        )

        self.assertEqual(
            result.needs.hunger,
            self.cat.needs.hunger,
        )

        self.assert_not_mapping(
            result
        )

        self.assert_not_mapping(
            result.needs
        )

    def test_advance_snapshot_is_detached_from_live_needs(
        self
    ):
        result = (
            CatNeedSystem.advance(
                self.cat
            )
        )

        hunger_at_advance = (
            result.needs.hunger
        )

        self.cat.needs.hunger = 1.0

        self.assertEqual(
            result.needs.hunger,
            hunger_at_advance,
        )

        self.assertNotEqual(
            result.needs.hunger,
            self.cat.needs.hunger,
        )

    def test_apply_action_returns_snapshot_object(
        self
    ):
        self.cat.needs.fatigue = 1.0

        result = (
            CatNeedSystem.apply_action(
                self.cat,
                "rest",
            )
        )

        self.assertIsInstance(
            result,
            CatNeedsSnapshot,
        )

        self.assertEqual(
            result.fatigue,
            0.65,
        )

        self.assertEqual(
            result.fatigue,
            self.cat.needs.fatigue,
        )

        self.assert_not_mapping(
            result
        )

    def test_autonomous_tick_keeps_typed_need_results(
        self
    ):
        self.cat.position = (
            SpatialVector3.zero()
        )

        report = self.cats.tick()

        tick_result = (
            report.cats[0].result
        )

        self.assertEqual(
            tick_result.mode,
            "thought_cycle",
        )

        self.assertIsInstance(
            tick_result.needs,
            CatNeedsAdvancedResult,
        )

        self.assertIsInstance(
            tick_result.needs_after_action,
            CatNeedsSnapshot,
        )


if __name__ == "__main__":
    unittest.main()
