import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_knowledge import CatKnowledge
from cats.cat_perception import CatPerception

class CatQuantumBoxPairingPrincipleTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(name='observer', color='black', fur_length='short')
        self.cat.current_layer = 'quantum_layer'
        self.cat.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.box = self.universe.create_quantum_box()
        self.box.current_layer = 'quantum_layer'
        self.box.position = {'x': 3.0, 'y': 0.0, 'z': 0.0}

    def observe(self):
        return CatPerception(self.cats).observe(self.cat)

    def box_detail(self):
        observed = self.observe()
        return next((item for item in observed['visible_box_details'] if item['id'] == self.box.id))

    def explore_box(self):
        self.cat.mind.current_intention = {'type': 'explore_box', 'target': self.box.id, 'score': 1.0, 'reasons': ['test']}
        result = self.cats.execute_cat_intention(self.cat)
        for _ in range(10):
            if result['name'] == 'cat_explored_quantum_box':
                return result
            result = self.cats.execute_cat_intention(self.cat)
        return result

    def test_pairing_is_known_as_principle_not_as_route(self):
        knowledge = CatKnowledge.ensure_cat_knowledge(self.cat)
        self.assertTrue(knowledge['known_principles']['quantum_boxes_are_paired'])
        before = self.box_detail()
        self.assertFalse(before['explored'])
        self.assertNotIn('paired', before)
        result = self.explore_box()
        self.assertEqual(result['name'], 'cat_explored_quantum_box')
        after = self.box_detail()
        self.assertTrue(after['recognized_as_quantum_box'])
        self.assertTrue(after['paired'])
        self.assertFalse(after['counterpart_known'])
        self.assertNotIn('counterpart_box_id', after)
        self.assertNotIn('target_layer', after)
        self.assertNotIn('quantum_counterpart', after)

    def test_disappearing_box_leaves_memory_not_perception(self):
        result = self.explore_box()
        self.assertEqual(result['name'], 'cat_explored_quantum_box')
        memories = self.cat.memory.recall(event_type='quantum_box_observed')
        self.assertTrue(any((self.box.id in memory.get('participants', []) for memory in memories)))
        self.universe.quantum_boxes.remove(self.box)
        observed = self.observe()
        self.assertNotIn(self.box.id, observed['visible_boxes'])
        self.assertFalse(any((item.get('id') == self.box.id for item in observed['visible_box_details'])))
        memories_after = self.cat.memory.recall(event_type='quantum_box_observed')
        self.assertTrue(any((self.box.id in memory.get('participants', []) for memory in memories_after)))
        knowledge = CatKnowledge.ensure_cat_knowledge(self.cat)
        self.assertTrue(knowledge['known_principles']['quantum_boxes_are_paired'])
if __name__ == '__main__':
    unittest.main()
