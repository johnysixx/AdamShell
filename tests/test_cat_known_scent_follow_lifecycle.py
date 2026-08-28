import unittest
from universe.universe import Universe
from cats.cats import Cats

class CatKnownScentFollowLifecycleTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(name='tracker', color='black', fur_length='short')
        self.cat.current_layer = 'quantum_layer'
        self.cat.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.cat.mind['current_intention'] = {'type': 'follow_known_scent', 'target': {'identity': 'cat:pazuzu', 'layer': 'quantum_layer', 'position': {'x': 3.0, 'y': 0.0, 'z': 0.0}, 'source_id': 'trace_latest', 'trail_direction': {'inferred': True, 'unit_vector': {'x': 1.0, 'y': 0.0, 'z': 0.0}, 'confidence': 0.8}}, 'score': 1.0, 'reasons': ['test']}

    def test_cat_reaches_last_known_scent_point(self):
        first = self.cats.execute_cat_intention(self.cat)
        self.assertEqual(first['name'], 'cat_following_known_scent')
        self.assertIsNotNone(self.cat.mind['current_intention'])
        result = first
        for _ in range(10):
            result = self.cats.execute_cat_intention(self.cat)
            if result['name'] == 'cat_reached_known_scent':
                break
        self.assertEqual(result['name'], 'cat_reached_known_scent')
        self.assertEqual(self.cat.position, {'x': 3.0, 'y': 0.0, 'z': 0.0})
        self.assertTrue(self.cat.known_scent_follow['arrived'])
        self.assertFalse(self.cat.known_scent_follow['active'])
        self.assertIsNone(self.cat.mind['current_intention'])
        self.assertTrue(self.cat.known_scent_follow['trail_direction']['inferred'])
if __name__ == '__main__':
    unittest.main()
