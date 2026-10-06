import unittest

from cats.cat_group_institution_inheritance_state import (
    CatGroupInstitutionsInheritedResult,
)
from cats.cat_group_institution_system import (
    CatGroupInstitutionSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupInstitutionInheritanceObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.parent_founder = (
            self.cats.create_cat(
                name="parent_founder",
                color="black",
                fur_length="short",
            )
        )

        self.child_founder = (
            self.cats.create_cat(
                name="child_founder",
                color="white",
                fur_length="short",
            )
        )

        self.groups = (
            CatGroupSystem(
                self.cats
            )
        )

        parent_created = (
            self.groups.create_group(
                self.parent_founder,
                name="parent_group",
            )
        )

        child_created = (
            self.groups.create_group(
                self.child_founder,
                name="child_group",
            )
        )

        self.parent_group_id = (
            parent_created.group_id
        )

        self.child_group_id = (
            child_created.group_id
        )

        self.institutions = (
            CatGroupInstitutionSystem(
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
                "institutions"
            ]

    def test_transfer_returns_object_result(
        self
    ):
        self.institutions.establish(
            self.parent_group_id,
            "night_watch",
            "protect_group",
            roles=[],
            rituals=[],
        )

        result = (
            self.institutions.transfer_after_split(
                self.parent_group_id,
                self.child_group_id,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupInstitutionsInheritedResult,
        )

        self.assertEqual(
            result.name,
            "cat_group_institutions_inherited",
        )

        self.assertEqual(
            result.parent_group,
            self.parent_group_id,
        )

        self.assertEqual(
            result.child_group,
            self.child_group_id,
        )

        self.assertEqual(
            result.institutions,
            (
                "night_watch",
            ),
        )

        self.assert_not_mapping(
            result
        )

    def test_transfer_copies_institution_state(
        self
    ):
        self.institutions.establish(
            self.parent_group_id,
            "night_watch",
            "protect_group",
            roles=[
                "guardian"
            ],
            rituals=[
                "evening_patrol"
            ],
        )

        parent_group = (
            self.groups.groups[
                self.parent_group_id
            ]
        )

        child_group = (
            self.groups.groups[
                self.child_group_id
            ]
        )

        original = (
            parent_group.institutions[
                "night_watch"
            ]
        )

        original.continuity = 0.8
        original.generations = 2

        result = (
            self.institutions.transfer_after_split(
                self.parent_group_id,
                self.child_group_id,
                retention=0.5,
            )
        )

        inherited = (
            child_group.institutions[
                result.institutions[
                    0
                ]
            ]
        )

        self.assertIsNot(
            inherited,
            original,
        )

        self.assertEqual(
            inherited.name,
            original.name,
        )

        self.assertEqual(
            inherited.purpose,
            original.purpose,
        )

        self.assertEqual(
            inherited.roles,
            original.roles,
        )

        self.assertEqual(
            inherited.rituals,
            original.rituals,
        )

        self.assertEqual(
            inherited.continuity,
            0.4,
        )

        self.assertEqual(
            inherited.generations,
            3,
        )

        self.assertEqual(
            inherited.inherited_from,
            self.parent_group_id,
        )

        self.assertEqual(
            original.continuity,
            0.8,
        )

        self.assertEqual(
            original.generations,
            2,
        )

    def test_multiple_institutions_are_returned_as_tuple(
        self
    ):
        self.institutions.establish(
            self.parent_group_id,
            "night_watch",
            "protect_group",
            roles=[],
            rituals=[],
        )

        self.institutions.establish(
            self.parent_group_id,
            "kitten_guard",
            "protect_kittens",
            roles=[],
            rituals=[],
        )

        result = (
            self.institutions.transfer_after_split(
                self.parent_group_id,
                self.child_group_id,
            )
        )

        self.assertIsInstance(
            result.institutions,
            tuple,
        )

        self.assertEqual(
            result.institutions,
            (
                "night_watch",
                "kitten_guard",
            ),
        )

        child_group = (
            self.groups.groups[
                self.child_group_id
            ]
        )

        self.assertIn(
            "night_watch",
            child_group.institutions,
        )

        self.assertIn(
            "kitten_guard",
            child_group.institutions,
        )

    def test_empty_parent_returns_empty_tuple(
        self
    ):
        result = (
            self.institutions.transfer_after_split(
                self.parent_group_id,
                self.child_group_id,
            )
        )

        self.assertEqual(
            result.institutions,
            (),
        )

    def test_result_is_immutable(
        self
    ):
        result = (
            self.institutions.transfer_after_split(
                self.parent_group_id,
                self.child_group_id,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            result.child_group = "changed"

        with self.assertRaises(
            AttributeError
        ):
            result.institutions = (
                "changed",
            )


if __name__ == "__main__":
    unittest.main()
