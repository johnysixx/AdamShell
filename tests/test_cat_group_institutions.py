import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import CatGroupSystem
from cats.cat_group_role_system import CatGroupRoleSystem
from cats.cat_group_ritual_system import CatGroupRitualSystem
from cats.cat_group_institution_system import CatGroupInstitutionSystem

class CatGroupInstitutionTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.first = self.cats.create_cat(name='first', color='black', fur_length='short')
        self.second = self.cats.create_cat(name='second', color='white', fur_length='short')
        self.groups = CatGroupSystem(self.cats)
        self.group_id = self.groups.create_group(self.first, name='bar_cats')['group_id']
        self.groups.add_member(self.group_id, self.second, self.cats.cats)

    def test_cat_can_gain_dynamic_role(self):
        self.first.personality.setdefault('traits', {})['courage'] = 1.0
        self.first.group.influence = 0.8
        roles = CatGroupRoleSystem(self.groups)
        result = roles.assign(self.group_id, self.first, 'guardian')
        self.assertTrue(result['assigned'])
        self.assertIn('guardian', self.first.group_roles.active)

    def test_role_can_be_released(self):
        self.first.personality.setdefault('traits', {})['courage'] = 1.0
        self.first.group.influence = 1.0
        roles = CatGroupRoleSystem(self.groups)
        roles.assign(self.group_id, self.first, 'guardian')
        roles.release(self.group_id, self.first, 'guardian')
        self.assertNotIn('guardian', self.first.group_roles.active)

    def test_group_can_define_and_perform_ritual(self):
        rituals = CatGroupRitualSystem(self.groups)
        rituals.define(self.group_id, 'evening_patrol', 'territory', required_roles=['guardian'])
        result = rituals.perform(self.group_id, 'evening_patrol', [self.first, self.second])
        self.assertTrue(result['performed'])
        self.assertEqual(self.groups.groups[self.group_id].rituals['evening_patrol'].performances, 1)

    def test_ritual_strengthens_group_tradition(self):
        rituals = CatGroupRitualSystem(self.groups)
        rituals.define(self.group_id, 'evening_patrol', 'territory')
        rituals.perform(self.group_id, 'evening_patrol', [self.first])
        self.assertIn('evening_patrol', self.groups.groups[self.group_id].culture.traditions)

    def test_group_can_establish_institution(self):
        institutions = CatGroupInstitutionSystem(self.groups)
        result = institutions.establish(self.group_id, institution_name='night_watch', purpose='protect_sleeping_group', roles=['guardian'], rituals=['evening_patrol'])
        self.assertTrue(result['established'])
        self.assertIn('night_watch', self.groups.groups[self.group_id].institutions)

    def test_institution_strengthens_when_role_and_ritual_exist(self):
        self.first.personality.setdefault('traits', {})['courage'] = 1.0
        self.first.group.influence = 1.0
        roles = CatGroupRoleSystem(self.groups)
        roles.assign(self.group_id, self.first, 'guardian')
        rituals = CatGroupRitualSystem(self.groups)
        rituals.define(self.group_id, 'evening_patrol', 'territory')
        rituals.perform(self.group_id, 'evening_patrol', [self.first])
        institutions = CatGroupInstitutionSystem(self.groups)
        institutions.establish(self.group_id, 'night_watch', 'protect_group', roles=['guardian'], rituals=['evening_patrol'])
        before = self.groups.groups[self.group_id].institutions['night_watch'].generations
        result = institutions.maintain(self.group_id, 'night_watch')
        after = self.groups.groups[self.group_id].institutions['night_watch'].generations
        self.assertEqual(result['status'], 'maintained')
        self.assertGreater(after, before)
if __name__ == '__main__':
    unittest.main()
