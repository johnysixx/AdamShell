import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from universe.bootstraps.entity_bootstrap import (
    EntityBootstrap
)
from gods import Gods
from idea_entities import IdeaEntities


class AllEntitiesAreObjectsTests(
    unittest.TestCase
):

    def assert_object_entity(
        self,
        entity
    ):
        self.assertIsNotNone(
            entity
        )

        self.assertFalse(
            isinstance(
                entity,
                dict
            )
        )

        self.assertTrue(
            hasattr(
                entity,
                "name"
            )
        )

        self.assertTrue(
            hasattr(
                entity,
                "type"
            )
        )

    def test_god_is_object(
        self
    ):
        universe = Universe()

        god = Gods(
            universe
        ).create_god(
            name="god"
        )

        self.assert_object_entity(
            god
        )

    def test_idea_entity_is_object(
        self
    ):
        universe = Universe()

        serpent = IdeaEntities(
            universe
        ).create_idea_entity(
            name="serpent"
        )

        self.assert_object_entity(
            serpent
        )

    def test_god_mask_is_object(
        self
    ):
        universe = Universe()

        gods = Gods(
            universe
        )

        god = gods.create_god(
            name="god"
        )

        mask = gods.assume_mask(
            god=god,
            mask_name="director",
            role="quantum_director"
        )

        self.assert_object_entity(
            mask
        )

        self.assertEqual(
            mask.name,
            "director"
        )

        self.assertEqual(
            mask.type,
            "god_mask"
        )

        self.assertIs(
            mask.mask_of,
            god
        )

    def test_bootstrapped_entities_are_objects(
        self
    ):
        universe = Universe()
        registry = UniverseRegistry()

        (
            root_transition,
            layers,
            idea_universe
        ) = UniverseBootstrap(
            registry,
            universe
        ).run()

        EntityBootstrap(
            universe,
            idea_universe,
            root_transition
        ).run()

        self.assert_object_entity(
            universe.god
        )

        for god in universe.gods.gods:
            self.assert_object_entity(
                god
            )

        for cat in universe.cats_layer.cats:
            self.assert_object_entity(
                cat
            )

        # Canonical entities must remain domain objects.
        idea_entities = (
            universe.idea_entities.idea_entities
        )

        for entity in idea_entities:
            self.assert_object_entity(
                entity
            )

        # The world projection is a detached public index,
        # not the canonical registry of runtime objects.
        public_entries = universe.world[
            "idea_entities"
        ]["idea_entities"]

        state_entries = universe.world[
            "idea_entities"
        ]["idea_entities_state"]["idea_entities"]

        self.assertEqual(
            len(public_entries),
            len(idea_entities),
        )

        self.assertEqual(
            public_entries,
            state_entries,
        )

        for entity, entry in zip(
            idea_entities,
            public_entries,
            strict=True,
        ):
            self.assertIsInstance(entry, dict)
            self.assertIsNot(entity, entry)
            self.assertEqual(entry["name"], entity.name)
            self.assertEqual(entry["type"], entity.type)
            self.assertEqual(entry["role"], entity.role)

        # Mutating the public projection cannot change
        # the canonical bootstrap-created entity.
        if public_entries:
            original_name = idea_entities[0].name
            public_entries[0]["name"] = "modified_export"

            self.assertEqual(
                idea_entities[0].name,
                original_name,
            )

            self.assertEqual(
                state_entries[0]["name"],
                original_name,
            )

        meeting_place = layers.get(
            "meeting"
        )

        for entity in meeting_place.entities:
            self.assert_object_entity(
                entity
            )


if __name__ == "__main__":
    unittest.main()
