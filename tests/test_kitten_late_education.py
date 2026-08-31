import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.development_resolver import CatDevelopmentResolver
from cats.kitten_upbringing_resolver import KittenUpbringingResolver
from cats.feline_ability_resolver import FelineAbilityResolver

class KittenLateEducationTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.development = CatDevelopmentResolver(self.universe)
        self.upbringing = KittenUpbringingResolver(self.universe)
        self.abilities = FelineAbilityResolver(self.universe)
        self.mother = self.cats.create_cat(name='mother', color='black', fur_length='short', origin='natural_birth')
        self.garfield = self.cats.create_cat(name='garfield', color='orange', fur_length='short', origin='canonical_birth')
        self.dice_teacher = self.cats.create_cat(name='dice_teacher', color='gray', fur_length='short', origin='dice_manifestation')
        self.kitten = self.cats.create_cat(name='kitten', color='white', fur_length='short', origin='kitten_birth_resolver')
        self.kitten.parents = {'mother': 'mother', 'father': None}
        self.kitten.mother_name = 'mother'
        self.development.initialize_newborn(self.kitten, birth_day=0)
        self.complete_early_education()
        self.mother.learning['meow_knowledge'].update({'learned': True, 'understood': True, 'can_speak': True, 'teacher': 'garfield', 'source': 'bootstrap'})
        self.dice_teacher.learning['meow_knowledge'].update({'learned': True, 'understood': True, 'can_speak': True, 'teacher': 'garfield', 'source': 'bootstrap'})
        self.abilities.register_garfield_teaching_abilities(self.garfield)

    def complete_early_education(self):
        learning = self.kitten.learning
        for skill_name in ('socialization', 'litter_box', 'box_travel', 'cat_door_travel', 'hunting'):
            learning['skills'][skill_name].update({'learned': True, 'progress': 1.0, 'teacher': 'mother', 'learned_on_day': 50})

    def run_at_age(self, age_days):
        self.kitten.age_days = age_days
        return self.upbringing.tick_day(kitten=self.kitten, cats=self.cats.cats, current_day=age_days)

    def teach_all_vocalizations(self):
        for age in range(60, 68):
            self.run_at_age(age)

    def complete_hunting_education(self):
        self.run_at_age(35)
        for age in range(36, 39):
            self.run_at_age(age)
        hunting = self.kitten.learning['skills']['hunting']
        self.assertTrue(hunting['learned'])

    def test_vocalizations_are_taught_one_per_day(self):
        result = self.run_at_age(60)
        lessons = [event for event in result['events'] if event.get('name') == 'adult_vocalization_learned']
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0]['vocalization'], 'food_request')

    def test_repertoire_is_complete_on_day_sixty_seven(self):
        self.teach_all_vocalizations()
        skill = self.kitten.learning['skills']['adult_meowing']
        self.assertTrue(skill['learned'])
        self.assertTrue(all(skill['vocalizations'].values()))

    def test_human_communication_is_learned_on_day_75(self):
        self.teach_all_vocalizations()
        result = self.run_at_age(75)
        event_names = {event['name'] for event in result['events']}
        self.assertIn('human_feline_communication_learned', event_names)
        self.assertTrue(self.kitten.learning['human_communication_learned'])

    def test_mother_transmits_meow_on_day_90(self):
        self.complete_hunting_education()
        self.teach_all_vocalizations()
        self.run_at_age(75)
        result = self.run_at_age(90)
        meow_event = next((event for event in result['events'] if event.get('name') == 'meow_knowledge_transmitted'))
        self.assertTrue(meow_event['transmitted'])
        self.assertEqual(meow_event['teacher_role'], 'biological_mother')
        self.assertTrue(self.kitten.learning['meow_knowledge']['learned'])

    def test_qualified_cat_teaches_orphaned_kitten(self):
        self.complete_hunting_education()
        self.teach_all_vocalizations()
        self.run_at_age(75)
        self.kitten.parents['mother'] = None
        self.kitten.learning['teacher_mother'] = 'dice_teacher'
        self.cats.cats.remove(self.mother)
        lesson = self.abilities.teach_method(teacher=self.garfield, student=self.dice_teacher, ability_name='teach_other_cats', method_name='garfield_teaching_method')
        self.assertTrue(lesson['learned'])
        result = self.run_at_age(90)
        meow_event = next((event for event in result['events'] if event.get('name') == 'meow_knowledge_transmitted'))
        self.assertTrue(meow_event['transmitted'])
        self.assertEqual(meow_event['teacher_role'], 'dice_cat_teacher')
        self.assertEqual(meow_event['mother'], 'dice_teacher')

    def test_unqualified_cat_cannot_replace_mother(self):
        self.complete_hunting_education()
        self.teach_all_vocalizations()
        self.run_at_age(75)
        self.kitten.parents['mother'] = None
        self.kitten.learning['teacher_mother'] = None
        self.cats.cats.remove(self.mother)
        self.cats.cats.remove(self.garfield)
        result = self.run_at_age(90)
        event_names = {event['name'] for event in result['events']}
        self.assertIn('meow_teacher_unavailable', event_names)
        self.assertFalse(self.kitten.learning['meow_knowledge']['learned'])
if __name__ == '__main__':
    unittest.main()
