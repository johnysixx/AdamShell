import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind
from cats.cat_perception import CatPerception

class CatQuantumCounterpartSensingTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(name='observer', color='black', fur_length='short')
        self.cat.current_layer = 'quantum_layer'
        self.source = self.universe.create_quantum_box()
        self.target = self.universe.create_quantum_box()
        self.source.current_layer = 'quantum_layer'
        self.target.current_layer = 'meeting_place'
        self.source.position = {'x': 2.0, 'y': 0.0, 'z': 0.0}
        self.target.position = {'x': 9.0, 'y': 4.0, 'z': 0.0}
        self.source.pair_with(self.target)
        self.cat.position = {'x': 2.0, 'y': 0.0, 'z': 0.0}
        self.cat.memory.remember(event_type='quantum_box_observed', universe_tick=0, location='quantum_layer', participants=[self.source.id], details={'box_id': self.source.id})

    def observations(self):
        return CatPerception(self.cats).observe(self.cat)

    def test_cat_can_choose_to_sense_counterpart(self):
        observations = self.observations()
        candidates = CatMind.consider(cat=self.cat, observations=observations)
        resonance = [candidate for candidate in candidates if candidate['type'] == 'sense_quantum_counterpart']
        self.assertEqual(len(resonance), 1)
        self.assertEqual(resonance[0]['target']['box_id'], self.source.id)

    def test_sensing_reveals_current_counterpart_location(self):
        candidates = CatMind.consider(cat=self.cat, observations=self.observations())
        intention = next((candidate for candidate in candidates if candidate['type'] == 'sense_quantum_counterpart'))
        self.cat.mind.current_intention = intention
        result = self.cats.execute_cat_intention(self.cat)
        self.assertEqual(result['name'], 'cat_sensed_quantum_counterpart')
        observation = result['observation']
        self.assertEqual(observation['counterpart_box_id'], self.target.id)
        self.assertEqual(observation['counterpart_layer'], 'meeting_place')
        self.assertEqual(observation['counterpart_position'], self.target.position)
        self.assertTrue(observation['temporary'])
        self.assertTrue(observation['pair_currently_valid'])

    def test_counterpart_observation_disappears_with_pair(self):
        candidates = CatMind.consider(cat=self.cat, observations=self.observations())
        intention = next((candidate for candidate in candidates if candidate['type'] == 'sense_quantum_counterpart'))
        self.cat.mind.current_intention = intention
        result = self.cats.execute_cat_intention(self.cat)
        self.assertTrue(result['observation']['pair_currently_valid'])
        before = self.observations()
        self.assertIsNotNone(before['quantum_counterpart_observation'])
        self.universe.quantum_boxes.remove(self.target)
        after = self.observations()
        self.assertIsNone(after['quantum_counterpart_observation'])
        self.assertFalse(hasattr(self.cat, 'current_quantum_counterpart_observation'))

    def test_previous_quantum_travel_increases_sensing_score(self):
        inexperienced_candidates = CatMind.consider(cat=self.cat, observations=self.observations())
        inexperienced = next((candidate for candidate in inexperienced_candidates if candidate['type'] == 'sense_quantum_counterpart'))
        self.cat.memory.remember(event_type='quantum_box_layer_transfer', universe_tick=0, location={'x': 9.0, 'y': 4.0, 'z': 0.0}, participants=['old_source_box', 'old_target_box'], details={'source_layer': 'old_quantum_layer', 'target_layer': 'old_meeting_place', 'target_box_consumed': True, 'energy_j': 1.0, 'trail_id': 'old_quantum_trail'})
        experienced_candidates = CatMind.consider(cat=self.cat, observations=self.observations())
        experienced = next((candidate for candidate in experienced_candidates if candidate['type'] == 'sense_quantum_counterpart'))
        self.assertGreater(experienced['score'], inexperienced['score'])
        self.assertIn('experienced_quantum_traveler', experienced['reasons'])

    def test_quantum_travel_experience_bonus_scales_with_history(self):

        def sense_score():
            candidates = CatMind.consider(cat=self.cat, observations=self.observations())
            return next((candidate['score'] for candidate in candidates if candidate['type'] == 'sense_quantum_counterpart'))
        base_score = sense_score()
        self.cat.memory.remember(event_type='quantum_box_layer_transfer', universe_tick=1, location={'x': 1.0, 'y': 1.0, 'z': 0.0}, participants=['source_1', 'target_1'], details={'source_layer': 'quantum_layer', 'target_layer': 'meeting_place', 'target_box_consumed': True})
        one_transfer_score = sense_score()
        self.cat.memory.remember(event_type='quantum_box_layer_transfer', universe_tick=2, location={'x': 2.0, 'y': 2.0, 'z': 0.0}, participants=['source_2', 'target_2'], details={'source_layer': 'quantum_layer', 'target_layer': 'meeting_place', 'target_box_consumed': True})
        self.cat.memory.remember(event_type='quantum_box_layer_transfer', universe_tick=3, location={'x': 3.0, 'y': 3.0, 'z': 0.0}, participants=['source_3', 'target_3'], details={'source_layer': 'quantum_layer', 'target_layer': 'meeting_place', 'target_box_consumed': True})
        three_transfer_score = sense_score()
        self.assertGreater(one_transfer_score, base_score)
        self.assertGreater(three_transfer_score, one_transfer_score)
        self.assertAlmostEqual(three_transfer_score - base_score, 0.2, places=7)

    def test_failed_quantum_travel_reduces_travel_score(self):
        candidates = CatMind.consider(cat=self.cat, observations=self.observations())
        sense = next((candidate for candidate in candidates if candidate['type'] == 'sense_quantum_counterpart'))
        self.cat.mind.current_intention = sense
        result = self.cats.execute_cat_intention(self.cat)
        self.assertTrue(result['executed'])
        before_candidates = CatMind.consider(cat=self.cat, observations=self.observations())
        before = next((candidate for candidate in before_candidates if candidate['type'] == 'travel_through_known_quantum_box'))
        self.cat.memory.remember(event_type='quantum_box_layer_transfer_failed', universe_tick=1, location=dict(self.cat.position), participants=[self.source.id, self.target.id], details={'source_layer': 'quantum_layer', 'target_layer': 'meeting_place', 'reason': 'test_quantum_failure', 'cronenberg_id': 'test_cronenberg'})
        after_candidates = CatMind.consider(cat=self.cat, observations=self.observations())
        after = next((candidate for candidate in after_candidates if candidate['type'] == 'travel_through_known_quantum_box'))
        self.assertLess(after['score'], before['score'])
        self.assertIn('negative_quantum_travel_memory', after['reasons'])
if __name__ == '__main__':
    unittest.main()
