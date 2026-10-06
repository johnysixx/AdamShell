import unittest

from cats.cat_group_leave_state import (
    CatGroupLeaveDeniedResult,
    CatLeftGroupEvent,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupLeaveObjectStateTests(
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

        self.groups = CatGroupSystem(
            self.cats
        )

        created = (
            self.groups.create_group(
                self.first,
                name="bar_cats",
            )
        )

        self.group_id = (
            created[
                "group_id"
            ]
        )

    def assert_not_mapping(
        self,
        value,
    ):
        for method_name in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    method_name,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                "left"
            ]

    def test_non_member_leave_returns_denied_object(
        self
    ):
        result = (
            self.groups.leave_group(
                self.group_id,
                self.second,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupLeaveDeniedResult,
        )

        self.assertFalse(
            result.left
        )

        self.assertEqual(
            result.reason,
            "not_member",
        )

        self.assertEqual(
            result.cat,
            self.second.name,
        )

        self.assert_not_mapping(
            result
        )

    def test_member_leave_returns_event_object(
        self
    ):
        self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        result = (
            self.groups.leave_group(
                self.group_id,
                self.second,
            )
        )

        self.assertIsInstance(
            result,
            CatLeftGroupEvent,
        )

        self.assertTrue(
            result.left
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
            result.member_count,
            1,
        )

        self.assertFalse(
            self.second.group.member
        )

        self.assertIsNone(
            self.second.group.group_id
        )

        self.assert_not_mapping(
            result
        )

    def test_leave_history_stores_detached_event_object(
        self
    ):
        self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        result = (
            self.groups.leave_group(
                self.group_id,
                self.second,
            )
        )

        stored = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatLeftGroupEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_not_mapping(
            stored
        )

    def test_cat_social_history_stores_detached_event_object(
        self
    ):
        self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        result = (
            self.groups.leave_group(
                self.group_id,
                self.second,
            )
        )

        stored = (
            self.second
            .social_interactions[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatLeftGroupEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_not_mapping(
            stored
        )

    def test_leave_results_are_frozen(
        self
    ):
        denied = (
            self.groups.leave_group(
                self.group_id,
                self.second,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.reason = (
                "changed"
            )

        self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        left = (
            self.groups.leave_group(
                self.group_id,
                self.second,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            left.cat = (
                "changed"
            )


if __name__ == "__main__":
    unittest.main()
