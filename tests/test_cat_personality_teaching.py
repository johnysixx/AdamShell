import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.feline_ability_resolver import FelineAbilityResolver

class CatPersonalityTeachingTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.resolver = FelineAbilityResolver(self.universe)
        self.garfield = self.cats.create_cat(name='garfield', color='orange', fur_length='short', origin='canonical_birth')
        self.student = self.cats.create_cat(name='student', color='gray', fur_length='short', origin='natural_birth')
        self.resolver.register_garfield_teaching_abilities(self.garfield)

    def traits(self, cat):
        return cat.personality['traits']

    def test_successful_lesson_shapes_teacher(self):
        result = self.resolver.teach_method(teacher=self.garfield, student=self.student, ability_name='teach_other_cats', method_name='garfield_teaching_method')
        self.assertTrue(result['learned'])
        self.assertAlmostEqual(self.traits(self.garfield)['empathy'], 0.52)
        self.assertAlmostEqual(self.traits(self.garfield)['patience'], 0.515)
        self.assertTrue(result['teacher_personality']['applied'])

    def test_successful_lesson_builds_student_curiosity(self):
        result = self.resolver.teach_method(teacher=self.garfield, student=self.student, ability_name='teach_other_cats', method_name='garfield_teaching_method')
        self.assertTrue(result['learned'])
        self.assertAlmostEqual(self.traits(self.student)['curiosity'], 0.51)
        self.assertTrue(result['student_personality']['applied'])

    def test_denied_lesson_changes_no_personality(self):
        unqualified = self.cats.create_cat(name='unqualified', color='white', fur_length='short', origin='natural_birth')
        result = self.resolver.teach_method(teacher=unqualified, student=self.student, ability_name='teach_other_cats', method_name='garfield_teaching_method')
        self.assertFalse(result.get('learned', False))
        self.assertEqual(self.traits(unqualified)['empathy'], 0.5)
        self.assertEqual(self.traits(unqualified)['patience'], 0.5)
        self.assertEqual(self.traits(self.student)['curiosity'], 0.5)
if __name__ == '__main__':
    unittest.main()
