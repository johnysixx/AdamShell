import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_family_system import CatFamilySystem
from cats.cat_maternal_care_system import CatMaternalCareSystem
from cats.cat_sibling_play_system import CatSiblingPlaySystem
from cats.cat_social_objects import CatRelationship

class CatFamilyCareIntegrationTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.mother = self.cats.create_cat(name='mother', color='black', fur_length='short')
        self.mother.sex = 'female'
        self.first = self.cats.create_cat(name='kitten_1', color='black', fur_length='short')
        self.second = self.cats.create_cat(name='kitten_2', color='black', fur_length='short')
        for kitten in (self.first, self.second):
            kitten.mother_name = self.mother.name
            kitten.father_name = 'father'
        family = CatFamilySystem(self.cats)
        family.register_birth(mother=self.mother, kittens=[self.first, self.second], cats=self.cats.cats)

    def test_existing_upbringing_events_sync_maternal_state(self):
        care = CatMaternalCareSystem(self.cats)
        existing_events = [{'name': 'fed_by_mother'}, {'name': 'cleaned_by_mother'}, {'name': 'warmed_by_mother'}, {'name': 'protected_by_mother'}]
        result = care.record_upbringing_care(mother=self.mother, kitten=self.first, events=existing_events, age_days=5, current_day=100)
        self.assertTrue(result['synced'])
        received = self.first.maternal_care_received
        self.assertEqual(received.nursing_events, 1)
        self.assertEqual(received.cleaning_events, 1)
        self.assertEqual(received.warming_events, 1)
        self.assertEqual(received.protection_events, 1)

    def test_sync_does_not_perform_second_feeding(self):
        care = CatMaternalCareSystem(self.cats)
        before_size = self.first.size
        care.record_upbringing_care(mother=self.mother, kitten=self.first, events=[{'name': 'fed_by_mother'}], age_days=5)
        self.assertEqual(self.first.size, before_size)

    def test_mother_can_protect_kitten_from_threat(self):
        care = CatMaternalCareSystem(self.cats)
        result = care.protect_from_threat(mother=self.mother, kitten=self.first, threat={'name': 'cronenberg'}, current_day=12)
        self.assertTrue(result['protected'])
        self.assertEqual(self.mother.state, 'protecting_kitten')
        self.assertEqual(self.first.state, 'protected_by_mother')
        self.assertEqual(self.first.maternal_care_received.protection_events, 1)

    def test_littermates_can_play(self):
        play = CatSiblingPlaySystem(self.cats)
        result = play.play(self.first, self.second, age_days=30, current_day=200)
        self.assertTrue(result['played'])
        self.assertEqual(result['relation'], 'sibling_littermate')
        self.assertEqual(self.first.sibling_play.play_events, 1)
        self.assertEqual(self.second.sibling_play.play_events, 1)

    def test_sibling_play_strengthens_relationship(self):
        play = CatSiblingPlaySystem(self.cats)
        play.play(self.first, self.second, age_days=30)
        relation = self.first.relationships[self.second.name]
        reverse = self.second.relationships[self.first.name]
        self.assertIsInstance(relation, CatRelationship)
        self.assertIsInstance(reverse, CatRelationship)
        self.assertIsNot(relation, reverse)
        for record in (relation, reverse):
            self.assertAlmostEqual(record.familiarity, 0.04)
            self.assertAlmostEqual(record.trust, 0.52)
            self.assertAlmostEqual(record.affiliation, 0.03)
            self.assertEqual(record.last_interaction, 'sibling_play')

    def test_non_littermates_cannot_use_sibling_play(self):
        stranger = self.cats.create_cat(name='stranger', color='gray', fur_length='short')
        play = CatSiblingPlaySystem(self.cats)
        result = play.play(self.first, stranger, age_days=30)
        self.assertFalse(result['played'])

    def test_repeated_play_preserves_existing_relationship_records(self):
        relation = CatRelationship.create()
        relation.trust = 0.8
        relation.familiarity = 0.2
        relation.shared_scent = 0.3
        relation.meet_count = 4
        history = [{'reason': 'past_meeting'}]
        relation.trust_history = history
        legacy = {'trust': 0.7, 'custom_note': 'known_before_play'}
        self.first.relationships[self.second.name] = relation
        self.second.relationships[self.first.name] = legacy

        play = CatSiblingPlaySystem(self.cats)
        for _ in range(2):
            result = play.play(self.first, self.second, age_days=30)
            self.assertTrue(result['played'])

        self.assertIs(self.first.relationships[self.second.name], relation)
        self.assertIs(self.second.relationships[self.first.name], legacy)
        self.assertAlmostEqual(relation.trust, 0.84)
        self.assertAlmostEqual(relation.familiarity, 0.28)
        self.assertAlmostEqual(relation.shared_scent, 0.3)
        self.assertEqual(relation.meet_count, 4)
        self.assertIs(relation.trust_history, history)
        self.assertEqual(relation.last_interaction, 'sibling_play')
        self.assertAlmostEqual(legacy['trust'], 0.74)
        self.assertAlmostEqual(legacy['familiarity'], 0.08)
        self.assertEqual(legacy['custom_note'], 'known_before_play')


if __name__ == '__main__':
    unittest.main()
