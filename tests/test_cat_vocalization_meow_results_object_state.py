import unittest

from universe.universe import Universe

from cats.adult_vocalization_resolver import (
    AdultVocalizationResolver,
)
from cats.adult_vocalization_result_state import (
    AdultVocalizationLearnedEvent,
    AdultVocalizationRepertoireTaughtEvent,
)
from cats.cats import Cats
from cats.development_resolver import (
    CatDevelopmentResolver,
)
from cats.meow_knowledge_resolver import (
    MeowKnowledgeResolver,
)
from cats.meow_knowledge_result_state import (
    MeowKnowledgeLesson,
    MeowKnowledgeReadinessResult,
    MeowKnowledgeTransmittedEvent,
    MeowTeacherRoleResult,
)


class CatVocalizationMeowResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.development = (
            CatDevelopmentResolver(
                self.universe
            )
        )

        self.vocalization = (
            AdultVocalizationResolver(
                self.universe
            )
        )

        self.meow = (
            MeowKnowledgeResolver(
                self.universe
            )
        )

        self.mother = (
            self.cats.create_cat(
                name="object_voice_mother",
                color="black",
                fur_length="short",
                origin="natural_birth",
            )
        )

        self.kitten = (
            self.cats.create_cat(
                name="object_voice_kitten",
                color="white",
                fur_length="short",
                origin=(
                    "kitten_birth_resolver"
                ),
            )
        )

        self.kitten.mother_name = (
            self.mother.name
        )

        self.development.initialize_newborn(
            self.kitten,
            birth_day=0,
        )

    def assert_object_only(
        self,
        value,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                "name"
            ]

    def complete_required_experiences(
        self
    ):
        for skill_name in (
            self.meow.REQUIRED_EXPERIENCES
        ):
            skill = (
                self.kitten
                .learning
                .skills[
                    skill_name
                ]
            )

            skill.learned = True
            skill.progress = 1.0
            skill.teacher = self.mother.name
            skill.learned_on_day = 70

        (
            self.kitten
            .learning
            .adult_meowing_learned
        ) = True

        (
            self.kitten
            .learning
            .human_communication_learned
        ) = True

    def test_repertoire_result_contains_objects(
        self
    ):
        result = (
            self.vocalization.teach_all(
                teacher=self.mother,
                kitten=self.kitten,
                current_day=70,
            )
        )

        self.assertIsInstance(
            result,
            AdultVocalizationRepertoireTaughtEvent,
        )

        self.assertTrue(
            result.complete
        )

        self.assertIsInstance(
            result.results,
            tuple,
        )

        self.assertTrue(
            all(
                isinstance(
                    lesson,
                    AdultVocalizationLearnedEvent,
                )
                for lesson
                in result.results
            )
        )

        self.assertFalse(
            any(
                isinstance(
                    lesson,
                    dict,
                )
                for lesson
                in result.results
            )
        )

        self.assert_object_only(
            result
        )

    def test_vocalization_quantum_audit_is_object(
        self
    ):
        result = (
            self.vocalization.teach(
                teacher=self.mother,
                kitten=self.kitten,
                vocalization="food_request",
                current_day=60,
            )
        )

        audit = (
            self.universe
            .quantum_events[
                -1
            ]
        )

        self.assertIsInstance(
            audit,
            AdultVocalizationLearnedEvent,
        )

        self.assertEqual(
            audit,
            result,
        )

        self.assertIsNot(
            audit,
            result,
        )

        self.assert_object_only(
            audit
        )

    def test_meow_readiness_is_object(
        self
    ):
        readiness = (
            self.meow.can_receive_meow(
                self.kitten,
                self.mother,
            )
        )

        self.assertIsInstance(
            readiness,
            MeowKnowledgeReadinessResult,
        )

        self.assertFalse(
            readiness.allowed
        )

        self.assertEqual(
            readiness.reason,
            "required_experiences_missing",
        )

        self.assertIsInstance(
            readiness.missing_experiences,
            tuple,
        )

        self.assertIn(
            "hunting",
            readiness.missing_experiences,
        )

        self.assertIsInstance(
            readiness.teacher_role,
            MeowTeacherRoleResult,
        )

        self.assertEqual(
            readiness.teacher_role.role,
            "biological_mother",
        )

        self.assert_object_only(
            readiness
        )

        self.assert_object_only(
            readiness.teacher_role
        )

    def test_ready_meow_keeps_teacher_role_object(
        self
    ):
        self.complete_required_experiences()

        readiness = (
            self.meow.can_receive_meow(
                self.kitten,
                self.mother,
            )
        )

        self.assertTrue(
            readiness.allowed
        )

        self.assertEqual(
            readiness.reason,
            "ready_for_meow",
        )

        self.assertEqual(
            readiness.missing_experiences,
            (),
        )

        self.assertIsInstance(
            readiness.teacher_role,
            MeowTeacherRoleResult,
        )

        self.assertTrue(
            readiness.teacher_role.allowed
        )

        self.assertEqual(
            readiness.teacher_role.role,
            "biological_mother",
        )

    def test_meow_quantum_audit_is_object(
        self
    ):
        self.complete_required_experiences()

        result = self.meow.transmit(
            mother=self.mother,
            kitten=self.kitten,
            current_day=75,
        )

        audit = (
            self.universe
            .quantum_events[
                -1
            ]
        )

        self.assertIsInstance(
            result,
            MeowKnowledgeTransmittedEvent,
        )

        self.assertIsInstance(
            audit,
            MeowKnowledgeTransmittedEvent,
        )

        self.assertEqual(
            audit,
            result,
        )

        self.assertIsNot(
            audit,
            result,
        )

        self.assert_object_only(
            result
        )

        self.assert_object_only(
            audit
        )

    def test_learning_snapshot_serializes_pure_vocalization_lesson(
        self
    ):
        event = (
            self.vocalization.teach(
                teacher=self.mother,
                kitten=self.kitten,
                vocalization="food_request",
                current_day=60,
            )
        )

        self.assert_object_only(
            event
        )

        snapshot = (
            self.kitten
            .learning
            .to_dict()
        )

        lesson = (
            snapshot[
                "lessons"
            ][
                -1
            ]
        )

        self.assertIsInstance(
            lesson,
            dict,
        )

        self.assertEqual(
            lesson[
                "vocalization"
            ],
            "food_request",
        )

    def test_learning_snapshot_serializes_pure_meow_lesson(
        self
    ):
        self.complete_required_experiences()

        self.meow.transmit(
            mother=self.mother,
            kitten=self.kitten,
            current_day=75,
        )

        event = (
            self.kitten
            .learning
            .lessons[
                -1
            ]
        )

        self.assertIsInstance(
            event,
            MeowKnowledgeLesson,
        )

        self.assert_object_only(
            event
        )

        snapshot = (
            self.kitten
            .learning
            .to_dict()
        )

        lesson = (
            snapshot[
                "lessons"
            ][
                -1
            ]
        )

        self.assertIsInstance(
            lesson,
            dict,
        )

        self.assertEqual(
            lesson[
                "name"
            ],
            "mother_spoke_meow",
        )

        self.assertIsInstance(
            lesson[
                "knowledge"
            ],
            list,
        )


if __name__ == "__main__":
    unittest.main()
