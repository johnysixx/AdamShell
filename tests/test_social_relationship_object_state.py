from core.entity.social_entity import (
    CatPettedEvent,
    SocialEntity,
    SocialInteractionRecord,
    SocialRelationshipRegistry,
    SocialRelationshipEntry,
)
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
        ).cat

    def test_petting_creates_social_relationship_object(self):
        self.actor.pet_cat(self.cat)

        relation = self.cat.social_relationships.relationship_for('lilith')

        self.assertIsInstance(relation, SocialRelationship)
        self.assertEqual(relation.pet_count, 1)
        self.assertGreater(relation.affinity, 0.0)
        self.assertEqual(relation.last_interaction, 'pet')

    def test_last_social_interaction_is_object_state(
        self
    ):
        event = self.actor.pet_cat(
            self.cat
        )

        interaction = (
            self.cat
            .last_social_interaction
        )

        self.assertIsInstance(
            interaction,
            SocialInteractionRecord,
        )

        self.assertEqual(
            interaction.interaction_type,
            'pet',
        )

        self.assertEqual(
            interaction.actor,
            'lilith',
        )

        for mapping_method in (
            'get',
            'keys',
            'items',
            'values',
        ):
            self.assertFalse(
                hasattr(
                    interaction,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = interaction['actor']

        snapshot = interaction.to_dict()
        snapshot['actor'] = 'changed'

        self.assertEqual(
            interaction.actor,
            'lilith',
        )

        self.assertIsInstance(event, CatPettedEvent)
        self.assertFalse(hasattr(event, 'get'))
        with self.assertRaises(TypeError):
            _ = event['actor']

        self.assertEqual(
            event.actor,
            'lilith',
        )

    def test_repeated_petting_replaces_immutable_state(self):
        self.actor.pet_cat(self.cat)

        initial_registry = self.cat.social_relationships
        initial = initial_registry.relationship_for("lilith")

        self.actor.pet_cat(self.cat)

        current_registry = self.cat.social_relationships
        current = current_registry.relationship_for("lilith")

        self.assertIsNot(current_registry, initial_registry)
        self.assertIsNot(current, initial)

        self.assertEqual(initial.pet_count, 1)
        self.assertEqual(current.pet_count, 2)
        self.assertGreater(current.affinity, initial.affinity)

        self.assertIs(
            initial_registry.relationship_for("lilith"),
            initial,
        )

    def test_social_relationship_registry_rejects_mapping_values(self):
        self.actor.pet_cat(self.cat)
        previous = self.cat.social_relationships

        with self.assertRaises(TypeError):
            self.cat.social_relationships = {
                "lilith": {
                    "affinity": 0.5,
                }
            }

        self.assertIs(
            self.cat.social_relationships,
            previous,
        )

        with self.assertRaises(TypeError):
            _ = previous["lilith"]

        for method in ("get", "keys", "items", "values"):
            self.assertFalse(hasattr(previous, method))

    def test_registry_and_relationship_are_frozen(self):
        from dataclasses import FrozenInstanceError

        self.actor.pet_cat(self.cat)

        registry = self.cat.social_relationships
        relationship = registry.relationship_for("lilith")

        self.assertIsInstance(
            registry, SocialRelationshipRegistry
        )
        self.assertIsInstance(
            registry.entries[0], SocialRelationshipEntry
        )

        with self.assertRaises(FrozenInstanceError):
            registry.entries = ()

        with self.assertRaises(FrozenInstanceError):
            relationship.affinity = 1.0

        with self.assertRaises(FrozenInstanceError):
            relationship.pet_count = 99

        snapshot = registry.to_dict()
        snapshot["lilith"]["pet_count"] = 99

        self.assertEqual(relationship.pet_count, 1)

    def test_social_relationship_serialization_boundary(self):
        entity = SocialEntity.from_mapping({
            "name": "guest",
            "social_relationships": {
                "lilith": {
                    "affinity": 0.4,
                    "pet_count": 2,
                    "last_interaction": "pet",
                }
            },
        })

        self.assertIsInstance(
            entity.social_relationships,
            SocialRelationshipRegistry,
        )

        snapshot = entity.to_dict()
        snapshot["social_relationships"]["lilith"][
            "affinity"
        ] = 1.0

        self.assertEqual(
            entity.social_relationships
            .relationship_for("lilith").affinity,
            0.4,
        )

    def test_to_dict_returns_detached_boundary_snapshot(self):
        self.actor.pet_cat(self.cat)
        relation = self.cat.social_relationships.relationship_for('lilith')

        snapshot = relation.to_dict()
        snapshot['affinity'] = 1.0
        snapshot['pet_count'] = 99

        self.assertNotEqual(relation.affinity, snapshot['affinity'])
        self.assertEqual(relation.pet_count, 1)


if __name__ == '__main__':
    unittest.main()
