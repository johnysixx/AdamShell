from core.entity.social_entity import SocialEntity
import unittest
from universe.cat_recipient_registry import CatRecipientRegistry

class CatRecipientRegistryTests(unittest.TestCase):

    def test_register_and_find_recipient(self):
        registry = CatRecipientRegistry()
        entity = SocialEntity.from_mapping({'id': 'alice', 'name': 'Alice', 'type': 'human', 'needs_cat': True, 'current_layer': 'idea_universe', 'position': {'x': 1.0, 'y': 2.0, 'z': 3.0}})
        registered = registry.register(entity)
        self.assertIs(registered, entity)
        self.assertIs(registry.find('alice'), entity)

    def test_any_entity_can_need_cat(self):
        registry = CatRecipientRegistry()
        entity = SocialEntity.from_mapping({'id': 'strange_entity', 'type': 'idea_entity', 'needs_cat': True})
        registry.register(entity)
        waiting = registry.waiting_for_cat()
        self.assertEqual(waiting, [entity])
if __name__ == '__main__':
    unittest.main()
