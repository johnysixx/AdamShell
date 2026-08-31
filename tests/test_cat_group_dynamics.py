import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import CatGroupSystem
from cats.cat_group_hierarchy_system import CatGroupHierarchySystem
from cats.cat_group_bonding_system import CatGroupBondingSystem
from cats.cat_group_recruitment_system import CatGroupRecruitmentSystem

class CatGroupDynamicsTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.first = self.cats.create_cat(name='first', color='black', fur_length='short')
        self.second = self.cats.create_cat(name='second', color='white', fur_length='short')
        self.third = self.cats.create_cat(name='third', color='gray', fur_length='short')
        self.candidate = self.cats.create_cat(name='candidate', color='orange', fur_length='short')
        self.groups = CatGroupSystem(self.cats)
        created = self.groups.create_group(self.first, name='bar_cats')
        self.group_id = created['group_id']
        self.groups.add_member(self.group_id, self.second, self.cats.cats)
        self.groups.add_member(self.group_id, self.third, self.cats.cats)

    def test_group_has_dynamic_influence_ranking(self):
        self.first.personality.setdefault('traits', {})['courage'] = 1.0
        self.first.group.defense_events = 5
        hierarchy = CatGroupHierarchySystem(self.groups)
        ranking = hierarchy.rank(self.group_id, self.cats.cats)
        self.assertEqual(ranking[0]['cat'], self.first.name)
        self.assertGreater(self.first.group.influence, 0.0)

    def test_group_bonding_can_raise_cohesion(self):
        bonding = CatGroupBondingSystem(self.groups)
        before = bonding.evaluate(self.group_id, self.cats.cats)['cohesion']
        for _ in range(10):
            bonding.reinforce(self.group_id, self.cats.cats, amount=0.08)
        after = bonding.evaluate(self.group_id, self.cats.cats)
        self.assertGreater(after['cohesion'], before)
        self.assertTrue(after['bonded_group'])

    def test_group_bond_does_not_create_personal_bond(self):
        bonding = CatGroupBondingSystem(self.groups)
        bonding.reinforce(self.group_id, self.cats.cats, amount=0.2)
        self.assertNotIn(self.second.name, self.first.bonds)

    def test_group_can_vote_candidate_in(self):
        recruitment = CatGroupRecruitmentSystem(self.groups)
        result = recruitment.recruit(self.group_id, self.candidate, self.cats.cats, sponsor=self.first)
        self.assertTrue(result['joined'])
        self.assertTrue(self.candidate.group.member)

    def test_severe_hostility_can_veto_candidate(self):
        self.second.relationships[self.candidate.name] = {'trust': 0.0, 'affiliation': 0.0, 'familiarity': 0.8, 'tension': 1.0, 'shared_scent': 0.0}
        recruitment = CatGroupRecruitmentSystem(self.groups)
        vote = recruitment.vote(self.group_id, self.candidate, self.cats.cats)
        self.assertFalse(vote['accepted'])
        self.assertIn(self.second.name, vote['vetoes'])

    def test_defending_group_increases_future_influence(self):
        self.first.personality.setdefault('traits', {})['courage'] = 1.0
        hierarchy = CatGroupHierarchySystem(self.groups)
        before = {item['cat']: item['influence'] for item in hierarchy.rank(self.group_id, self.cats.cats)}[self.first.name]
        self.groups.respond_to_threat(self.group_id, self.cats.cats, threat={'name': 'cronenberg'})
        after = {item['cat']: item['influence'] for item in hierarchy.rank(self.group_id, self.cats.cats)}[self.first.name]
        self.assertGreater(after, before)
if __name__ == '__main__':
    unittest.main()
