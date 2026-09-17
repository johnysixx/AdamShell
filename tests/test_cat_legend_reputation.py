import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_knowledge import CatKnowledge
from cats.cat_social_objects import CatRelationship
from cats.cat_exploration_planner import CatExplorationPlanner

class CatLegendReputationTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.storyteller = self.cats.create_cat(name='pazuzu', color='black', fur_length='short')
        self.listener = self.cats.create_cat(name='garfield', color='orange', fur_length='short')
        place = CatKnowledge.remember_place(self.storyteller, 'quantum_layer', {'x': 9.0, 'y': 1.0, 'z': 0.0})
        self.legend = CatKnowledge.publish_legend(self.universe, self.storyteller, place)
        CatKnowledge.hear_legend(self.listener, self.storyteller, self.legend)

    def test_verified_legend_increases_trust(self):
        place = CatKnowledge.remember_place(self.listener, 'quantum_layer', {'x': 9.0, 'y': 1.0, 'z': 0.0})
        CatKnowledge.verify_heard_legend(self.listener, place)
        trust = self.listener.relationships['pazuzu'].trust
        self.assertAlmostEqual(trust, 0.6)

    def test_contradicted_legend_decreases_trust(self):
        result = CatKnowledge.contradict_heard_legend(cat=self.listener, legend_id=self.legend.legend_id)
        self.assertTrue(result['contradicted'])
        trust = self.listener.relationships['pazuzu'].trust
        self.assertAlmostEqual(trust, 0.35)

    def test_trust_history_is_recorded(self):
        CatKnowledge.contradict_heard_legend(self.listener, self.legend.legend_id)
        history = self.listener.relationships['pazuzu'].trust_history
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['reason'], 'personal_observation_contradicted')

    def test_trust_is_clamped_to_zero_and_one(self):
        for _ in range(20):
            CatKnowledge.adjust_storyteller_trust(self.listener, 'pazuzu', 0.1, 'test')
        self.assertEqual(self.listener.relationships['pazuzu'].trust, 1.0)
        for _ in range(20):
            CatKnowledge.adjust_storyteller_trust(self.listener, 'pazuzu', -0.15, 'test')
        self.assertEqual(self.listener.relationships['pazuzu'].trust, 0.0)

    def test_contradicted_legend_is_not_used_for_planning(self):
        CatKnowledge.contradict_heard_legend(self.listener, self.legend.legend_id)
        self.listener.current_layer = 'meeting_place'
        result = CatExplorationPlanner.choose_destination(cat=self.listener, universe=self.universe)
        heard_candidates = [candidate for candidate in result['candidates'] if candidate.get('source') == 'heard_legend']
        self.assertEqual(heard_candidates, [])

    def test_trust_updates_preserve_existing_records_and_history(self):
        record = CatRelationship.create()
        record.trust = 0.8
        record.meet_count = 4
        record.trust_history = [{'reason': 'past_observation'}]
        legacy = CatRelationship.create()
        legacy.trust = 0.6
        legacy.trust_history = [{'reason': 'earlier_observation'}]
        legacy.custom_note = 'preserve_me'

        for name, relation, expected in (
            (self.storyteller.name, record, 0.7),
            ('legacy_storyteller', legacy, 0.5),
        ):
            self.listener.relationships[name] = relation
            history = relation.trust_history
            prior_event = dict(history[0])
            first = CatKnowledge.adjust_storyteller_trust(
                self.listener, name, 0.1, 'confirmed',
                legend_id=self.legend.legend_id,
            )
            second = CatKnowledge.adjust_storyteller_trust(
                self.listener, name, -0.2, 'contradicted',
                legend_id=self.legend.legend_id,
            )

            self.assertIs(self.listener.relationships[name], relation)
            self.assertIs(relation.trust_history, history)
            self.assertAlmostEqual(relation.trust, expected)
            self.assertAlmostEqual(
                CatKnowledge._trust_in_cat(self.listener, name), expected,
            )
            self.assertEqual(len(history), 3)
            self.assertEqual(history[0], prior_event)
            self.assertEqual(history[1], first)
            self.assertEqual(history[2], second)
            second['current'] = -1.0
            self.assertAlmostEqual(history[2]['current'], expected)

        self.assertEqual(record.meet_count, 4)
        self.assertEqual(legacy.custom_note, 'preserve_me')


if __name__ == '__main__':
    unittest.main()
