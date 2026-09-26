import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.feline_wisdom import FelineWisdom
from cats.feline_ability_resolver import (
    FelineAbilityResolver,
)
from cats.feline_teacher_resolver import (
    FelineAbilityLessonRequestedEvent,
    FelineAbilityTeacherChosenEvent,
    FelineAbilityTeacherSearchEvent,
    FelineTeacherCandidate,
    FelineTeacherMatch,
    FelineTeacherResolver,
)


class FelineTeacherHistoryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.abilities = (
            FelineAbilityResolver(
                self.universe
            )
        )

        self.resolver = (
            FelineTeacherResolver(
                self.universe
            )
        )

        self.pazuzu = (
            self.cats.create_cat(
                name="pazuzu",
                color="black",
                fur_length="short",
                origin=(
                    "canonical_birth"
                ),
            )
        )

        self.garfield = (
            self.cats.create_cat(
                name="garfield",
                color="orange",
                fur_length="short",
                origin=(
                    "canonical_birth"
                ),
            )
        )

        self.kitten = (
            self.cats.create_cat(
                name="kitten",
                color="white",
                fur_length="short",
                origin=(
                    "kitten_birth_resolver"
                ),
            )
        )

        self.abilities.register_pazuzu_door_method(
            self.pazuzu
        )

        self.abilities.register_garfield_teaching_abilities(
            self.garfield
        )

        self.abilities.teach_method(
            teacher=self.garfield,
            student=self.pazuzu,
            ability_name=(
                "teach_other_cats"
            ),
            method_name=(
                "garfield_teaching_method"
            ),
        )

        FelineWisdom.add_awareness(
            cat=self.kitten,
            knowledge_name=(
                "open_human_door"
            ),
            domain="feline",
            description=(
                "Some cats can open "
                "unlocked human doors."
            ),
            known_teachers=[
                "pazuzu"
            ],
        )

    def test_search_history_uses_nested_object_state(
        self
    ):
        result = (
            self.resolver
            .find_teachers(
                student=self.kitten,
                ability_name=(
                    "open_human_door"
                ),
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            FelineAbilityTeacherSearchEvent,
        )

        self.assertIsInstance(
            event.candidates[0],
            FelineTeacherCandidate,
        )

        self.assertIsInstance(
            event.teachers[0],
            FelineTeacherMatch,
        )

        self.assertIs(
            event.teachers[0].cat,
            self.pazuzu,
        )

        for obj in (
            event,
            event.candidates[0],
            event.teachers[0],
        ):
            self.assertFalse(
                hasattr(
                    obj,
                    "get"
                )
            )

            self.assertFalse(
                hasattr(
                    obj,
                    "items"
                )
            )

            with self.assertRaises(
                TypeError
            ):
                _ = obj["name"]

        result[
            "candidates"
        ][0][
            "methods"
        ].append(
            "changed"
        )

        self.assertNotIn(
            "changed",
            event.candidates[0].methods,
        )

    def test_choose_teacher_history_uses_chosen_event(
        self
    ):
        result = (
            self.resolver
            .choose_teacher(
                student=self.kitten,
                ability_name=(
                    "open_human_door"
                ),
                method_name=(
                    "hang_on_handle"
                ),
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            FelineAbilityTeacherChosenEvent,
        )

        self.assertEqual(
            event.teacher,
            "pazuzu",
        )

        self.assertIs(
            result["teacher_cat"],
            self.pazuzu,
        )

        result[
            "available_methods"
        ].append(
            "changed"
        )

        self.assertNotIn(
            "changed",
            event.available_methods,
        )

    def test_lesson_history_freezes_nested_lesson_and_keeps_boundary_dict(
        self
    ):
        result = (
            self.resolver
            .request_lesson(
                student=self.kitten,
                ability_name=(
                    "open_human_door"
                ),
                ability_resolver=(
                    self.abilities
                ),
                method_name=(
                    "hang_on_handle"
                ),
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            FelineAbilityLessonRequestedEvent,
        )

        with self.assertRaises(
            TypeError
        ):
            event.lesson[
                "learned"
            ] = False

        result[
            "lesson"
        ][
            "learned"
        ] = False

        self.assertTrue(
            event.lesson[
                "learned"
            ]
        )

        audit = (
            self.universe
            .quantum_events[-1]
        )

        self.assertIsInstance(
            audit,
            dict,
        )

        audit[
            "learned"
        ] = False

        self.assertTrue(
            event.learned
        )

    def test_history_rejects_mapping(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            self.resolver._record(
                {
                    "name": (
                        "feline_ability_"
                        "teacher_search"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
