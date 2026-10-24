import unittest

from cats.cat_learning import CatLearning
from cats.cat_learning_state import (
    CatFamilyKnowledgeState,
    CatLearningState,
    CatMeowKnowledgeState,
    CatSkillRegistry,
    CatSkillState,
)


class CatLearningObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        state,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "update",
            "setdefault",
            "__getitem__",
            "__setitem__",
            "__contains__",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    state,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = state[
                "learned"
            ]

    def test_learning_state_is_object_only(
        self
    ):
        self._assert_object_only(
            CatLearningState()
        )

    def test_nested_states_are_object_only(
        self
    ):
        for state in (
            CatMeowKnowledgeState(),
            CatSkillState(
                name="test"
            ),
            CatFamilyKnowledgeState(),
        ):
            with self.subTest(
                state=type(state).__name__
            ):
                self._assert_object_only(
                    state
                )

    def test_complete_factory_builds_object_graph(
        self
    ):
        learning = (
            CatLearning
            .create_complete_state()
        )

        self.assertIsInstance(
            learning,
            CatLearningState,
        )

        self.assertIsInstance(
            learning.meow_knowledge,
            CatMeowKnowledgeState,
        )

        self.assertIsInstance(
            learning.family_knowledge,
            CatFamilyKnowledgeState,
        )

        self.assertIsInstance(
            learning.skills,
            CatSkillRegistry,
        )

        self._assert_object_only(
            learning.skills
        )

        self.assertTrue(
            all(
                isinstance(
                    skill,
                    CatSkillState,
                )
                for skill
                in learning.skills.records()
            )
        )

    def test_complete_factory_preserves_values(
        self
    ):
        learning = (
            CatLearning
            .create_complete_state()
        )

        self.assertFalse(
            learning.teaching_required
        )

        self.assertIsNone(
            learning.teaching_deadline_days
        )

        self.assertTrue(
            learning.kitten_meowing_instinctive
        )

        self.assertTrue(
            learning.adult_meowing_learned
        )

        self.assertTrue(
            learning.human_communication_learned
        )

        self.assertTrue(
            learning.complete
        )

        self.assertTrue(
            learning.meow_knowledge.learned
        )

        self.assertEqual(
            tuple(
                learning
                .meow_knowledge
                .contains
            ),
            CatLearning.MEOW_CONTENTS,
        )

        self.assertTrue(
            all(
                skill.learned
                for skill
                in learning.skills.records()
            )
        )

    def test_newborn_factory_preserves_values(
        self
    ):
        learning = (
            CatLearning
            .create_newborn_state(
                mother_name="mother"
            )
        )

        self.assertTrue(
            learning.teaching_required
        )

        self.assertEqual(
            learning.teaching_deadline_days,
            CatLearning.MATERNAL_TEACHING_DAYS,
        )

        self.assertEqual(
            learning.teacher_mother,
            "mother",
        )

        self.assertFalse(
            learning.complete
        )

        self.assertFalse(
            learning.meow_knowledge.learned
        )

        self.assertFalse(
            any(
                skill.learned
                for skill
                in learning.skills.records()
            )
        )

    def test_skill_registry_has_object_values(
        self
    ):
        learning = (
            CatLearning
            .create_newborn_state()
        )

        self.assertEqual(
            set(learning.skills.names()),
            set(CatLearning.SKILLS),
        )

        vocalizations = (
            learning
            .skills.record("adult_meowing")
            .vocalizations
        )

        self.assertEqual(
            set(vocalizations.names()),
            set(
                CatLearning
                .ADULT_VOCALIZATIONS
            ),
        )

        self.assertEqual(
            vocalizations.learned_count(),
            0,
        )

    def test_learning_state_keeps_nested_state_object_only(
        self
    ):
        learning = (
            CatLearning
            .create_newborn_state(
                mother_name="mother"
            )
        )

        self._assert_object_only(
            learning
        )

        nested_objects = (
            learning.meow_knowledge,
            learning.family_knowledge,
            learning.skills.record(
                "hunting"
            ),
        )

        for obj in nested_objects:
            with self.subTest(
                obj=type(obj).__name__
            ):
                self._assert_object_only(
                    obj
                )

        self.assertEqual(
            tuple(
                learning.meow_knowledge.contains
            ),
            CatLearning.MEOW_CONTENTS,
        )

        self.assertEqual(
            learning
            .skills.record(
                "hunting"
            )
            .progress,
            0.0,
        )

        self.assertEqual(
            learning
            .family_knowledge
            .parental_lessons,
            0,
        )


if __name__ == "__main__":
    unittest.main()
