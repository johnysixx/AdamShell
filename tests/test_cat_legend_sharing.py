import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_knowledge import CatKnowledge

class CatLegendSharingTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.storyteller = self.cats.create_cat(name='pazuzu', color='black', fur_length='short')
        self.listener = self.cats.create_cat(name='garfield', color='orange', fur_length='short')
        self.storyteller.relationships = {'garfield': {'trust': 1.0}}
        place = CatKnowledge.remember_place(self.storyteller, 'quantum_layer', {'x': 7.0, 'y': 2.0, 'z': 0.0})
        self.legend = CatKnowledge.publish_legend(self.universe, self.storyteller, place)

    def test_cat_can_choose_legend_for_listener(self):
        result = CatKnowledge.choose_legend_to_share(storyteller=self.storyteller, listener=self.listener, universe=self.universe)
        self.assertTrue(result['selected'])
        self.assertEqual(result['legend'].legend_id, self.legend.legend_id)

    def test_trusted_cat_shares_valuable_legend(self):
        result = CatKnowledge.share_legend(storyteller=self.storyteller, listener=self.listener, universe=self.universe)
        self.assertTrue(result['shared'])
        self.assertEqual(len(self.listener.knowledge['heard_legends']), 1)

    def test_same_story_is_not_repeated_forever(self):
        first = CatKnowledge.share_legend(self.storyteller, self.listener, self.universe)
        second = CatKnowledge.share_legend(self.storyteller, self.listener, self.universe)
        self.assertTrue(first['shared'])
        self.assertFalse(second['shared'])
        self.assertEqual(second['reason'], 'no_shareable_legend')

    def test_low_relationship_can_prevent_sharing(self):
        stranger = self.cats.create_cat(name='stranger', color='gray', fur_length='short')
        self.storyteller.relationships['stranger'] = {'trust': 0.0}
        self.storyteller.personality['traits']['curiosity'] = 0.0
        self.storyteller.personality['traits']['patience'] = 0.0
        result = CatKnowledge.share_legend(self.storyteller, stranger, self.universe)
        self.assertFalse(result['shared'])
if __name__ == '__main__':
    unittest.main()
