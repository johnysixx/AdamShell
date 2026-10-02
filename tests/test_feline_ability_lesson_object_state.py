import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.feline_ability_resolver import (
    FelineAbilityResolver,
)
from cats.feline_wisdom_state import (
    FelineAbilityLessonDeniedResult,
    FelineAbilityMethodLearnedEvent,
    FelineAbilityTeachingCronenbergResult,
)


class FelineAbilityLessonObjectStateTests(
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

        self.student = (
            self.cats.create_cat(
                name="student",
                color="gray",
                fur_length="short",
                origin="natural_birth",
            )
        )

        self.resolver.register_garfield_teaching_abilities(
            self.garfield
        )

        self.resolver.register_pazuzu_door_method(
            self.pazuzu
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

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "learned"
            ]

    def test_success_returns_and_stores_lesson_object(
        self
    ):
        result = (
            self.resolver
            .teach_method(
                teacher=self.garfield,
                student=self.student,
                ability_name=(
                    "teach_other_cats"
                ),
                method_name=(
                    "garfield_teaching_method"
                ),
            )
        )

        self.assertIsInstance(
            result,
            FelineAbilityMethodLearnedEvent,
        )

        self.assertTrue(
            result.learned
        )

        self.assertIs(
            result,
            self.student
            .feline_wisdom
            .lesson_history[-1],
        )

        self.assertTrue(
            result.teacher_personality.applied
        )

        self.assertTrue(
            result.student_personality.applied
        )

        self.assert_not_mapping(
            result
        )

        boundary = (
            result.to_dict()
        )

        boundary[
            "constraints"
        ][
            "changed"
        ] = True

        self.assertNotIn(
            "changed",
            result.constraints,
        )

        audit = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            audit,
            dict,
        )

        self.assertTrue(
            audit[
                "learned"
            ]
        )

    def test_denied_lesson_returns_result_object(
        self
    ):
        result = (
            self.resolver
            .teach_method(
                teacher=self.student,
                student=self.pazuzu,
                ability_name=(
                    "open_human_door"
                ),
                method_name=(
                    "hang_on_handle"
                ),
            )
        )

        self.assertIsInstance(
            result,
            FelineAbilityLessonDeniedResult,
        )

        self.assertFalse(
            result.learned
        )

        self.assertEqual(
            result.reason,
            "teacher_has_not_learned_to_teach",
        )

        self.assert_not_mapping(
            result
        )

        boundary = (
            result.to_dict()
        )

        boundary[
            "reason"
        ] = "changed"

        self.assertEqual(
            result.reason,
            "teacher_has_not_learned_to_teach",
        )

    def test_forbidden_teacher_creation_returns_cronenberg_object(
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
            .teach_method(
                teacher=self.pazuzu,
                student=self.student,
                ability_name=(
                    "teach_other_cats"
                ),
                method_name=(
                    "garfield_teaching_method"
                ),
            )
        )

        self.assertIsInstance(
            result,
            FelineAbilityTeachingCronenbergResult,
        )

        self.assertFalse(
            result.learned
        )

        self.assertTrue(
            result.cronenberg_created
        )

        self.assertEqual(
            result.cronenberg_id,
            self.universe
            .cronenbergs[-1]
            .id,
        )

        self.assert_not_mapping(
            result
        )


if __name__ == "__main__":
    unittest.main()
