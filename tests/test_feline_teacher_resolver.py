import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.feline_wisdom import FelineWisdom
from cats.feline_ability_resolver import FelineAbilityResolver
from cats.feline_teacher_resolver import FelineTeacherResolver

class FelineTeacherResolverTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.abilities = FelineAbilityResolver(self.universe)
        self.teachers = FelineTeacherResolver(self.universe)
        self.pazuzu = self.cats.create_cat(name='pazuzu', color='black', fur_length='short', origin='canonical_birth')
        self.queen = self.cats.create_cat(name='queen_elisabeth', color='calico', pattern='tricolor', eye_color='green', fur_length='long', origin='canonical_birth')
        self.garfield = self.cats.create_cat(name='garfield', color='orange', fur_length='short', origin='canonical_birth')
        self.kitten = self.cats.create_cat(name='kitten', color='white', pattern='tabby', fur_length='short', origin='kitten_birth_resolver')
        self.abilities.register_pazuzu_door_method(self.pazuzu)
        self.abilities.register_queen_elisabeth_door_method(self.queen)
        self.abilities.register_garfield_teaching_abilities(self.garfield)
        self.abilities.teach_method(teacher=self.garfield, student=self.pazuzu, ability_name='teach_other_cats', method_name='garfield_teaching_method')
        self.abilities.teach_method(teacher=self.garfield, student=self.queen, ability_name='teach_other_cats', method_name='garfield_teaching_method')

    def give_door_awareness(self, teacher_names=None):
        FelineWisdom.add_awareness(cat=self.kitten, knowledge_name='open_human_door', domain='feline', description='Some cats can open unlocked human doors.', known_teachers=teacher_names or ['pazuzu', 'queen_elisabeth'])

    def test_cat_without_awareness_cannot_search(self):
        result = self.teachers.find_teachers(student=self.kitten, ability_name='open_human_door')
        self.assertFalse(result['found'])
        self.assertEqual(result['reason'], 'ability_not_known_to_exist')

    def test_awareness_finds_both_verified_teachers(self):
        self.give_door_awareness()
        result = self.teachers.find_teachers(student=self.kitten, ability_name='open_human_door')
        self.assertTrue(result['found'])
        self.assertEqual(result['teacher_count'], 2)
        names = {teacher['name'] for teacher in result['teachers']}
        self.assertEqual(names, {'pazuzu', 'queen_elisabeth'})

    def test_unknown_teacher_name_is_not_trusted(self):
        self.give_door_awareness(teacher_names=['imaginary_cat'])
        result = self.teachers.find_teachers(student=self.kitten, ability_name='open_human_door')
        self.assertFalse(result['found'])
        self.assertEqual(result['reason'], 'no_available_verified_teacher')
        self.assertFalse(result['candidates'][0]['cat_found'])

    def test_named_cat_must_really_know_ability(self):
        ordinary_cat = self.cats.create_cat(name='ordinary_cat', color='gray', fur_length='short', origin='natural_birth')
        self.give_door_awareness(teacher_names=[ordinary_cat.name])
        result = self.teachers.find_teachers(student=self.kitten, ability_name='open_human_door')
        self.assertFalse(result['found'])
        self.assertFalse(result['candidates'][0]['knows_ability'])

    def test_cat_can_choose_pazuzu_method(self):
        self.give_door_awareness()
        result = self.teachers.choose_teacher(student=self.kitten, ability_name='open_human_door', method_name='hang_on_handle')
        self.assertTrue(result['chosen'])
        self.assertEqual(result['teacher'], 'pazuzu')

    def test_cat_can_choose_queen_method(self):
        self.give_door_awareness()
        result = self.teachers.choose_teacher(student=self.kitten, ability_name='open_human_door', method_name='pull_with_paw')
        self.assertTrue(result['chosen'])
        self.assertEqual(result['teacher'], 'queen_elisabeth')

    def test_request_lesson_teaches_real_method(self):
        self.give_door_awareness()
        result = self.teachers.request_lesson(student=self.kitten, ability_name='open_human_door', method_name='hang_on_handle', ability_resolver=self.abilities)
        self.assertTrue(result['learned'])
        self.assertEqual(result['teacher'], 'pazuzu')
        methods = self.kitten.feline_wisdom['abilities']['open_human_door']['methods']
        self.assertIn('hang_on_handle', methods)

    def test_awareness_does_not_teach_before_lesson(self):
        self.give_door_awareness()
        self.teachers.find_teachers(student=self.kitten, ability_name='open_human_door')
        wisdom = self.kitten.feline_wisdom
        self.assertNotIn('open_human_door', wisdom['abilities'])
if __name__ == '__main__':
    unittest.main()
