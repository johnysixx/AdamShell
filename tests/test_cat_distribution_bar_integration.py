from core.entity.social_entity import SocialEntity
import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from cats.cats import Cats
from universe.bootstraps.universe_bootstrap import UniverseBootstrap

class CatDistributionBarIntegrationTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        bootstrap = UniverseBootstrap(UniverseRegistry(), self.universe)
        self.root_transition, self.layers, self.idea_universe = bootstrap.run()
        self.meeting_place = self.universe.meeting_place

    def test_cat_is_assigned_after_milk_but_stays_in_bar(self):
        cats = Cats(self.universe)
        cat = cats.create_cat(name='bar_cat', color='black', fur_length='short')
        cat.current_layer = 'meeting_place'
        cat.recipient = None
        recipient = SocialEntity.from_mapping({'id': 'alice', 'type': 'human', 'needs_cat': True})
        self.meeting_place.entities.append(cat)
        self.universe.cat_recipient_registry.register(recipient)
        event = self.meeting_place.serve_cat_milk(cat)
        self.assertTrue(event['served'])
        self.assertEqual(event['name'], 'cat_drank_milk_at_bar')
        self.assertIn('distribution', event)
        distribution = event['distribution']
        self.assertTrue(distribution['distributed'])
        self.assertEqual(distribution['status'], 'assigned')
        self.assertEqual(distribution['recipient'], 'alice')
        self.assertEqual(cat.recipient, 'alice')
        self.assertIn(cat, self.meeting_place.entities)
        self.assertNotIn(cat, self.idea_universe.entities)
        self.assertEqual(cat.current_layer, 'meeting_place')
        self.assertFalse(recipient.needs_cat)
if __name__ == '__main__':
    unittest.main()
