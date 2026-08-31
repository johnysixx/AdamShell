import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import CatGroupSystem

class CatGroupSystemTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.first = self.cats.create_cat(name='first', color='black', fur_length='short')
        self.second = self.cats.create_cat(name='second', color='white', fur_length='short')
        self.third = self.cats.create_cat(name='third', color='gray', fur_length='short')
        self.group_system = CatGroupSystem(self.cats)

    def _create_group(self):
        result = self.group_system.create_group(self.first, name='bar_cats')
        return result['group_id']

    def test_cat_can_create_group(self):
        group_id = self._create_group()
        self.assertTrue(self.first.group.member)
        self.assertEqual(self.first.group.group_id, group_id)

    def test_neutral_cat_can_join_group(self):
        group_id = self._create_group()
        result = self.group_system.add_member(group_id, self.second, self.cats.cats)
        self.assertTrue(result['joined'])
        self.assertTrue(self.group_system.same_group(self.first, self.second))

    def test_hostile_cat_is_rejected(self):
        group_id = self._create_group()
        self.first.relationships[self.second.name] = {'familiarity': 0.5, 'trust': 0.1, 'affiliation': 0.0, 'tension': 0.9}
        result = self.group_system.add_member(group_id, self.second, self.cats.cats)
        self.assertFalse(result['joined'])
        self.assertEqual(result['reason'], 'group_social_rejection')

    def test_group_scent_creates_shared_scent(self):
        group_id = self._create_group()
        self.group_system.add_member(group_id, self.second, self.cats.cats)
        result = self.group_system.mix_group_scent(group_id, self.cats.cats, amount=0.2)
        self.assertTrue(result['mixed'])
        self.assertGreater(self.first.relationships[self.second.name]['shared_scent'], 0.0)
        self.assertGreater(self.second.relationships[self.first.name]['shared_scent'], 0.0)

    def test_group_can_claim_shared_territory(self):
        group_id = self._create_group()
        self.group_system.add_member(group_id, self.second, self.cats.cats)
        result = self.group_system.claim_territory(group_id, self.cats.cats, layer='meeting_place', location='bar_window', strength=0.8)
        self.assertTrue(result['claimed'])
        key = 'meeting_place::bar_window'
        self.assertIn(key, self.first.territories)
        self.assertIn(key, self.second.territories)

    def test_group_responds_collectively_to_threat(self):
        group_id = self._create_group()
        self.group_system.add_member(group_id, self.second, self.cats.cats)
        self.first.personality.setdefault('traits', {})['courage'] = 1.0
        self.second.personality.setdefault('traits', {})['courage'] = 0.0
        result = self.group_system.respond_to_threat(group_id, self.cats.cats, threat={'name': 'cronenberg'})
        self.assertTrue(result['responded'])
        self.assertIn(self.first.name, result['defenders'])
        self.assertIn(self.second.name, result['withdrawers'])

    def test_cat_can_leave_group(self):
        group_id = self._create_group()
        self.group_system.add_member(group_id, self.second, self.cats.cats)
        result = self.group_system.leave_group(group_id, self.second)
        self.assertTrue(result['left'])
        self.assertFalse(self.second.group.member)
        self.assertFalse(self.group_system.same_group(self.first, self.second))

    def test_group_membership_does_not_create_bond(self):
        group_id = self._create_group()
        self.group_system.add_member(group_id, self.second, self.cats.cats)
        self.assertNotIn(self.second.name, self.first.bonds)
        self.assertNotIn(self.first.name, self.second.bonds)
if __name__ == '__main__':
    unittest.main()
