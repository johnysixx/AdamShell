import unittest

from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_group_taboo_definition_state import (
    CatGroupTabooDefinedResult,
)
from cats.cat_group_taboo_system import (
    CatGroupTabooSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupTabooDefinitionObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.founder = (
            self.cats.create_cat(
                name="founder",
                color="black",
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
                self.founder,
                name="bar_cats",
            )
        )

        self.group_id = (
            created_group[
                "group_id"
            ]
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
                "taboo_id"
            ]

    def test_define_returns_object_result(
        self
    ):
        result = (
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

        self.assertIsInstance(
            result,
            CatGroupTabooDefinedResult,
        )

        self.assertTrue(
            result.defined
        )

        self.assertEqual(
            result.name,
            "cat_group_taboo_defined",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.taboo_name,
            "do_not_open_black_box",
        )

        self.assertIn(
            result.taboo_id,
            self.groups.groups[
                self.group_id
            ].taboos,
        )

        self.assert_not_mapping(
            result
        )

    def test_definition_creates_taboo_object(
        self
    ):
        result = (
            self.taboos.define(
                self.group_id,
                "protect_food",
                taboo_type="resource",
                target={
                    "resource": "food",
                },
                severity=0.7,
            )
        )

        taboo = (
            self.groups.groups[
                self.group_id
            ].taboos[
                result.taboo_id
            ]
        )

        self.assertEqual(
            taboo.id,
            result.taboo_id,
        )

        self.assertEqual(
            taboo.name,
            "protect_food",
        )

        self.assertEqual(
            taboo.type,
            "resource",
        )

        self.assertEqual(
            taboo.severity,
            0.7,
        )

        self.assertEqual(
            taboo.violations,
            0,
        )

        self.assertTrue(
            taboo.active
        )

    def test_definition_result_is_immutable(
        self
    ):
        result = (
            self.taboos.define(
                self.group_id,
                "quiet_zone",
                taboo_type="place_action",
                target={
                    "place": "sleeping_area",
                },
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            result.taboo_name = (
                "changed"
            )


if __name__ == "__main__":
    unittest.main()
