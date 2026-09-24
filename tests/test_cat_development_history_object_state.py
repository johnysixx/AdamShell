import unittest

from universe.universe import Universe
from cats import Cats
from cats.development_resolver import (
    CatAgeAdvancedEvent,
    CatDevelopmentResolver,
    CatDevelopmentStageTransition,
    NewbornCatDevelopmentInitializedEvent,
)


class CatDevelopmentHistoryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.start_big_bang()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="development_history_cat",
            color="black",
            fur_length="short",
            sex="female",
        )

        self.resolver = (
            CatDevelopmentResolver(
                self.universe
            )
        )

    def test_newborn_history_uses_object_state(
        self
    ):
        result = (
            self.resolver
            .initialize_newborn(
                self.cat,
                birth_day=10,
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            NewbornCatDevelopmentInitializedEvent,
        )

        self.assertEqual(
            event.birth_day,
            10,
        )

        self.assertEqual(
            result["stage"],
            "newborn",
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
            _ = event["stage"]

    def test_age_history_and_transitions_use_objects(
        self
    ):
        self.resolver.initialize_newborn(
            self.cat
        )

        result = (
            self.resolver
            .advance_age(
                self.cat,
                days=365,
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            CatAgeAdvancedEvent,
        )

        self.assertTrue(
            event.stage_changed
        )

        self.assertTrue(
            all(
                isinstance(
                    transition,
                    CatDevelopmentStageTransition,
                )
                for transition
                in event.transitions
            )
        )

        self.assertEqual(
            result["transitions"][0],
            {
                "day": 14,
                "stage":
                    "socializing_kitten",
            },
        )

        with self.assertRaises(TypeError):
            _ = event.transitions[0][
                "day"
            ]

    def test_boundary_snapshot_is_detached_from_history(
        self
    ):
        self.resolver.initialize_newborn(
            self.cat
        )

        result = (
            self.resolver
            .advance_age(
                self.cat,
                days=14,
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        result[
            "transitions"
        ][0][
            "stage"
        ] = "changed"

        self.assertEqual(
            event
            .transitions[0]
            .stage,
            "socializing_kitten",
        )

        self.assertEqual(
            self.universe
            .quantum_events[-1]
            ["transitions"][0]
            ["stage"],
            "socializing_kitten",
        )

    def test_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(TypeError):
            self.resolver.record_event(
                {
                    "name":
                        "cat_age_advanced",
                }
            )


if __name__ == "__main__":
    unittest.main()
