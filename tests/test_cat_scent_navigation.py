import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_knowledge import CatKnowledge
from cats.cat_mind import CatMind

class CatScentNavigationTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(name='tracker', color='black', fur_length='short')
        self.cat.current_layer = 'quantum_layer'
        self.cat.position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        CatKnowledge.remember_scent_place(cat=self.cat, layer='quantum_layer', position={'x': 5.0, 'y': 0.0, 'z': 0.0}, source_id='box_pazuzu', recognized_identity='cat:pazuzu', components={'cat': 1.0, 'fur': 0.8}, perceived_intensity=0.8, universe_tick=10)

    def observations(self):
        return {'bar_known': True, 'bar_visible': False, 'visible_cronenbergs': [], 'huntable_cronenbergs': [], 'cronenberg_danger': 0.0, 'unexplored_boxes': [], 'can_create_exploration_pair': False, 'nearby_cats': [], 'shareable_legend_count': 0, 'cronenberg_scent_recognized': False}

    def test_cat_mind_can_choose_known_scent(self):
        traits = self.cat.personality['traits']
        traits['curiosity'] = 1.0
        traits['courage'] = 0.8
        candidates = CatMind.consider(cat=self.cat, observations=self.observations())
        scent = [candidate for candidate in candidates if candidate['type'] == 'follow_known_scent']
        self.assertEqual(len(scent), 1)
        self.assertEqual(scent[0]['target']['identity'], 'cat:pazuzu')

    def test_planner_remembers_strongest_scent_place(self):
        from cats.cat_exploration_planner import CatExplorationPlanner
        result = CatExplorationPlanner.choose_scent_destination(cat=self.cat, preferred_identity='cat:pazuzu')
        self.assertTrue(result['selected'])
        self.assertEqual(result['position'], {'x': 5.0, 'y': 0.0, 'z': 0.0})

    def test_known_scent_navigation_prefers_current_layer(self):
        from cats.cat_knowledge import CatKnowledge
        CatKnowledge.remember_scent_place(cat=self.cat, layer='meeting_place', position={'x': 99.0, 'y': 0.0, 'z': 0.0}, source_id='old_pazuzu_trace', recognized_identity='cat:pazuzu', components={'cat': 1.0, 'individual_cat:pazuzu': 2.0}, perceived_intensity=1.0, universe_tick=1)
        old_memory = next((memory for memory in self.cat.knowledge['known_scent_places'] if memory['source_id'] == 'old_pazuzu_trace'))
        old_memory['confidence'] = 1.0
        CatKnowledge.remember_scent_place(cat=self.cat, layer='quantum_layer', position={'x': 7.0, 'y': 0.0, 'z': 0.0}, source_id='local_pazuzu_trace', recognized_identity='cat:pazuzu', components={'cat': 0.4, 'individual_cat:pazuzu': 0.8}, perceived_intensity=0.3, universe_tick=2)
        candidates = CatMind.consider(cat=self.cat, observations=self.observations())
        scent = next((candidate for candidate in candidates if candidate['type'] == 'follow_known_scent'))
        self.assertEqual(scent['target']['layer'], 'quantum_layer')
        self.assertNotEqual(scent['target']['source_id'], 'old_pazuzu_trace')
        self.assertEqual(scent['target']['layer'], 'quantum_layer')

    def test_fresh_scent_beats_old_stronger_memory(self):
        from cats.cat_knowledge import CatKnowledge
        self.cat.knowledge['known_scent_places'] = []
        CatKnowledge.remember_scent_place(cat=self.cat, layer='quantum_layer', position={'x': 2.0, 'y': 0.0, 'z': 0.0}, source_id='old_strong_trace', recognized_identity='cat:pazuzu', components={}, perceived_intensity=1.0, universe_tick=0)
        CatKnowledge.remember_scent_place(cat=self.cat, layer='quantum_layer', position={'x': 8.0, 'y': 0.0, 'z': 0.0}, source_id='fresh_trace', recognized_identity='cat:pazuzu', components={}, perceived_intensity=0.4, universe_tick=195)
        self.cat.knowledge['scent_clock_tick'] = 200
        candidates = CatMind.consider(cat=self.cat, observations=self.observations())
        scent = next((candidate for candidate in candidates if candidate['type'] == 'follow_known_scent'))
        self.assertEqual(scent['target']['source_id'], 'fresh_trace')
        self.assertEqual(scent['target']['age_ticks'], 5)
        self.assertGreater(scent['target']['freshness'], 0.9)

    def test_ancient_scent_remains_memory_but_not_navigation_target(self):
        from cats.cat_knowledge import CatKnowledge
        self.cat.knowledge['known_scent_places'] = []
        CatKnowledge.remember_scent_place(cat=self.cat, layer='quantum_layer', position={'x': 5.0, 'y': 0.0, 'z': 0.0}, source_id='ancient_trace', recognized_identity='cat:pazuzu', components={}, perceived_intensity=1.0, universe_tick=0)
        self.cat.knowledge['scent_clock_tick'] = 300
        candidates = CatMind.consider(cat=self.cat, observations=self.observations())
        scent_candidates = [candidate for candidate in candidates if candidate['type'] == 'follow_known_scent']
        self.assertEqual(scent_candidates, [])
        memories = self.cat.knowledge['known_scent_places']
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0]['source_id'], 'ancient_trace')

    def test_cat_infers_direction_from_scent_points(self):
        from cats.cat_knowledge import CatKnowledge
        self.cat.knowledge['known_scent_places'] = []
        CatKnowledge.remember_scent_place(cat=self.cat, layer='quantum_layer', position={'x': 1.0, 'y': 0.0, 'z': 0.0}, source_id='trace_a', recognized_identity='cat:pazuzu', components={}, perceived_intensity=0.4, universe_tick=10)
        CatKnowledge.remember_scent_place(cat=self.cat, layer='quantum_layer', position={'x': 4.0, 'y': 0.0, 'z': 0.0}, source_id='trace_b', recognized_identity='cat:pazuzu', components={}, perceived_intensity=0.6, universe_tick=20)
        self.cat.knowledge['scent_clock_tick'] = 20
        result = CatKnowledge.infer_scent_direction(cat=self.cat, identity='cat:pazuzu', layer='quantum_layer')
        self.assertTrue(result['inferred'])
        self.assertEqual(result['from_source_id'], 'trace_a')
        self.assertEqual(result['to_source_id'], 'trace_b')
        self.assertEqual(result['vector'], {'x': 3.0, 'y': 0.0, 'z': 0.0})
        self.assertEqual(result['unit_vector'], {'x': 1.0, 'y': 0.0, 'z': 0.0})
        self.assertEqual(result['tick_delta'], 10)

    def test_follow_known_scent_contains_inferred_direction(self):
        from cats.cat_knowledge import CatKnowledge
        self.cat.knowledge['known_scent_places'] = []
        CatKnowledge.remember_scent_place(cat=self.cat, layer='quantum_layer', position={'x': 1.0, 'y': 1.0, 'z': 0.0}, source_id='trace_1', recognized_identity='cat:pazuzu', components={}, perceived_intensity=0.4, universe_tick=10)
        CatKnowledge.remember_scent_place(cat=self.cat, layer='quantum_layer', position={'x': 2.0, 'y': 2.0, 'z': 0.0}, source_id='trace_2', recognized_identity='cat:pazuzu', components={}, perceived_intensity=0.8, universe_tick=20)
        self.cat.knowledge['scent_clock_tick'] = 20
        candidates = CatMind.consider(cat=self.cat, observations=self.observations())
        scent = next((candidate for candidate in candidates if candidate['type'] == 'follow_known_scent'))
        direction = scent['target']['trail_direction']
        self.assertTrue(direction['inferred'])
        self.assertEqual(direction['to_source_id'], 'trace_2')
        self.assertGreater(direction['confidence'], 0.0)
if __name__ == '__main__':
    unittest.main()
