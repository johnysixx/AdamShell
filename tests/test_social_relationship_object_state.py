import unittest

from core.entity.social_entity import SocialRelationship
from idea_entities import IdeaEntities
from multiverse import UniverseRegistry
from universe.universe import Universe


class SocialRelationshipObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.actor = IdeaEntities(self.universe).create_idea_entity(
            name='lilith',
            role='archetype_principle',
            active=True,
        )
        self.cat = self.universe.manifest_cat(
            name='social_relationship_object_cat',
            source='test',
        )['cat']

    def test_petting_creates_social_relationship_object(self):
        self.actor.pet_cat(self.cat)

        relation = self.cat.social_relationships['lilith']

        self.assertIsInstance(relation, SocialRelationship)
        self.assertEqual(relation.pet_count, 1)
        self.assertGreater(relation.affinity, 0.0)
        self.assertEqual(relation.last_interaction, 'pet')

    def test_repeated_petting_mutates_relationship_through_attributes(self):
        self.actor.pet_cat(self.cat)
        relation = self.cat.social_relationships['lilith']
        first_affinity = relation.affinity

        self.actor.pet_cat(self.cat)

        self.assertIs(self.cat.social_relationships['lilith'], relation)
        self.assertEqual(relation.pet_count, 2)
        self.assertGreater(relation.affinity, first_affinity)

    def test_social_relationship_registry_rejects_mapping_values(self):
        self.cat.social_relationships = {
            'lilith': {
                'affinity': 0.5,
                'pet_count': 1,
                'last_interaction': 'pet',
            },
        }

        with self.assertRaises(TypeError):
            self.actor.pet_cat(self.cat)

        with self.assertRaises(TypeError):
            self.cat.affinity_toward(self.actor)

    def test_to_dict_returns_detached_boundary_snapshot(self):
        self.actor.pet_cat(self.cat)
        relation = self.cat.social_relationships['lilith']

        snapshot = relation.to_dict()
        snapshot['affinity'] = 1.0
        snapshot['pet_count'] = 99

        self.assertNotEqual(relation.affinity, snapshot['affinity'])
        self.assertEqual(relation.pet_count, 1)


if __name__ == '__main__':
    unittest.main()
