import unittest

from cats.cat_knowledge import CatKnowledge
from cats.cat_social_objects import CatRelationship
from cats.cats import Cats
from universe.universe import Universe


class CatKnowledgeRelationshipTrustTests(unittest.TestCase):

    def setUp(self):
        self.cats = Cats(Universe())
        self.listener = self.cats.create_cat(
            name='listener', color='black', fur_length='short',
        )
        self.storyteller_name = 'storyteller'

    def test_reads_and_clamps_object_and_legacy_trust(self):
        relationship = CatRelationship.create()
        history = [{'reason': 'past_meeting'}]
        legacy = {'trust_history': history}

        for value, expected in (
            (0.9, 0.9), ('0.8', 0.8), (-0.2, 0.0), (1.2, 1.0),
        ):
            relationship.trust = value
            legacy['trust'] = value
            for record in (relationship, legacy):
                self.listener.relationships[self.storyteller_name] = record
                self.assertAlmostEqual(
                    CatKnowledge._trust_in_cat(
                        self.listener, self.storyteller_name,
                    ),
                    expected,
                )
                self.assertIs(
                    self.listener.relationships[self.storyteller_name], record,
                )
            self.assertEqual(relationship.trust, value)
            self.assertEqual(legacy['trust'], value)

        self.assertIs(legacy['trust_history'], history)
        self.assertEqual(history, [{'reason': 'past_meeting'}])

    def test_missing_trust_defaults_without_mutating_records(self):
        self.assertEqual(
            CatKnowledge._trust_in_cat(self.listener, self.storyteller_name),
            0.5,
        )
        self.assertNotIn(self.storyteller_name, self.listener.relationships)

        legacy = {}
        incomplete = CatRelationship()
        for record in (legacy, incomplete, None):
            self.listener.relationships[self.storyteller_name] = record
            self.assertEqual(
                CatKnowledge._trust_in_cat(self.listener, self.storyteller_name),
                0.5,
            )
            self.assertIs(
                self.listener.relationships[self.storyteller_name], record,
            )

        self.assertEqual(legacy, {})
        self.assertFalse(hasattr(incomplete, 'trust'))


if __name__ == '__main__':
    unittest.main()
