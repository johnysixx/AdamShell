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

    def test_reads_and_clamps_object_and_second_relationship_trust(self):
        relationship = CatRelationship.create()
        history = [{'reason': 'past_meeting'}]
        second_relationship = CatRelationship(trust_history=history)

        for value, expected in (
            (0.9, 0.9), ('0.8', 0.8), (-0.2, 0.0), (1.2, 1.0),
        ):
            relationship.trust = value
            second_relationship.trust = value
            for record in (relationship, second_relationship):
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
            self.assertEqual(second_relationship.trust, value)

        self.assertIs(second_relationship.trust_history, history)
        self.assertEqual(history, [{'reason': 'past_meeting'}])

    def test_missing_trust_defaults_without_mutating_records(self):
        self.assertEqual(
            CatKnowledge._trust_in_cat(self.listener, self.storyteller_name),
            0.5,
        )
        self.assertNotIn(self.storyteller_name, self.listener.relationships)

        second_relationship = CatRelationship()
        incomplete = CatRelationship()
        for record in (second_relationship, incomplete, None):
            self.listener.relationships[self.storyteller_name] = record
            self.assertEqual(
                CatKnowledge._trust_in_cat(self.listener, self.storyteller_name),
                0.5,
            )
            self.assertIs(
                self.listener.relationships[self.storyteller_name], record,
            )

        self.assertEqual(second_relationship.trust, 0.5)
        self.assertEqual(incomplete.trust, 0.5)


    def test_adjustment_initializes_missing_fields_on_existing_records(self):
        relationship = CatRelationship()
        second_relationship = CatRelationship()
        for name, record in (('object', relationship), ('second_relationship', second_relationship)):
            self.listener.relationships[name] = record
            event = CatKnowledge.adjust_storyteller_trust(
                self.listener, name, 0.1, 'confirmed', legend_id='legend_1',
            )
            self.assertIs(self.listener.relationships[name], record)
            self.assertAlmostEqual(event['previous'], 0.5)
            self.assertAlmostEqual(event['current'], 0.6)
            self.assertAlmostEqual(event['delta'], 0.1)
            self.assertEqual(event['reason'], 'confirmed')
            self.assertEqual(event['legend_id'], 'legend_1')

        self.assertAlmostEqual(relationship.trust, 0.6)
        self.assertAlmostEqual(second_relationship.trust, 0.6)
        self.assertEqual(len(relationship.trust_history), 1)
        self.assertEqual(relationship.trust_history, second_relationship.trust_history)
        self.assertIsNot(relationship.trust_history, second_relationship.trust_history)

    def test_adjustments_preserve_history_and_record_effective_delta(self):
        relationship = CatRelationship.create()
        relationship.trust = '1.2'
        object_history = [{'reason': 'past_meeting'}]
        relationship.trust_history = object_history
        second_relationship_history = [{'reason': 'past_meeting'}]
        second_relationship = CatRelationship(trust='1.2', trust_history=second_relationship_history)

        for name, record, history in (
            ('object', relationship, object_history),
            ('second_relationship', second_relationship, second_relationship_history),
        ):
            self.listener.relationships[name] = record
            previous_entry = history[0]
            for index, (delta, previous, current) in enumerate((
                (-0.1, 1.2, 1.0), (-2.0, 1.0, 0.0), (2.0, 0.0, 1.0),
            )):
                event = CatKnowledge.adjust_storyteller_trust(
                    self.listener, name, delta, 'updated', legend_id='legend_1',
                )
                self.assertAlmostEqual(event['previous'], previous)
                self.assertAlmostEqual(event['current'], current)
                self.assertAlmostEqual(event['delta'], current - previous)
                self.assertEqual(event['reason'], 'updated')
                self.assertEqual(event['legend_id'], 'legend_1')
                self.assertEqual(len(history), index + 2)
                self.assertEqual(history[-1], event)
                self.assertIsNot(history[-1], event)
                event['current'] = -1.0
                self.assertAlmostEqual(history[-1]['current'], current)

            self.assertIs(self.listener.relationships[name], record)
            self.assertIs(history[0], previous_entry)
            self.assertEqual(previous_entry, {'reason': 'past_meeting'})

        self.assertEqual(relationship.trust, 1.0)
        self.assertEqual(second_relationship.trust, 1.0)
        self.assertIs(relationship.trust_history, object_history)
        self.assertIs(second_relationship.trust_history, second_relationship_history)


if __name__ == '__main__':
    unittest.main()
