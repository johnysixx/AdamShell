import unittest
from universe.universe import Universe
from cats.cats import Cats
from universe.dark_sector import QUANTUM_BOX_ENERGY_COST_J

class CatAutonomousExplorationPairTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(name='explorer', color='black', fur_length='short')
        self.cat.current_layer = 'meeting_place'
        self.cat.position = {'x': 3.0, 'y': 1.0, 'z': 0.0}
        self.cat.idea_energy = QUANTUM_BOX_ENERGY_COST_J * 10.0
        self.cat.personality['traits']['curiosity'] = 1.0

    def test_perception_offers_pair_creation_without_box(self):
        observations = self.cats.observe_cat(self.cat)
        self.assertEqual(observations['unexplored_boxes'], [])
        self.assertTrue(observations['can_create_exploration_pair'])
        self.assertEqual(observations['exploration_destination_layer'], 'quantum_layer')

    def test_cat_mind_selects_pair_creation(self):
        observations = self.cats.observe_cat(self.cat)
        from cats.cat_mind import CatMind
        decision = CatMind.decide(cat=self.cat, observations=observations)
        self.assertEqual(decision['intention'], 'create_exploration_pair')

    def test_think_and_act_creates_and_uses_stable_pair(self):
        before_boxes = len(self.universe.quantum_boxes)
        before_energy = self.cat.idea_energy
        result = self.cats.think_and_act(cat=self.cat)
        self.assertTrue(result['completed'])
        self.assertEqual(result['decision']['intention'], 'create_exploration_pair')
        execution = result['execution']
        self.assertTrue(execution['executed'])
        self.assertEqual(execution['name'], 'cat_started_autonomous_exploration_through_new_pair')
        self.assertEqual(len(self.universe.quantum_boxes), before_boxes + 2)
        self.assertEqual(len(self.universe.stable_cat_box_pairs), 1)
        self.assertLess(self.cat.idea_energy, before_energy)
        self.assertEqual(self.cat.current_layer, 'quantum_layer')
        self.assertEqual(self.cat.state, 'materialized_through_stable_exploration_pair')
        self.assertTrue(execution['transfer']['transferred'])
        self.assertTrue(execution['transfer']['pair_remains_stable'])
        self.assertFalse(execution['transfer']['target_box_consumed'])
        self.assertIsNone(self.cat.mind['current_intention'])

    def test_existing_unexplored_box_is_preferred(self):
        box = self.universe.create_quantum_box(layer='meeting_place')
        box.position = {'x': 3.5, 'y': 1.0, 'z': 0.0}
        observations = self.cats.observe_cat(self.cat)
        self.assertFalse(observations['can_create_exploration_pair'])
        from cats.cat_mind import CatMind
        decision = CatMind.decide(cat=self.cat, observations=observations)
        self.assertEqual(decision['intention'], 'explore_box')
if __name__ == '__main__':
    unittest.main()
