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

        idea_entities = (
            universe.world[
                "idea_entities"
            ][
                "idea_entities"
            ]
        )

        for entity in idea_entities:
            self.assert_object_entity(
                entity
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
