import unittest

from cats.cat_social_objects import CatRelationship
from cats.cat_social_system import CatSocialSystem
from cats.cats import Cats
from universe.universe import Universe


class CatRelationshipObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.first = self.cats.create_cat(
            name="first",
            color="black",
            fur_length="short",
        )
        self.second = self.cats.create_cat(
            name="second",
            color="white",
            fur_length="short",
        )
        self.first.position = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        }
        self.second.position = dict(
            self.first.position
        )
        self.system = CatSocialSystem(
            self.cats
        )

    def test_social_meeting_creates_relationship_object(self):
        self.system.meet(
            self.first,
            self.second,
        )

        relationship = self.first.relationships[
            self.second.name
        ]

        self.assertIsInstance(
            relationship,
            CatRelationship,
        )

    def test_relationship_has_neutral_defaults(self):
        relationship = CatRelationship.create()

        self.assertEqual(
            relationship.familiarity,
            0.0,
        )
        self.assertEqual(
            relationship.trust,
            0.5,
        )
        self.assertEqual(
            relationship.affiliation,
            0.0,
        )
        self.assertEqual(
            relationship.tension,
            0.0,
        )
        self.assertEqual(
            relationship.shared_scent,
            0.0,
        )

    def test_social_updates_preserve_relationship_object(self):
        self.system.meet(
            self.first,
            self.second,
        )

        relationship = self.first.relationships[
            self.second.name
        ]

        self.assertIsInstance(
            relationship,
            CatRelationship,
        )
        self.assertGreater(
            relationship.meet_count,
            0,
        )
        self.assertIsNotNone(
            relationship.last_interaction,
        )

    def test_knowledge_reads_object_relationship_trust(self):
        from cats.cat_knowledge import CatKnowledge

        self.system.meet(self.first, self.second)
        relationship = self.first.relationships[self.second.name]

        self.assertIsInstance(relationship, CatRelationship)
        relationship.trust = 0.9

        self.assertAlmostEqual(
            CatKnowledge._trust_in_cat(
                self.first,
                self.second.name,
            ),
            0.9,
        )


if __name__ == "__main__":
    unittest.main()
