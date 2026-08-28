import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from idea_entities import IdeaEntities


class CatSocialRelationshipsTests(
    unittest.TestCase
):

    def setUp(
        self
    ):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.lilith = (
            IdeaEntities(
                self.universe
            )
            .create_idea_entity(
                name="lilith",
                role="archetype_principle",
                active=True
            )
        )

        self.serpent = (
            IdeaEntities(
                self.universe
            )
            .create_idea_entity(
                name="serpent",
                role="primordial_idea_entity",
                active=True
            )
        )

        manifestation = (
            self.universe
            .manifest_cat(
                name="social_cat",
                source="test"
            )
        )

        self.cat = manifestation[
            "cat"
        ]

    def test_people_are_objects(
        self
    ):
        self.assertFalse(
            isinstance(
                self.lilith,
                dict
            )
        )

        self.assertFalse(
            isinstance(
                self.serpent,
                dict
            )
        )

        self.assertEqual(
            self.lilith.name,
            "lilith"
        )

        self.assertEqual(
            self.serpent.name,
            "serpent"
        )

    def test_person_can_pet_cat(
        self
    ):
        event = self.lilith.pet_cat(
            self.cat
        )

        self.assertEqual(
            event[
                "name"
            ],
            "cat_petted"
        )

        self.assertEqual(
            event[
                "actor"
            ],
            "lilith"
        )

        self.assertEqual(
            event[
                "cat"
            ],
            "social_cat"
        )

    def test_cat_remembers_who_petted_it(
        self
    ):
        self.lilith.pet_cat(
            self.cat
        )

        relation = (
            self.cat
            .social_relationships[
                "lilith"
            ]
        )

        self.assertEqual(
            relation[
                "pet_count"
            ],
            1
        )

        self.assertGreater(
            relation[
                "affinity"
            ],
            0.0
        )

    def test_repeated_petting_increases_affinity(
        self
    ):
        self.lilith.pet_cat(
            self.cat
        )

        first = (
            self.cat
            .affinity_toward(
                self.lilith
            )
        )

        self.lilith.pet_cat(
            self.cat
        )

        second = (
            self.cat
            .affinity_toward(
                self.lilith
            )
        )

        self.assertGreater(
            second,
            first
        )

    def test_relationship_is_person_specific(
        self
    ):
        self.lilith.pet_cat(
            self.cat
        )

        self.lilith.pet_cat(
            self.cat
        )

        self.serpent.pet_cat(
            self.cat
        )

        self.assertGreater(
            self.cat.affinity_toward(
                self.lilith
            ),
            self.cat.affinity_toward(
                self.serpent
            )
        )

    def test_petting_changes_next_social_target(
        self
    ):
        self.serpent.pet_cat(
            self.cat
        )

        self.assertEqual(
            self.cat.next_social_target,
            "serpent"
        )

        self.assertGreater(
            self.cat.social_attention_bias,
            0.0
        )

    def test_last_person_to_pet_cat_becomes_current_social_target(
        self
    ):
        self.lilith.pet_cat(
            self.cat
        )

        self.assertEqual(
            self.cat.next_social_target,
            "lilith"
        )

        self.serpent.pet_cat(
            self.cat
        )

        self.assertEqual(
            self.cat.next_social_target,
            "serpent"
        )


if __name__ == "__main__":
    unittest.main()
