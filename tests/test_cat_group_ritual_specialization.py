import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import CatGroupSystem
from cats.cat_group_role_system import CatGroupRoleSystem
from cats.cat_group_role_specialization_system import CatGroupRoleSpecializationSystem
from cats.cat_group_ritual_system import CatGroupRitualSystem
from cats.cat_group_ritual_evolution_system import CatGroupRitualEvolutionSystem
from cats.cat_group_institution_system import CatGroupInstitutionSystem
from cats.cat_group_split_system import CatGroupSplitSystem

class CatGroupRitualSpecializationTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.members = []
        for index in range(4):
            cat = self.cats.create_cat(name=f'cat_{index}', color='black', fur_length='short')
            self.members.append(cat)
        self.groups = CatGroupSystem(self.cats)
        created = self.groups.create_group(self.members[0], name='parent')
        self.group_id = created['group_id']
        for cat in self.members[1:]:
            self.groups.add_member(self.group_id, cat, self.cats.cats)

    def test_defined_ritual_has_lineage_origin(self):
        rituals = CatGroupRitualSystem(self.groups)
        rituals.define(self.group_id, 'evening_patrol', 'territory')
        ritual = self.groups.groups[self.group_id].rituals['evening_patrol']
        self.assertEqual(ritual.lineage_root, 'evening_patrol')
        self.assertEqual(ritual.generation, 0)

    def test_ritual_can_mutate_into_descendant(self):
        rituals = CatGroupRitualSystem(self.groups)
        rituals.define(self.group_id, 'evening_patrol', 'territory', required_roles=['guardian'])
        evolution = CatGroupRitualEvolutionSystem(self.groups)
        result = evolution.mutate(self.group_id, 'evening_patrol', 'silent_evening_patrol', required_roles=['night_guardian'])
        self.assertTrue(result['mutated'])
        child = self.groups.groups[self.group_id].rituals['silent_evening_patrol']
        self.assertEqual(child.parent_ritual, 'evening_patrol')
        self.assertEqual(child.generation, 1)

    def test_guardian_can_specialize(self):
        cat = self.members[0]
        cat.personality.setdefault('traits', {})['courage'] = 1.0
        roles = CatGroupRoleSystem(self.groups)
        assigned = roles.assign(self.group_id, cat, 'guardian')
        self.assertTrue(assigned['assigned'])
        specialization = CatGroupRoleSpecializationSystem(self.groups)
        result = specialization.specialize(self.group_id, cat, 'guardian', 'night_guardian')
        self.assertTrue(result['specialized'])
        self.assertIn('night_guardian', cat.group_roles.active)

    def test_specialization_requires_base_role(self):
        specialization = CatGroupRoleSpecializationSystem(self.groups)
        result = specialization.specialize(self.group_id, self.members[1], 'guardian', 'night_guardian')
        self.assertFalse(result['specialized'])
        self.assertEqual(result['reason'], 'base_role_not_held')

    def test_institution_is_inherited_after_group_split(self):
        institutions = CatGroupInstitutionSystem(self.groups)
        institutions.establish(self.group_id, 'night_watch', 'protect_group', roles=['guardian'], rituals=['evening_patrol'])
        split = CatGroupSplitSystem(self.groups)
        result = split.split(self.group_id, self.cats.cats, departing_members=[self.members[2].name, self.members[3].name], new_name='daughter')
        daughter = result['daughter_group']
        inherited = self.groups.groups[daughter].institutions['night_watch']
        self.assertEqual(inherited.inherited_from, self.group_id)
        self.assertLess(inherited.continuity, 1.0)
if __name__ == '__main__':
    unittest.main()
