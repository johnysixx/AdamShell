import unittest

from cats.cat_group_norm_observation_state import (
    CatGroupNormObservationDeniedResult,
    CatGroupNormObservedResult,
)
from cats.cat_group_norm_system import (
    CatGroupNormSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupNormObservationObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = (
            self.cats.create_cat(
                name="first",
                color="black",
                fur_length="short",
            )
        )

        self.second = (
            self.cats.create_cat(
                name="second",
                color="white",
                fur_length="short",
            )
        )

        self.groups = (
            CatGroupSystem(
                self.cats
            )
        )

        created_group = (
            self.groups.create_group(
                self.first,
                name="bar_cats",
            )
        )

        self.group_id = (
            created_group.group_id
        )

        self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        self.norms = (
            CatGroupNormSystem(
                self.groups
            )
        )

        created_norm = (
            self.norms.define(
                self.group_id,
                "protect_kittens",
                "protective",
                {
                    "action": "protect",
                    "target": "kitten",
                },
                importance=0.9,
            )
        )

        self.norm_id = (
            created_norm.norm_id
        )

    def assert_not_mapping(
        self,
        result,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "observed"
            ]

    def test_observe_returns_object_result(
        self
    ):
        result = (
            self.norms.observe(
                self.group_id,
                self.second,
                self.norm_id,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupNormObservedResult,
        )

        self.assertTrue(
            result.observed
        )

        self.assertEqual(
            result.name,
            "cat_group_norm_observed",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.cat,
            self.second.name,
        )

        self.assertEqual(
            result.norm_id,
            self.norm_id,
        )

        self.assert_not_mapping(
            result
        )

    def test_observe_increments_norm_object(
        self
    ):
        norm = (
            self.groups
            .groups[
                self.group_id
            ]
            .norms[
                self.norm_id
            ]
        )

        before = norm.observances

        result = (
            self.norms.observe(
                self.group_id,
                self.second,
                self.norm_id,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupNormObservedResult,
        )

        self.assertEqual(
            norm.observances,
            before + 1,
        )

    def test_unknown_norm_returns_denied_object(
        self
    ):
        result = (
            self.norms.observe(
                self.group_id,
                self.second,
                "missing_norm",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupNormObservationDeniedResult,
        )

        self.assertFalse(
            result.observed
        )

        self.assertEqual(
            result.name,
            "cat_group_norm_observation_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_norm",
        )

        self.assert_not_mapping(
            result
        )


if __name__ == "__main__":
    unittest.main()
