from core.entity.social_entity import SocialEntity
import unittest
from cats.cat_distribution_system import CatDistributionSystem
from cats.cats import Cats
from universe.universe import Universe
from universe.cat_recipient_registry import CatRecipientRegistry

class CatDistributionSystemTests(unittest.TestCase):

    def make_cat(self, name, recipient=None):
        universe = Universe()
        cats = Cats(universe)
        cat = cats.create_cat(name=name, color='black', fur_length='short')
        cat.current_layer = 'meeting_place'
        cat.recipient = recipient
        return cat

    def test_unowned_cat_gets_fallback_suggestion_without_travel(self):
        cat = self.make_cat(name='traveler')
        meeting_entities = [cat]
        idea_entities = []
        system = CatDistributionSystem(meeting_entities=meeting_entities, idea_entities=idea_entities)
        result = system.handle_after_milk(cat)
        self.assertFalse(result['distributed'])
        self.assertEqual(result['status'], 'unassigned')
        self.assertEqual(result['suggested_layer'], 'idea_universe')
        self.assertIn(cat, meeting_entities)
        self.assertNotIn(cat, idea_entities)
        self.assertEqual(cat.current_layer, 'meeting_place')
        self.assertEqual(cat.distribution['suggested_layer'], 'idea_universe')

    def test_assigned_cat_is_not_distributed(self):
        cat = self.make_cat(name='house_cat', recipient='alice')
        meeting_entities = [cat]
        idea_entities = []
        system = CatDistributionSystem(meeting_entities=meeting_entities, idea_entities=idea_entities)
        result = system.handle_after_milk(cat)
        self.assertFalse(result['distributed'])
        self.assertEqual(result['reason'], 'cat_already_has_recipient')
        self.assertIn(cat, meeting_entities)
        self.assertNotIn(cat, idea_entities)

    def test_unowned_cat_is_assigned_to_waiting_recipient(self):
        cat = self.make_cat(name='traveler')
        meeting_entities = [cat]
        idea_entities = []
        recipient_registry = CatRecipientRegistry()
        recipient = SocialEntity.from_mapping({'id': 'alice', 'type': 'human', 'needs_cat': True})
        recipient_registry.register(recipient)
        system = CatDistributionSystem(meeting_entities=meeting_entities, idea_entities=idea_entities, recipient_registry=recipient_registry)
        result = system.handle_after_milk(cat)
        self.assertTrue(result['distributed'])
        self.assertEqual(result['status'], 'assigned')
        self.assertEqual(result['recipient'], 'alice')
        self.assertEqual(cat.recipient, 'alice')
        self.assertEqual(cat.distribution['status'], 'assigned')
        self.assertEqual(cat.distribution['recipient'], 'alice')
        self.assertIn(cat, meeting_entities)
        self.assertEqual(cat.current_layer, 'meeting_place')
        self.assertFalse(recipient['needs_cat'])

    def test_first_waiting_recipient_gets_cat(self):
        cat = self.make_cat(name='traveler')
        first = SocialEntity.from_mapping({'id': 'alice', 'type': 'human', 'needs_cat': True})
        second = SocialEntity.from_mapping({'id': 'wizard', 'type': 'idea_entity', 'needs_cat': True})
        recipient_registry = CatRecipientRegistry()
        recipient_registry.register(first)
        recipient_registry.register(second)
        system = CatDistributionSystem(meeting_entities=[cat], idea_entities=[], recipient_registry=recipient_registry)
        result = system.handle_after_milk(cat)
        self.assertEqual(result['recipient'], 'alice')
        self.assertEqual(cat.recipient, 'alice')
        self.assertFalse(first['needs_cat'])
        self.assertTrue(second['needs_cat'])
