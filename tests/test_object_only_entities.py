import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from gods import Gods
from idea_entities import IdeaEntities
from meeting_place.meeting_place import (
    MeetingPlace
)


class ObjectOnlyEntityTests(
    unittest.TestCase
):

    def setUp(
        self
    ):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

    def test_god_is_object_not_dict(
        self
    ):
        god = Gods(
            self.universe
        ).create_god(
            name="god",
            role="librarian"
        )

        self.assertFalse(
            isinstance(
                god,
                dict
            )
        )

        self.assertEqual(
            god.name,
            "god"
        )

        self.assertEqual(
            god.type,
            "god"
        )

    def test_idea_entity_is_object_not_dict(
        self
    ):
        entity = IdeaEntities(
            self.universe
        ).create_idea_entity(
            name="lilith",
            role="archetype_principle",
            active=True
        )

        self.assertFalse(
            isinstance(
                entity,
                dict
            )
        )

        self.assertEqual(
            entity.name,
            "lilith"
        )

        self.assertEqual(
            entity.type,
            "idea_entity"
        )

    def test_old_mapping_syntax_is_compatibility_only(
        self
    ):
        entity = IdeaEntities(
            self.universe
        ).create_idea_entity(
            name="serpent",
            active=True
        )

        entity[
            "energy_j"
        ] = 12.0

        self.assertEqual(
            entity.energy_j,
            12.0
        )

        self.assertIs(
            entity[
                "energy_j"
            ],
            entity.energy_j
        )

    def test_social_entity_can_pet_cat(
        self
    ):
        actor = IdeaEntities(
            self.universe
        ).create_idea_entity(
            name="lilith",
            active=True
        )

        manifestation = (
            self.universe
            .manifest_cat(
                name="test_social_cat",
                source="test"
            )
        )

        cat = manifestation[
            "cat"
        ]

        event = actor.pet_cat(
            cat
        )

        self.assertEqual(
            event[
                "actor"
            ],
            "lilith"
        )

        self.assertGreater(
            cat.affinity_toward(
                actor
            ),
            0.0
        )

    def test_petting_sets_next_social_target(
        self
    ):
        actor = IdeaEntities(
            self.universe
        ).create_idea_entity(
            name="serpent",
            active=True
        )

        cat = (
            self.universe
            .manifest_cat(
                name="social_target_cat",
                source="test"
            )[
                "cat"
            ]
        )

        actor.pet_cat(
            cat
        )

        self.assertEqual(
            cat.next_social_target,
            "serpent"
        )

        self.assertGreater(
            cat.social_attention_bias,
            0.0
        )

    def test_meeting_place_rejects_raw_dict_entity(
        self
    ):
        meeting = MeetingPlace(
            self.universe
        )

        with self.assertRaises(
            TypeError
        ):
            meeting.add_entity({
                "name": "illegal_dict_entity",
                "type": "idea_entity"
            })


if __name__ == "__main__":
    unittest.main()
