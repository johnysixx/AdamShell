import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_family_system import CatFamilySystem
from cats.cat_maternal_care_system import CatMaternalCareSystem

class CatMaternalCareSystemTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.mother = self.cats.create_cat(name='mother', color='black', fur_length='short')
        self.mother.sex = 'female'
        self.kitten = self.cats.create_cat(name='kitten', color='black', fur_length='short')
        self.kitten.mother_name = self.mother.name
        self.kitten.father_name = 'father'
        family = CatFamilySystem(self.cats)
        family.register_birth(mother=self.mother, kittens=[self.kitten], cats=self.cats.cats)
        self.care = CatMaternalCareSystem(self.cats)

    def test_neonatal_kitten_gets_complete_care(self):
        result = self.care.provide_care(self.mother, self.kitten, age_days=5, current_day=100)
        self.assertTrue(result['provided'])
        self.assertEqual(result['phase'], 'neonatal_maternal_care')
        self.assertIn('nursing', result['actions'])
        self.assertIn('cleaning', result['actions'])
        self.assertIn('warming', result['actions'])
        self.assertIn('protection', result['actions'])
        self.assertIn('retrieval', result['actions'])

    def test_warming_stops_after_neonatal_phase(self):
        result = self.care.provide_care(self.mother, self.kitten, age_days=20)
        self.assertEqual(result['phase'], 'complete_maternal_care')
        self.assertNotIn('warming', result['actions'])

    def test_weaning_phase_keeps_reduced_care(self):
        result = self.care.provide_care(self.mother, self.kitten, age_days=40)
        self.assertEqual(result['phase'], 'reduced_maternal_care')
        self.assertIn('nursing', result['actions'])
        self.assertNotIn('retrieval', result['actions'])

    def test_independent_kitten_is_no_longer_nursed(self):
        result = self.care.provide_care(self.mother, self.kitten, age_days=70)
        self.assertEqual(result['phase'], 'maternal_independence')
        self.assertNotIn('nursing', result['actions'])
        self.assertIn('protection', result['actions'])

    def test_maternal_care_is_persisted(self):
        self.care.provide_care(self.mother, self.kitten, age_days=5, current_day=20)
        self.assertEqual(self.mother.maternal_care.care_events, 1)
        self.assertEqual(self.kitten.maternal_care_received.mother, self.mother.name)
        self.assertEqual(self.kitten.maternal_care_received.nursing_events, 1)
        self.assertEqual(self.kitten.maternal_care_received.warming_events, 1)

    def test_non_mother_cannot_provide_maternal_care(self):
        stranger = self.cats.create_cat(name='stranger', color='white', fur_length='short')
        stranger.sex = 'female'
        result = self.care.provide_care(stranger, self.kitten, age_days=5)
        self.assertFalse(result['provided'])
        self.assertEqual(result['reason'], 'not_biological_mother')
if __name__ == '__main__':
    unittest.main()
