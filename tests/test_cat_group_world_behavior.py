import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import CatGroupSystem
from cats.cat_group_bonding_system import CatGroupBondingSystem
from cats.cat_group_lifecycle_system import CatGroupLifecycleSystem
from cats.cat_group_migration_system import CatGroupMigrationSystem
from cats.cat_group_conflict_system import CatGroupConflictSystem
from cats.cat_group_split_system import CatGroupSplitSystem

class CatGroupWorldBehaviorTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.members = []
        for index in range(6):
            cat = self.cats.create_cat(name=f'cat_{index}', color='black', fur_length='short')
            self.members.append(cat)
        self.groups = CatGroupSystem(self.cats)

    def _group(self, members, name):
        created = self.groups.create_group(members[0], name=name)
        group_id = created['group_id']
        for cat in members[1:]:
            self.groups.add_member(group_id, cat, self.cats.cats)
        return group_id

    def test_group_lifecycle_reaches_stable_state(self):
        group_id = self._group(self.members[:3], 'first')
        bonding = CatGroupBondingSystem(self.groups)
        for _ in range(10):
            bonding.reinforce(group_id, self.cats.cats, amount=0.08)
        lifecycle = CatGroupLifecycleSystem(self.groups)
        result = lifecycle.advance(group_id, self.cats.cats)
        self.assertEqual(result['state'], 'stable')

    def test_group_can_migrate_together(self):
        group_id = self._group(self.members[:3], 'first')
        migration = CatGroupMigrationSystem(self.groups)
        result = migration.migrate(group_id, self.cats.cats, layer='meeting_place', location='back_room', position={'x': 2.0, 'y': 1.0, 'z': 0.0})
        self.assertTrue(result['migrated'])
        for cat in self.members[:3]:
            self.assertEqual(cat.location, 'back_room')
            self.assertEqual(cat.current_layer, 'meeting_place')

    def test_two_groups_can_have_territorial_conflict(self):
        first = self._group(self.members[:3], 'first')
        second = self._group(self.members[3:], 'second')
        self.groups.claim_territory(first, self.cats.cats, layer='meeting_place', location='window', strength=0.8)
        self.groups.claim_territory(second, self.cats.cats, layer='meeting_place', location='window', strength=0.8)
        conflict = CatGroupConflictSystem(self.groups)
        result = conflict.encounter(first, second, self.cats.cats)
        self.assertTrue(result['conflict'])
        self.assertIn(result['outcome'], {'standoff', 'first_group_prevailed', 'second_group_prevailed'})

    def test_group_conflict_increments_history(self):
        first = self._group(self.members[:3], 'first')
        second = self._group(self.members[3:], 'second')
        conflict = CatGroupConflictSystem(self.groups)
        conflict.resolve(first, second, self.cats.cats, resource='milk')
        self.assertEqual(self.groups.groups[first].conflict_count, 1)
        self.assertEqual(self.groups.groups[second].conflict_count, 1)

    def test_group_can_split_into_daughter_group(self):
        group_id = self._group(self.members[:4], 'parent')
        split = CatGroupSplitSystem(self.groups)
        result = split.split(group_id, self.cats.cats, departing_members=[self.members[2].name, self.members[3].name], new_name='daughter')
        self.assertTrue(result['split'])
        daughter = result['daughter_group']
        self.assertEqual(self.groups.groups[daughter].parent_group, group_id)
        self.assertIn(daughter, self.groups.groups[group_id].daughter_groups)

    def test_group_can_dissolve(self):
        group_id = self._group(self.members[:2], 'first')
        lifecycle = CatGroupLifecycleSystem(self.groups)
        result = lifecycle.dissolve(group_id, self.cats.cats, reason='members_disperse')
        self.assertTrue(result['dissolved'])
        self.assertEqual(self.groups.groups[group_id].state, 'dissolved')
        for cat in self.members[:2]:
            self.assertFalse(cat.group.member)
if __name__ == '__main__':
    unittest.main()

