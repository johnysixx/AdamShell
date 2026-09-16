import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import CatGroupSystem
from cats.cat_group_role_system import CatGroupRoleSystem
from cats.cat_group_institution_system import CatGroupInstitutionSystem
from cats.cat_group_norm_system import CatGroupNormSystem
from cats.cat_group_taboo_system import CatGroupTabooSystem
from cats.cat_group_sanction_system import CatGroupSanctionSystem
from cats.cat_culture_objects import CatViolation
from cats.cat_social_objects import CatRelationship
from cats.cat_group_norm_institution_system import CatGroupNormInstitutionSystem

class CatGroupNormTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.first = self.cats.create_cat(name='first', color='black', fur_length='short')
        self.second = self.cats.create_cat(name='second', color='white', fur_length='short')
        self.groups = CatGroupSystem(self.cats)
        self.group_id = self.groups.create_group(self.first, name='bar_cats')['group_id']
        self.groups.add_member(self.group_id, self.second, self.cats.cats)

    def test_group_can_define_norm(self):
        norms = CatGroupNormSystem(self.groups)
        result = norms.define(self.group_id, 'protect_kittens', 'protective', {'action': 'protect', 'target': 'kitten'}, importance=0.9)
        self.assertTrue(result['defined'])
        self.assertIn(result['norm_id'], self.groups.groups[self.group_id].norms)

    def test_cat_can_violate_norm(self):
        norms = CatGroupNormSystem(self.groups)
        created = norms.define(self.group_id, 'do_not_disturb_sleep', 'social', {'action': 'avoid_disturbing_sleep'}, importance=0.5)
        result = norms.violate(self.group_id, self.second, created['norm_id'])
        self.assertTrue(result.violated)
        self.assertEqual(len(self.second.norms.violations), 1)

    def test_group_can_define_taboo(self):
        taboo = CatGroupTabooSystem(self.groups)
        result = taboo.define(self.group_id, 'do_not_open_black_box', taboo_type='place_action', target={'place': 'black_box', 'action': 'open'}, severity=1.0)
        self.assertTrue(result['defined'])

    def test_taboo_violation_can_recommend_expulsion(self):
        taboo = CatGroupTabooSystem(self.groups)
        created = taboo.define(self.group_id, 'do_not_open_black_box', taboo_type='place_action', target={'place': 'black_box', 'action': 'open'}, severity=1.0)
        violation = taboo.violate(self.group_id, self.second, created['taboo_id'])
        sanctions = CatGroupSanctionSystem(self.groups)
        result = sanctions.sanction(self.group_id, self.second, violation)
        self.assertEqual(result['sanction'], 'expulsion_recommended')
        self.assertEqual(self.second.state, 'group_expulsion_recommended')

    def test_repeated_minor_violations_escalate(self):
        norms = CatGroupNormSystem(self.groups)
        created = norms.define(self.group_id, 'quiet_sleeping_area', 'social', {'action': 'stay_quiet'}, importance=0.2)
        sanctions = CatGroupSanctionSystem(self.groups)
        last = None
        for _ in range(5):
            violation = norms.violate(self.group_id, self.second, created['norm_id'])
            last = sanctions.sanction(self.group_id, self.second, violation)
        self.assertNotEqual(last['sanction'], 'warning')

    def test_norm_can_belong_to_institution(self):
        institutions = CatGroupInstitutionSystem(self.groups)
        institutions.establish(self.group_id, 'kitten_guard', 'protect_kittens', roles=[], rituals=[])
        norms = CatGroupNormSystem(self.groups)
        created = norms.define(self.group_id, 'protect_kittens', 'protective', {'target': 'kitten'}, importance=0.9)
        linking = CatGroupNormInstitutionSystem(self.groups)
        result = linking.attach_norm(self.group_id, 'kitten_guard', created['norm_id'])
        self.assertTrue(result['linked'])
        self.assertIn(created['norm_id'], self.groups.groups[self.group_id].institutions['kitten_guard'].norms)

    def test_social_avoidance_creates_relationship_object(self):
        self.second.relationships.pop(self.first.name, None)
        sanctions = CatGroupSanctionSystem(self.groups)

        result = sanctions.sanction(
            self.group_id, self.second, CatViolation(severity=0.3)
        )

        relation = self.second.relationships[self.first.name]
        self.assertEqual(result['sanction'], 'social_avoidance')
        self.assertIsInstance(relation, CatRelationship)
        self.assertEqual(relation.affiliation, 0.0)
        self.assertEqual(relation.trust, 0.5)
        self.assertNotIn(self.second.name, self.second.relationships)

    def test_trust_loss_creates_relationship_object(self):
        self.second.relationships.pop(self.first.name, None)
        sanctions = CatGroupSanctionSystem(self.groups)

        result = sanctions.sanction(
            self.group_id, self.second, CatViolation(severity=0.6)
        )

        relation = self.second.relationships[self.first.name]
        self.assertEqual(result['sanction'], 'trust_loss')
        self.assertIsInstance(relation, CatRelationship)
        self.assertAlmostEqual(relation.trust, 0.26)
        self.assertEqual(relation.affiliation, 0.0)
        self.assertAlmostEqual(self.second.norms.trust_penalties, 0.24)
        self.assertNotIn(self.second.name, self.second.relationships)

    def test_sanctions_preserve_existing_relationship_records(self):
        sanctions = CatGroupSanctionSystem(self.groups)
        for cat, other, relation in (
            (self.first, self.second, CatRelationship.create()),
            (self.second, self.first, {}),
        ):
            history = [{'kind': 'shared_rest'}]
            relation.update({
                'affiliation': 0.4,
                'trust': 0.8,
                'trust_history': history,
                'meet_count': 3,
            })
            cat.relationships[other.name] = relation

            avoidance = sanctions.sanction(
                self.group_id, cat, CatViolation(severity=0.3)
            )
            self.assertEqual(avoidance['sanction'], 'social_avoidance')
            self.assertAlmostEqual(relation['affiliation'], 0.35)
            self.assertEqual(relation['trust'], 0.8)

            loss = sanctions.sanction(
                self.group_id, cat, CatViolation(severity=0.5)
            )

            self.assertEqual(loss['sanction'], 'trust_loss')
            self.assertAlmostEqual(loss['severity'], 0.58)
            self.assertIs(cat.relationships[other.name], relation)
            self.assertAlmostEqual(relation['trust'], 0.563)
            self.assertAlmostEqual(relation['affiliation'], 0.35)
            self.assertAlmostEqual(cat.norms.trust_penalties, 0.237)
            self.assertIs(relation['trust_history'], history)
            self.assertEqual(history, [{'kind': 'shared_rest'}])
            self.assertEqual(relation['meet_count'], 3)


if __name__ == '__main__':
    unittest.main()
