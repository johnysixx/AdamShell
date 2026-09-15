import unittest

from cats.cat_learning import CatLearning
from cats.cat_learning_state import (
    CatFamilyKnowledgeState,
    CatLearningState,
    CatMeowKnowledgeState,
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
            CatSkillState(),
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
            dict,
        )

        self.assertTrue(
            all(
                isinstance(
                    skill,
                    CatSkillState,
                )
                for skill
                in learning.skills.values()
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
                in learning.skills.values()
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
                in learning.skills.values()
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
            set(learning.skills),
            set(CatLearning.SKILLS),
        )

        vocalizations = (
            learning
            .skills["adult_meowing"]
            .vocalizations
        )

        self.assertEqual(
            set(vocalizations),
            set(
                CatLearning
                .ADULT_VOCALIZATIONS
            ),
        )

        self.assertFalse(
            any(
                vocalizations.values()
            )
        )

    def test_to_dict_is_detached_recursive_boundary(
        self
    ):
        learning = (
            CatLearning
            .create_newborn_state(
                mother_name="mother"
            )
        )

        learning.lessons.append({
            "name": "lesson",
            "details": [
                "original"
            ],
        })

        snapshot = (
            learning.to_dict()
        )

        self.assertIsInstance(
            snapshot,
            dict,
        )

        self.assertIsInstance(
            snapshot["meow_knowledge"],
            dict,
        )

        self.assertIsInstance(
            snapshot["skills"]["hunting"],
            dict,
        )

        self.assertIsInstance(
            snapshot["family_knowledge"],
            dict,
        )

        snapshot[
            "meow_knowledge"
        ][
            "contains"
        ].append(
            "changed"
        )

        snapshot[
            "skills"
        ][
            "hunting"
        ][
            "progress"
        ] = 1.0

        snapshot[
            "skills"
        ][
            "adult_meowing"
        ][
            "vocalizations"
        ][
            "food_request"
        ] = True

        snapshot[
            "family_knowledge"
        ][
            "parental_lessons"
        ] = 99

        snapshot[
            "lessons"
        ][0][
            "details"
        ].append(
            "changed"
        )

        self.assertNotIn(
            "changed",
            learning.meow_knowledge.contains,
        )

        self.assertEqual(
            learning
            .skills["hunting"]
            .progress,
            0.0,
        )

        self.assertFalse(
            learning
            .skills["adult_meowing"]
            .vocalizations["food_request"]
        )

        self.assertEqual(
            learning
            .family_knowledge
            .parental_lessons,
            0,
        )

        self.assertEqual(
            learning.lessons[0]["details"],
            [
                "original"
            ],
        )


if __name__ == "__main__":
    unittest.main()
