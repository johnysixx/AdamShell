import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.development_resolver import CatDevelopmentResolver
from cats.feline_wisdom import FelineWisdom
from cats.meow_knowledge_resolver import MeowKnowledgeResolver
from cats.feline_ability_resolver import FelineAbilityResolver

class MeowFelineWisdomIntegrationTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.development = CatDevelopmentResolver(self.universe)
        self.resolver = MeowKnowledgeResolver(self.universe)
        self.abilities = FelineAbilityResolver(self.universe)
        self.garfield = self.cats.create_cat(name='garfield', color='orange', fur_length='short', origin='canonical_birth')
        self.mother = self.cats.create_cat(name='mother', color='black', fur_length='short', origin='natural_birth')
        self.dice_cat = self.cats.create_cat(name='dice_cat', color='gray', fur_length='short', origin='dice_manifestation')
        self.other_cat = self.cats.create_cat(name='other_cat', color='orange', fur_length='short', origin='natural_birth')
        self.kitten = self.cats.create_cat(name='kitten', color='white', fur_length='short', origin='kitten_birth_resolver')
        self.kitten.parents = {'mother': 'mother', 'father': None}
        self.kitten.mother_name = 'mother'
        self.development.initialize_newborn(self.kitten, birth_day=0)
        self.abilities.register_garfield_teaching_abilities(self.garfield)
        self.complete_required_experiences()

    def complete_required_experiences(self):
        learning = self.kitten.learning
        for skill_name in self.resolver.REQUIRED_EXPERIENCES:
            skill = learning['skills'][skill_name]
            skill.update({'learned': True, 'progress': 1.0, 'teacher': 'mother', 'learned_on_day': 80})
        learning['adult_meowing_learned'] = True
        learning['human_communication_learned'] = True

    def test_mother_transmits_awareness_only(self):
        FelineWisdom.add_awareness(cat=self.mother, knowledge_name='open_human_door', domain='feline', description='Some cats can open human doors.', known_teachers=['pazuzu', 'queen_elisabeth'])
        FelineWisdom.learn_ability_method(cat=self.mother, ability_name='open_human_door', method_name='example_method', teacher_name='pazuzu', constraints={'requires_unlocked': True})
        result = self.resolver.transmit(mother=self.mother, kitten=self.kitten, current_day=90)
        wisdom = self.kitten.feline_wisdom
        self.assertTrue(result['transmitted'])
        self.assertEqual(result['teacher_role'], 'biological_mother')
        self.assertIn('open_human_door', wisdom['awareness'])
        self.assertNotIn('open_human_door', wisdom['abilities'])
        self.assertEqual(result['ability_methods_transferred'], 0)

    def test_unrelated_natural_cat_cannot_teach_meow(self):
        result = self.resolver.transmit(mother=self.other_cat, kitten=self.kitten, current_day=90)
        self.assertFalse(result['transmitted'])
        self.assertEqual(result['reason'], 'teacher_has_not_learned_to_teach')

    def test_dice_cat_can_teach_orphaned_kitten(self):
        self.kitten.parents['mother'] = None
        self.kitten.learning['teacher_mother'] = None
        teaching_lesson = self.abilities.teach_method(teacher=self.garfield, student=self.dice_cat, ability_name='teach_other_cats', method_name='garfield_teaching_method')
        self.assertTrue(teaching_lesson['learned'])
        FelineWisdom.add_awareness(cat=self.dice_cat, knowledge_name='open_human_door', domain='feline', known_teachers=['pazuzu', 'queen_elisabeth'])
        result = self.resolver.transmit(mother=self.dice_cat, kitten=self.kitten, current_day=90)
        self.assertTrue(result['transmitted'])
        self.assertEqual(result['teacher_role'], 'dice_cat_teacher')
        self.assertEqual(result['transmission_source'], 'qualified_dice_cat_transmission')
        self.assertIn('open_human_door', self.kitten.feline_wisdom['awareness'])

    def test_meow_ignores_forbidden_domains(self):
        teacher_wisdom = FelineWisdom.ensure_state(self.mother)
        teacher_wisdom['awareness']['forbidden_magic'] = {'name': 'forbidden_magic', 'domain': 'magic', 'known_to_exist': True}
        result = self.resolver.transmit(mother=self.mother, kitten=self.kitten, current_day=90)
        self.assertTrue(result['transmitted'])
        self.assertNotIn('forbidden_magic', self.kitten.feline_wisdom['awareness'])

    def test_untrained_dice_cat_cannot_teach_orphan(self):
        self.kitten.parents['mother'] = None
        self.kitten.learning['teacher_mother'] = None
        result = self.resolver.transmit(mother=self.dice_cat, kitten=self.kitten, current_day=90)
        self.assertFalse(result['transmitted'])
        self.assertEqual(result['reason'], 'teacher_has_not_learned_to_teach')
        self.assertFalse(self.kitten.learning['meow_knowledge']['learned'])
if __name__ == '__main__':
    unittest.main()
