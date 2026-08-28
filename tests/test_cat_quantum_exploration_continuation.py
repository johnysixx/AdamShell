import unittest
from universe.universe import Universe
from cats.cats import Cats
from universe.dark_sector import QUANTUM_BOX_ENERGY_COST_J

class CatQuantumExplorationContinuationTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(name='curious_explorer', color='black', fur_length='short')
        self.cat.current_layer = 'meeting_place'
        self.cat.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.cat.idea_energy = QUANTUM_BOX_ENERGY_COST_J * 10.0
        self.cat.exploration_goal = {'layer': 'quantum_layer', 'position': {'x': 4.0, 'y': 0.0, 'z': 0.0}}
        traits = self.cat.personality['traits']
        traits['curiosity'] = 1.0
        traits['courage'] = 1.0
        traits['patience'] = 0.0

    def reach_first_goal(self):
        self.cats.think_and_act(cat=self.cat)
        for _ in range(100):
            result = self.cats.advance_cat_quantum_exploration(self.cat)
            if result.get('arrived', False):
                return result
        self.fail('Kočka nedorazila k prvnímu cíli.')

    def test_continue_exploration_starts_new_route(self):
        result = self.reach_first_goal()
        resolution = result['arrival_resolution']
        self.assertEqual(resolution['action'], 'continue_exploration')
        continuation = resolution['continuation_plan']
        self.assertTrue(continuation['continued'])
        self.assertTrue(self.cat.quantum_exploration['active'])
        self.assertEqual(self.cat.quantum_exploration['stage'], 2)

    def test_continuation_does_not_create_new_pair(self):
        self.assertEqual(len(self.universe.stable_cat_box_pairs), 0)
        self.reach_first_goal()
        self.assertEqual(len(self.universe.stable_cat_box_pairs), 1)
        active_pairs = [pair for pair in self.universe.stable_cat_box_pairs if pair.get('active', False)]
        self.assertEqual(len(active_pairs), 1)

    def test_return_anchor_survives_continuation(self):
        self.reach_first_goal()
        pair = next((pair for pair in self.universe.stable_cat_box_pairs if pair.get('active', False)))
        self.assertIn(pair['anchor_box_id'], [box.id for box in self.universe.quantum_boxes])
        self.assertIn(pair['remote_box_id'], [box.id for box in self.universe.quantum_boxes])

    def test_second_goal_is_different(self):
        first_goal = dict(self.cat.exploration_goal['position'])
        self.reach_first_goal()
        second_goal = dict(self.cat.quantum_exploration['destination'])
        self.assertNotEqual(first_goal, second_goal)
if __name__ == '__main__':
    unittest.main()
