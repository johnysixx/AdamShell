import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind
from cats.cat_knowledge import CatKnowledge

class CatCronenbergScentBehaviorTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(name='scent_cat', color='black', fur_length='short')

    def observations(self):
        return {'bar_known': True, 'bar_visible': False, 'visible_cronenbergs': [], 'huntable_cronenbergs': [], 'cronenberg_danger': 0.0, 'unexplored_boxes': [], 'can_create_exploration_pair': False, 'nearby_cats': [], 'shareable_legend_count': 0, 'cronenberg_scent_recognized': True, 'smelled_cronenbergs': [{'entity_id': 'cronenberg_test', 'recognition': {'recognized': True, 'identity': 'cronenberg'}}]}

    def test_brave_cat_tracks_cronenberg_scent(self):
        traits = self.cat.personality['traits']
        traits['courage'] = 1.0
        traits['aggression'] = 1.0
        traits['curiosity'] = 1.0
        traits['patience'] = 0.0
        result = CatMind.decide(cat=self.cat, observations=self.observations())
        self.assertEqual(result['intention'], 'track_cronenberg_scent')

    def test_cautious_cat_avoids_cronenberg_scent(self):
        traits = self.cat.personality['traits']
        traits['courage'] = 0.0
        traits['aggression'] = 0.0
        traits['curiosity'] = 0.0
        traits['patience'] = 1.0
        result = CatMind.decide(cat=self.cat, observations=self.observations())
        self.assertEqual(result['intention'], 'avoid_cronenberg_scent')

    def test_unknown_ozone_does_not_mean_cronenberg(self):
        observations = self.observations()
        observations['cronenberg_scent_recognized'] = False
        observations['smelled_cronenbergs'] = []
        observations['ozone_detected'] = True
        candidates = CatMind.consider(cat=self.cat, observations=observations)
        intentions = {candidate['type'] for candidate in candidates}
        self.assertNotIn('track_cronenberg_scent', intentions)
        self.assertNotIn('avoid_cronenberg_scent', intentions)
if __name__ == '__main__':
    unittest.main()
