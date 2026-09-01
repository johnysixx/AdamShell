import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0GodUnderstandsSweetnessTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_god_tastes_wine_and_calls_it_bad(self):
        result = self.scene.advance_to_god_understands_sweetness()
        assessment = result['wine']['assessment']
        self.assertEqual(assessment['quality'], 'bad')
        self.assertEqual(assessment['body'], 'watery')

    def test_god_compares_wine_to_water_with_grapes(self):
        result = self.scene.advance_to_god_understands_sweetness()
        self.assertEqual(result['wine']['assessment']['comparison'], 'water_in_which_someone_soaked_grapes')

    def test_god_has_now_tasted_the_wine(self):
        self.scene.advance_to_god_understands_sweetness()
        self.assertTrue(self.scene.god.bar_state['wine_order']['tasted'])

    def test_lilith_explains_sweetness(self):
        result = self.scene.advance_to_god_understands_sweetness()
        self.assertEqual(result['explanation']['principle'], 'sweetness')
        self.assertTrue(self.scene.god.bar_knowledge['sweetness_explained'])

    def test_god_finishes_serpents_mead(self):
        result = self.scene.advance_to_god_understands_sweetness()
        mead = result['mead']
        self.assertTrue(mead['finished'])
        self.assertEqual(mead['source'], 'serpent')
        self.assertEqual(self.scene.serpent.bar_state['mead_finished_by'], 'god')

    def test_mead_teaches_god_sweetness(self):
        result = self.scene.advance_to_god_understands_sweetness()
        mead = result['mead']
        self.assertTrue(mead['understands']['sweetness'])
        self.assertTrue(mead['assessment']['sweet'])

    def test_god_still_says_mead_is_not_good(self):
        result = self.scene.advance_to_god_understands_sweetness()
        self.assertFalse(result['mead']['assessment']['good'])

    def test_wine_hypothesis_remains_unresolved(self):
        self.scene.advance_to_god_understands_sweetness()
        discussion = self.scene.serpent_lilith_good_drink_discussion
        self.assertEqual(discussion.current_hypothesis.acidity, 'moderate')
        self.assertTrue(discussion.current_hypothesis.sweetness)
        self.assertFalse(discussion.resolved)

    def test_event_order(self):
        self.scene.advance_to_god_understands_sweetness()
        names = [event['name'] for event in self.scene.history]
        wine = names.index('god_tastes_existing_wine')
        explanation = names.index('lilith_explains_sweetness_to_god')
        mead = names.index('god_finishes_serpents_mead_and_understands_sweetness')
        self.assertLess(wine, explanation)
        self.assertLess(explanation, mead)
if __name__ == '__main__':
    unittest.main()
