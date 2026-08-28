import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_knowledge import CatKnowledge
from cats.cat_exploration_planner import CatExplorationPlanner

class CatLegendTrustTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.storyteller = self.cats.create_cat(name='pazuzu', color='black', fur_length='short')
        self.listener = self.cats.create_cat(name='garfield', color='orange', fur_length='short')
        place = CatKnowledge.remember_place(self.storyteller, 'quantum_layer', {'x': 12.0, 'y': 3.0, 'z': 0.0})
        self.legend = CatKnowledge.publish_legend(self.universe, self.storyteller, place)

    def test_heard_legend_is_not_fact(self):
        heard = CatKnowledge.hear_legend(listener=self.listener, storyteller=self.storyteller, legend=self.legend)
        self.assertFalse(heard['verified'])
        self.assertEqual(len(self.listener.knowledge['known_places']), 0)
        self.assertEqual(len(self.listener.knowledge['heard_legends']), 1)

    def test_trust_changes_credibility(self):
        self.listener.relationships = {'pazuzu': {'trust': 1.0}}
        trusted = CatKnowledge.hear_legend(self.listener, self.storyteller, self.legend)
        other = self.cats.create_cat(name='skeptic', color='gray', fur_length='short')
        other['relationships'] = {'pazuzu': {'trust': 0.0}}
        skeptical = CatKnowledge.hear_legend(other, self.storyteller, self.legend)
        self.assertGreater(trusted['credibility'], skeptical['credibility'])

    def test_planner_can_use_credible_legend(self):
        self.listener.relationships = {'pazuzu': {'trust': 1.0}}
        CatKnowledge.hear_legend(self.listener, self.storyteller, self.legend)
        self.listener.current_layer = 'meeting_place'
        result = CatExplorationPlanner.choose_destination(cat=self.listener, universe=self.universe)
        heard = [candidate for candidate in result['candidates'] if candidate.get('source') == 'heard_legend']
        self.assertGreaterEqual(len(heard), 1)

    def test_personal_visit_verifies_legend(self):
        CatKnowledge.hear_legend(self.listener, self.storyteller, self.legend)
        place = CatKnowledge.remember_place(self.listener, 'quantum_layer', {'x': 12.0, 'y': 3.0, 'z': 0.0})
        verified = CatKnowledge.verify_heard_legend(self.listener, place)
        self.assertEqual(len(verified), 1)
        self.assertTrue(self.listener.knowledge['heard_legends'][0]['verified'])
if __name__ == '__main__':
    unittest.main()
