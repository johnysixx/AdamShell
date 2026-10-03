import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.feline_ability_resolver import (
    FelineAbilityResolver,
)
from cats.feline_wisdom_state import (
    FelineTeachingPermissionResult,
)


class FelineTeachingPermissionObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.resolver = (
            FelineAbilityResolver(
                self.universe
            )
        )

        self.garfield = (
            self.cats.create_cat(
                name="garfield",
                color="orange",
                fur_length="short",
                origin="canonical_birth",
            )
        )

        self.pazuzu = (
            self.cats.create_cat(
                name="pazuzu",
                color="black",
                fur_length="short",
                origin="canonical_birth",
            )
        )

        self.foreign_cat = (
            self.cats.create_cat(
                name="foreign_cat",
                color="gray",
                fur_length="short",
                origin="natural_birth",
            )
        )

        self.kitten = (
            self.cats.create_cat(
                name="kitten",
                color="black",
                fur_length="short",
                origin="kitten_birth_resolver",
            )
        )

        self.kitten.family.parents.mother = None
        self.kitten.family.parents.father = (
            self.pazuzu.name
        )

        self.resolver.register_garfield_teaching_abilities(
            self.garfield
        )

    def assert_permission_object(
        self,
        result,
    ):
        self.assertIsInstance(
            result,
            FelineTeachingPermissionResult,
        )

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
                "allowed"
            ]

    def test_parent_permission_is_object(
        self
    ):
        result = (
            self.resolver
            ._check_teaching_permission(
                teacher=self.pazuzu,
                student=self.kitten,
                ability_name=(
                    "open_human_door"
                ),
            )
        )

        self.assert_permission_object(
            result
        )

        self.assertTrue(
            result.allowed
        )

        self.assertEqual(
            result.reason,
            "parent_teaching_own_kitten",
        )

        self.assertFalse(
            result.creates_cronenberg
        )

    def test_garfield_permission_is_object(
        self
    ):
        result = (
            self.resolver
            ._check_teaching_permission(
                teacher=self.garfield,
                student=self.foreign_cat,
                ability_name=(
                    "teach_other_cats"
                ),
            )
        )

        self.assert_permission_object(
            result
        )

        self.assertTrue(
            result.allowed
        )

        self.assertEqual(
            result.reason,
            "garfield_teaches_teaching",
        )

    def test_untrained_teacher_permission_is_denied_object(
        self
    ):
        result = (
            self.resolver
            ._check_teaching_permission(
                teacher=self.foreign_cat,
                student=self.pazuzu,
                ability_name=(
                    "open_human_door"
                ),
            )
        )

        self.assert_permission_object(
            result
        )

        self.assertFalse(
            result.allowed
        )

        self.assertEqual(
            result.reason,
            "teacher_has_not_learned_to_teach",
        )

        self.assertFalse(
            result.creates_cronenberg
        )

    def test_teacher_creation_permission_marks_cronenberg(
        self
    ):
        self.resolver.teach_method(
            teacher=self.garfield,
            student=self.pazuzu,
            ability_name=(
                "teach_other_cats"
            ),
            method_name=(
                "garfield_teaching_method"
            ),
        )

        result = (
            self.resolver
            ._check_teaching_permission(
                teacher=self.pazuzu,
                student=self.foreign_cat,
                ability_name=(
                    "teach_other_cats"
                ),
            )
        )

        self.assert_permission_object(
            result
        )

        self.assertFalse(
            result.allowed
        )

        self.assertTrue(
            result.creates_cronenberg
        )

        self.assertEqual(
            result.reason,
            (
                "teacher_cannot_create_"
                "non_offspring_teacher"
            ),
        )

    def test_meta_teacher_permission_is_allowed_object(
        self
    ):
        self.resolver.teach_method(
            teacher=self.garfield,
            student=self.pazuzu,
            ability_name=(
                "teach_teaching"
            ),
            method_name=(
                "garfield_meta_teaching_method"
            ),
        )

        result = (
            self.resolver
            ._check_teaching_permission(
                teacher=self.pazuzu,
                student=self.foreign_cat,
                ability_name=(
                    "teach_other_cats"
                ),
            )
        )

        self.assert_permission_object(
            result
        )

        self.assertTrue(
            result.allowed
        )

        self.assertEqual(
            result.reason,
            "meta_teacher_creates_teacher",
        )

        self.assertFalse(
            result.creates_cronenberg
        )


if __name__ == "__main__":
    unittest.main()
