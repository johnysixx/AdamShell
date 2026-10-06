import unittest

from cats.cat_culture_objects import (
    CatTabooViolation,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_group_taboo_system import (
    CatGroupTabooSystem,
)
from cats.cat_group_taboo_violation_state import (
    CatGroupTabooViolationDeniedResult,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupTabooViolationResultObjectStateTests(
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

        self.taboos = (
            CatGroupTabooSystem(
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

    def test_unknown_taboo_returns_denied_object(
        self
    ):
        result = (
            self.taboos.violate(
                self.group_id,
                self.second,
                "missing_taboo",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupTabooViolationDeniedResult,
        )

        self.assertEqual(
            result.name,
            "cat_group_taboo_violation_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_taboo",
        )

        self.assertFalse(
            result.violated
        )

        self.assert_not_mapping(
            result
        )

    def test_denied_violation_does_not_touch_state(
        self
    ):
        group = (
            self.groups.groups[
                self.group_id
            ]
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
            self.taboos.violate(
                self.group_id,
                self.second,
                "missing_taboo",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupTabooViolationDeniedResult,
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

    def test_success_still_returns_taboo_violation_object(
        self
    ):
        defined = (
            self.taboos.define(
                self.group_id,
                "do_not_open_black_box",
                taboo_type="place_action",
                target={
                    "place": "black_box",
                    "action": "open",
                },
                severity=1.0,
            )
        )

        result = (
            self.taboos.violate(
                self.group_id,
                self.second,
                defined.taboo_id,
            )
        )

        self.assertIsInstance(
            result,
            CatTabooViolation,
        )

        self.assertTrue(
            result.violated
        )

        self.assertEqual(
            result.taboo_id,
            defined.taboo_id,
        )


if __name__ == "__main__":
    unittest.main()
