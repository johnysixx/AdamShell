import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import CatGroupSystem

class CatsAutonomousTickTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)

    def test_unpositioned_cat_is_skipped_without_error(self):
        cat = self.cats.create_cat(name='cat', color='black', fur_length='short')
        report = self.cats.tick()
        self.assertTrue(report['ok'])
        self.assertEqual(report['cats'][0]['result']['reason'], 'no_position')
        self.assertEqual(cat.mind.decision_count, 0)

    def test_positioned_cat_runs_thought_cycle(self):
        cat = self.cats.create_cat(name='cat', color='black', fur_length='short')
        cat.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        report = self.cats.tick()
        self.assertTrue(report['ok'])
        self.assertGreaterEqual(cat.mind.decision_count, 1)
        result = report['cats'][0]['result']
        self.assertEqual(result['mode'], 'thought_cycle')

    def test_one_broken_cat_does_not_stop_other_cats(self):
        broken = self.cats.create_cat(name='broken', color='black', fur_length='short')
        healthy = self.cats.create_cat(name='healthy', color='white', fur_length='short')
        broken.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        healthy.position = {'x': 1.0, 'y': 0.0, 'z': 0.0}
        original = self.cats._tick_cat_autonomously

        def sometimes_broken(cat):
            if cat is broken:
                raise RuntimeError('broken cat')
            return original(cat)
        self.cats._tick_cat_autonomously = sometimes_broken
        report = self.cats.tick()
        self.assertFalse(report['ok'])
        self.assertEqual(report['error_count'], 1)
        self.assertEqual(self.universe.cronenberg_count, 1)
        self.assertGreaterEqual(healthy.mind.decision_count, 1)

    def test_registered_group_advances_with_cats_tick(self):
        founder = self.cats.create_cat(name='founder', color='black', fur_length='short')
        member = self.cats.create_cat(name='member', color='white', fur_length='short')
        groups = CatGroupSystem(self.cats)
        created = groups.create_group(founder, name='group')
        group_id = created['group_id']
        groups.add_member(group_id, member, self.cats.cats)
        before = groups.groups[group_id].age_ticks
        report = self.cats.tick()
        after = groups.groups[group_id].age_ticks
        self.assertEqual(after, before + 1)
        self.assertEqual(len(report['groups']), 1)
if __name__ == '__main__':
    unittest.main()
