import unittest

from universe.universe import Universe
from cats import Cats
from cats.estrous_cycle_resolver import (
    CatEstrousCycleEvent,
    CatEstrousCycleResolver,
)
from cats.reproduction import (
    CatReproduction,
)


class CatEstrousCycleObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.start_big_bang()

        self.cats = Cats(
            self.universe
        )

        self.female = self.cats.create_cat(
            name="female",
            color="black",
            fur_length="short",
            sex="female",
        )

        self.resolver = (
            CatEstrousCycleResolver(
                self.universe
            )
        )

    def test_history_uses_object_state(
        self
    ):
        result = self.resolver.tick_day(
            self.female,
            day=1,
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            CatEstrousCycleEvent,
        )

        self.assertEqual(
            event.name,
            "cat_estrus_started",
        )
        self.assertEqual(
            event.phase,
            "estrus",
        )
        self.assertEqual(
            event.cycle_day,
            0,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = event["phase"]

        result["phase"] = "changed"

        self.assertEqual(
            event.phase,
            "estrus",
        )

    def test_inactive_boundary_shape_is_preserved(
        self
    ):
        self.female.reproduction = (
            CatReproduction.create_state(
                sex="female",
                neutered=True,
            )
        )

        result = self.resolver.tick_day(
            self.female,
            day=2,
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            CatEstrousCycleEvent,
        )

        self.assertEqual(
            event.reason,
            "neutered",
        )

        self.assertNotIn(
            "cycle_day",
            result,
        )

        self.assertEqual(
            result["reason"],
            "neutered",
        )

    def test_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(TypeError):
            self.resolver.record_event(
                {
                    "name": (
                        "cat_estrus_started"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
