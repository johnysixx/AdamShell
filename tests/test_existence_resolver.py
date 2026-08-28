from core.entity.social_entity import SocialEntity
import unittest
from core.entity.existence import ExistenceResolver

class ExistenceResolverTests(unittest.TestCase):

    def test_remove_from_strongest_world_only(self):
        entity = SocialEntity.from_mapping({'name': 'guest_1', 'native_world': 'idea_universe', 'existence_by_world': {'idea_universe': 20.0, 'root_universe': 70.0, 'eden': 40.0}})
        result = ExistenceResolver.remove_from_strongest_world(entity)
        self.assertEqual(result['world'], 'root_universe')
        self.assertEqual(result['removed_existence_pct'], 70.0)
        self.assertEqual(entity['existence_by_world'], {'idea_universe': 20.0, 'root_universe': 0.0, 'eden': 40.0})

    def test_entity_still_exists_if_any_world_has_existence(self):
        entity = SocialEntity.from_mapping({'name': 'guest_1', 'native_world': 'idea_universe', 'existence_by_world': {'idea_universe': 20.0, 'root_universe': 70.0, 'eden': 40.0}})
        ExistenceResolver.remove_from_strongest_world(entity)
        self.assertTrue(ExistenceResolver.exists_anywhere(entity))

    def test_entity_no_longer_exists_if_all_worlds_are_zero(self):
        entity = SocialEntity.from_mapping({'name': 'guest_1', 'native_world': 'idea_universe', 'existence_by_world': {'idea_universe': 0.0, 'root_universe': 70.0, 'eden': 0.0}})
        ExistenceResolver.remove_from_strongest_world(entity)
        self.assertFalse(ExistenceResolver.exists_anywhere(entity))

    def test_object_entity_can_remove_strongest_world_existence(self):

        class Guest:
            pass
        entity = Guest()
        entity.name = 'guest_1'
        entity.native_world = 'idea_universe'
        entity.existence_by_world = {'idea_universe': 20.0, 'root_universe': 70.0, 'eden': 40.0}
        result = ExistenceResolver.remove_from_strongest_world(entity)
        self.assertEqual(result['world'], 'root_universe')
        self.assertEqual(entity.existence_by_world, {'idea_universe': 20.0, 'root_universe': 0.0, 'eden': 40.0})
        self.assertTrue(ExistenceResolver.exists_anywhere(entity))
if __name__ == '__main__':
    unittest.main()
