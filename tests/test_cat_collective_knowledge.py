import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_knowledge import CatKnowledge

class CatCollectiveKnowledgeTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(name='pazuzu', color='black', fur_length='short')

    def test_cat_remembers_discovered_place(self):
        place = CatKnowledge.remember_place(cat=self.cat, layer='quantum_layer', position={'x': 10.0, 'y': 2.0, 'z': -1.0}, safe=True, universe_tick=10)
        self.assertEqual(len(self.cat.knowledge['known_places']), 1)
        self.assertEqual(place['visit_count'], 1)
        self.assertEqual(place['safety'], 1.0)

    def test_second_visit_increases_confidence(self):
        first = CatKnowledge.remember_place(self.cat, 'quantum_layer', {'x': 10.0, 'y': 2.0, 'z': -1.0})
        second = CatKnowledge.remember_place(self.cat, 'quantum_layer', {'x': 10.0, 'y': 2.0, 'z': -1.0})
        self.assertEqual(second['visit_count'], 2)
        self.assertGreater(second['confidence'], first['confidence'])
        self.assertEqual(len(self.cat.knowledge['known_places']), 1)

    def test_cat_can_publish_legend(self):
        place = CatKnowledge.remember_place(self.cat, 'quantum_layer', {'x': 5.0, 'y': 0.0, 'z': 0.0})
        legend = CatKnowledge.publish_legend(universe=self.universe, cat=self.cat, place=place)
        self.assertEqual(legend.discoverer, 'pazuzu')
        self.assertEqual(len(self.universe.cat_legends), 1)

    def test_other_cat_confirms_existing_legend(self):
        first_place = CatKnowledge.remember_place(self.cat, 'quantum_layer', {'x': 5.0, 'y': 0.0, 'z': 0.0})
        CatKnowledge.publish_legend(self.universe, self.cat, first_place)
        other = self.cats.create_cat(name='garfield', color='orange', fur_length='short')
        second_place = CatKnowledge.remember_place(other, 'quantum_layer', {'x': 5.0, 'y': 0.0, 'z': 0.0})
        legend = CatKnowledge.publish_legend(self.universe, other, second_place)
        self.assertEqual(len(self.universe.cat_legends), 1)
        self.assertEqual(legend.verification_count, 2)
        self.assertIn('garfield', legend.reported_by)
if __name__ == '__main__':
    unittest.main()
