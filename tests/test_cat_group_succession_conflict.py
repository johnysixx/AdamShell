import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import CatGroupSystem
from cats.cat_group_role_system import CatGroupRoleSystem
from cats.cat_group_ritual_system import CatGroupRitualSystem
from cats.cat_group_institution_system import CatGroupInstitutionSystem
from cats.cat_group_succession_system import CatGroupSuccessionSystem
from cats.cat_group_institutional_conflict_system import CatGroupInstitutionalConflictSystem

class CatGroupSuccessionConflictTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.first = self.cats.create_cat(name='first', color='black', fur_length='short')
        self.second = self.cats.create_cat(name='second', color='white', fur_length='short')
        self.third = self.cats.create_cat(name='third', color='gray', fur_length='short')
        self.groups = CatGroupSystem(self.cats)
        self.group_id = self.groups.create_group(self.first, name='bar_cats')['group_id']
        self.groups.add_member(self.group_id, self.second, self.cats.cats)
        self.groups.add_member(self.group_id, self.third, self.cats.cats)
        for cat in (self.first, self.second):
            cat.personality.setdefault('traits', {})['courage'] = 1.0
            cat.group.influence = 0.8

    def test_role_can_pass_to_successor(self):
        roles = CatGroupRoleSystem(self.groups)
        roles.assign(self.group_id, self.first, 'guardian')
        succession = CatGroupSuccessionSystem(self.groups)
        result = succession.succeed(self.group_id, self.first, 'guardian', self.cats.cats)
        self.assertTrue(result['succeeded'])
        self.assertEqual(result['successor'], self.second.name)
        self.assertIn('guardian', self.second.group_roles.active)

    def test_departure_can_trigger_succession(self):
        roles = CatGroupRoleSystem(self.groups)
        roles.assign(self.group_id, self.first, 'guardian')
        succession = CatGroupSuccessionSystem(self.groups)
        result = succession.handle_departure(self.group_id, self.first, self.cats.cats)
        self.assertTrue(result['departed'])
        self.assertFalse(self.first.group.member)
        self.assertIn('guardian', self.second.group_roles.active)

    def test_missing_successor_weakens_institution(self):
        roles = CatGroupRoleSystem(self.groups)
        roles.assign(self.group_id, self.first, 'guardian')
        institutions = CatGroupInstitutionSystem(self.groups)
        institutions.establish(self.group_id, 'night_watch', 'protect_group', roles=['guardian'], rituals=[])
        for cat in (self.second, self.third):
            cat.personality.setdefault('traits', {})['courage'] = 0.0
            cat.group.influence = 0.0
        succession = CatGroupSuccessionSystem(self.groups)
        before = self.groups.groups[self.group_id].institutions['night_watch'].continuity
        result = succession.succeed(self.group_id, self.first, 'guardian', self.cats.cats)
        after = self.groups.groups[self.group_id].institutions['night_watch'].continuity
        self.assertFalse(result['succeeded'])
        self.assertLess(after, before)

    def _institutions(self):
        institutions = CatGroupInstitutionSystem(self.groups)
        institutions.establish(self.group_id, 'night_watch', 'protect_sleeping_group', roles=['guardian'], rituals=['evening_patrol'])
        institutions.establish(self.group_id, 'door_watch', 'control_box_door', roles=['guardian'], rituals=['door_patrol'])

    def test_shared_role_can_create_institutional_friction(self):
        self._institutions()
        conflict = CatGroupInstitutionalConflictSystem(self.groups)
        result = conflict.detect(self.group_id, 'night_watch', 'door_watch')
        self.assertTrue(result['conflict'])
        self.assertIn('guardian', result['shared_roles'])

    def test_conflict_weakens_both_institutions(self):
        self._institutions()
        conflict = CatGroupInstitutionalConflictSystem(self.groups)
        result = conflict.escalate(self.group_id, 'night_watch', 'door_watch', issue='guardian_attention', intensity=0.8)
        self.assertTrue(result['escalated'])
        group = self.groups.groups[self.group_id]
        self.assertLess(group.institutions['night_watch'].continuity, 1.0)
        self.assertLess(group.institutions['door_watch'].continuity, 1.0)

    def test_mediator_can_resolve_conflict(self):
        self._institutions()
        self.third.personality.setdefault('traits', {})['sociability'] = 1.0
        self.third.group.influence = 1.0
        roles = CatGroupRoleSystem(self.groups)
        assigned = roles.assign(self.group_id, self.third, 'mediator')
        self.assertTrue(assigned['assigned'])
        conflict = CatGroupInstitutionalConflictSystem(self.groups)
        created = conflict.escalate(self.group_id, 'night_watch', 'door_watch', issue='guardian_attention', intensity=0.4)
        result = conflict.mediate(self.group_id, created['conflict_id'], self.third)
        self.assertTrue(result['mediated'])
        self.assertTrue(result['resolved'])
if __name__ == '__main__':
    unittest.main()
