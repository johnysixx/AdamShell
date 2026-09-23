import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.development_resolver import CatDevelopmentResolver
from cats.meow_knowledge_resolver import (
    MeowKnowledgeLesson,
    MeowKnowledgeTransmittedEvent,
    MeowKnowledgeTransmissionDeniedEvent,
    MeowKnowledgeResolver,
)

class MeowKnowledgeResolverTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.development = CatDevelopmentResolver(self.universe)
        self.meow = MeowKnowledgeResolver(self.universe)
        self.mother = self.cats.create_cat(name='mother', color='black', fur_length='short', origin='natural_birth')
        self.kitten = self.cats.create_cat(name='kitten', color='white', fur_length='short', origin='kitten_birth_resolver')
        self.kitten.mother_name = self.mother.name
        self.development.initialize_newborn(self.kitten, birth_day=0)

    def complete_required_experiences(self):
        for skill_name in self.meow.REQUIRED_EXPERIENCES:
            skill = self.kitten.learning.skills[skill_name]
            skill.learned = True
            skill.progress = 1.0
            skill.teacher = 'mother'
            skill.learned_on_day = 60
        self.kitten.learning.adult_meowing_learned = True
        self.kitten.learning.human_communication_learned = True

    def test_meow_is_denied_before_experiences(self):
        result = self.meow.transmit(mother=self.mother, kitten=self.kitten, current_day=30)
        self.assertFalse(result['transmitted'])
        self.assertEqual(result['reason'], 'required_experiences_missing')
        self.assertIn('hunting', result['missing_experiences'])
        self.assertFalse(self.kitten.learning.meow_knowledge.learned)

    def test_mother_must_know_meow(self):
        self.complete_required_experiences()
        self.mother.learning.meow_knowledge.learned = False
        result = self.meow.transmit(mother=self.mother, kitten=self.kitten, current_day=70)
        self.assertFalse(result['transmitted'])
        self.assertEqual(result['reason'], 'mother_does_not_know_meow')

    def test_ready_kitten_receives_complete_meow(self):
        self.complete_required_experiences()
        result = self.meow.transmit(mother=self.mother, kitten=self.kitten, current_day=75)
        learning = self.kitten.learning
        meow = learning.meow_knowledge
        self.assertTrue(result['transmitted'])
        self.assertEqual(result['name'], 'meow_knowledge_transmitted')
        self.assertTrue(meow.learned)
        self.assertTrue(meow.understood)
        self.assertTrue(meow.can_speak)
        self.assertEqual(meow.teacher, 'mother')
        self.assertEqual(meow.source, 'maternal_transmission')
        self.assertEqual(meow.learned_on_day, 75)

    def test_meow_completes_adult_vocalization(self):
        self.complete_required_experiences()
        self.meow.transmit(mother=self.mother, kitten=self.kitten, current_day=75)
        learning = self.kitten.learning
        adult_meowing = learning.skills['adult_meowing']
        human_communication = learning.skills['human_communication']
        self.assertTrue(adult_meowing.learned)
        self.assertTrue(human_communication.learned)
        self.assertTrue(learning.adult_meowing_learned)
        self.assertTrue(learning.human_communication_learned)

    def test_meow_completes_feline_education(self):
        self.complete_required_experiences()
        result = self.meow.transmit(mother=self.mother, kitten=self.kitten, current_day=75)
        learning = self.kitten.learning
        self.assertTrue(result['learning_complete'])
        self.assertTrue(learning.complete)
        self.assertFalse(learning.teaching_required)
        self.assertEqual(
            learning.lessons[-1].name,
            'mother_spoke_meow',
        )

    def test_successful_transmission_uses_object_state(
        self
    ):
        self.complete_required_experiences()

        result = self.meow.transmit(
            mother=self.mother,
            kitten=self.kitten,
            current_day=75,
        )

        event = self.meow.history[-1]
        lesson = (
            self.kitten
            .learning
            .lessons[-1]
        )

        self.assertIsInstance(
            event,
            MeowKnowledgeTransmittedEvent,
        )

        self.assertIsInstance(
            lesson,
            MeowKnowledgeLesson,
        )

        self.assertEqual(
            event.teacher_role,
            'biological_mother',
        )

        self.assertEqual(
            lesson.name,
            'mother_spoke_meow',
        )

        for value, key in (
            (
                event,
                'teacher_role',
            ),
            (
                lesson,
                'name',
            ),
        ):
            for mapping_method in (
                'get',
                'keys',
                'items',
                'values',
            ):
                self.assertFalse(
                    hasattr(
                        value,
                        mapping_method,
                    )
                )

            with self.assertRaises(TypeError):
                _ = value[key]

        result[
            'teacher_role'
        ] = 'changed'

        self.assertEqual(
            event.teacher_role,
            'biological_mother',
        )

    def test_denied_transmission_history_uses_object_state(
        self
    ):
        result = self.meow.transmit(
            mother=self.mother,
            kitten=self.kitten,
            current_day=30,
        )

        event = self.meow.history[-1]

        self.assertIsInstance(
            event,
            MeowKnowledgeTransmissionDeniedEvent,
        )

        self.assertEqual(
            event.reason,
            'required_experiences_missing',
        )

        self.assertIn(
            'hunting',
            event.missing_experiences,
        )

        self.assertFalse(
            event.transmitted
        )

        result['reason'] = 'changed'

        self.assertEqual(
            event.reason,
            'required_experiences_missing',
        )

        with self.assertRaises(TypeError):
            _ = event['reason']

    def test_learning_snapshot_serializes_meow_lesson_object(
        self
    ):
        self.complete_required_experiences()

        self.meow.transmit(
            mother=self.mother,
            kitten=self.kitten,
            current_day=75,
        )

        lesson = (
            self.kitten
            .learning
            .lessons[-1]
        )

        snapshot = (
            self.kitten
            .learning
            .to_dict()
        )

        lesson_snapshot = (
            snapshot['lessons'][-1]
        )

        self.assertEqual(
            lesson_snapshot['name'],
            'mother_spoke_meow',
        )

        lesson_snapshot[
            'name'
        ] = 'changed'

        self.assertEqual(
            lesson.name,
            'mother_spoke_meow',
        )

    def test_meow_cannot_be_transmitted_twice(self):
        self.complete_required_experiences()
        self.meow.transmit(mother=self.mother, kitten=self.kitten, current_day=75)
        second = self.meow.transmit(mother=self.mother, kitten=self.kitten, current_day=76)
        self.assertFalse(second['transmitted'])
        self.assertEqual(second['reason'], 'meow_already_known')
if __name__ == '__main__':
    unittest.main()
