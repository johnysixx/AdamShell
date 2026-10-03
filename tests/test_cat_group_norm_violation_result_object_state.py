import unittest

from cats.cat_culture_objects import (
    CatNormViolation,
)
from cats.cat_group_norm_system import (
    CatGroupNormSystem,
)
from cats.cat_group_norm_violation_state import (
    CatGroupNormViolationDeniedResult,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupNormViolationResultObjectStateTests(
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
            created_group[
                "group_id"
            ]
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
                "violated"
            ]

    def test_unknown_norm_returns_denied_object(
        self
    ):
        result = (
            self.norms.violate(
                self.group_id,
                self.second,
                "missing_norm",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupNormViolationDeniedResult,
        )

        self.assertEqual(
            result.name,
            "cat_group_norm_violation_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_norm",
        )

        self.assertFalse(
            result.violated
        )

        self.assert_not_mapping(
            result
        )

    def test_denied_violation_does_not_touch_histories(
        self
    ):
        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        group_history_before = (
            len(group.history)
        )

        group_violations_before = (
            len(
                group.norm_violations
            )
        )

        cat_violations_before = (
            len(
                self.second
                .norms
                .violations
            )
        )

        result = (
            self.norms.violate(
                self.group_id,
                self.second,
                "missing_norm",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupNormViolationDeniedResult,
        )

        self.assertEqual(
            len(group.history),
            group_history_before,
        )

        self.assertEqual(
            len(
                group.norm_violations
            ),
            group_violations_before,
        )

        self.assertEqual(
            len(
                self.second
                .norms
                .violations
            ),
            cat_violations_before,
        )

    def test_success_still_returns_norm_violation_object(
        self
    ):
        defined = (
            self.norms.define(
                self.group_id,
                "quiet_sleeping_area",
                "social",
                {
                    "action": "stay_quiet",
                },
                importance=0.5,
            )
        )

        result = (
            self.norms.violate(
                self.group_id,
                self.second,
                defined.norm_id,
            )
        )

        self.assertIsInstance(
            result,
            CatNormViolation,
        )

        self.assertTrue(
            result.violated
        )

        self.assertEqual(
            result.norm_id,
            defined.norm_id,
        )


if __name__ == "__main__":
    unittest.main()
