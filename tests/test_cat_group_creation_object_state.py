import unittest

from cats.cat_group import (
    CatGroup,
    CatGroupCulture,
)
from cats.cat_group_creation_state import (
    CatGroupCreatedEvent,
    CatGroupCreatedResult,
    CatGroupCreationDeniedResult,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupCreationObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = self.cats.create_cat(
            name="first",
            color="black",
            fur_length="short",
        )

        self.groups = CatGroupSystem(
            self.cats
        )

    def assert_not_mapping(
        self,
        value,
        key,
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
                key
            ]

    def test_create_group_returns_result_object(
        self
    ):
        result = self.groups.create_group(
            self.first,
            name="bar_cats",
        )

        self.assertIsInstance(
            result,
            CatGroupCreatedResult,
        )

        self.assertTrue(
            result.created
        )

        self.assertEqual(
            result.group_name,
            "bar_cats",
        )

        self.assertEqual(
            result.founder,
            self.first.name,
        )

        self.assertIn(
            result.group_id,
            self.groups.groups,
        )

        self.assertIsInstance(
            result.group,
            CatGroup,
        )

        self.assertIsInstance(
            result.group.culture,
            CatGroupCulture,
        )

        self.assert_not_mapping(
            result,
            "group_id",
        )

    def test_returned_group_is_detached_snapshot(
        self
    ):
        result = self.groups.create_group(
            self.first,
            name="bar_cats",
        )

        live = self.groups.groups[
            result.group_id
        ]

        self.assertIsNot(
            result.group,
            live,
        )

        result.group.name = (
            "changed_snapshot"
        )

        self.assertEqual(
            live.name,
            "bar_cats",
        )

    def test_group_history_stores_creation_event_object(
        self
    ):
        result = self.groups.create_group(
            self.first,
            name="bar_cats",
        )

        event = (
            self.groups.groups[
                result.group_id
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            event,
            CatGroupCreatedEvent,
        )

        self.assertEqual(
            event.group_id,
            result.group_id,
        )

        self.assertEqual(
            event.group_name,
            result.group_name,
        )

        self.assertEqual(
            event.founder,
            result.founder,
        )

        self.assert_not_mapping(
            event,
            "group_id",
        )

    def test_founder_social_history_stores_creation_event_object(
        self
    ):
        result = self.groups.create_group(
            self.first,
            name="bar_cats",
        )

        event = (
            self.first
            .social_interactions[
                -1
            ]
        )

        self.assertIsInstance(
            event,
            CatGroupCreatedEvent,
        )

        self.assertEqual(
            event.group_id,
            result.group_id,
        )

        self.assert_not_mapping(
            event,
            "group_id",
        )

    def test_existing_member_creation_is_denied_by_object(
        self
    ):
        first_result = (
            self.groups.create_group(
                self.first,
                name="first_group",
            )
        )

        denied = (
            self.groups.create_group(
                self.first,
                name="second_group",
            )
        )

        self.assertIsInstance(
            denied,
            CatGroupCreationDeniedResult,
        )

        self.assertFalse(
            denied.created
        )

        self.assertEqual(
            denied.cat,
            self.first.name,
        )

        self.assertEqual(
            denied.reason,
            "already_group_member",
        )

        self.assertEqual(
            len(
                self.groups.groups
            ),
            1,
        )

        self.assertIn(
            first_result.group_id,
            self.groups.groups,
        )

        self.assert_not_mapping(
            denied,
            "created",
        )

    def test_creation_results_are_frozen(
        self
    ):
        result = self.groups.create_group(
            self.first,
            name="bar_cats",
        )

        with self.assertRaises(
            AttributeError
        ):
            result.group_id = "changed"

        denied = self.groups.create_group(
            self.first,
            name="other_group",
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.reason = "changed"


if __name__ == "__main__":
    unittest.main()
