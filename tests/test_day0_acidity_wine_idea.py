import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0AcidityWineIdeaTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_serpent_explains_existing_ideas_to_god(self):
        result = self.scene.advance_to_acidity_wine_idea()
        summary = result['explained']['summary']
        self.assertTrue(summary['fuller_flavor'])
        self.assertTrue(summary['sweetness'])
        self.assertTrue(summary['bitterness'])

    def test_lilith_rejects_bitterness(self):
        result = self.scene.advance_to_acidity_wine_idea()
        self.assertEqual(result['revised']['rejection']['rejected_property'], 'bitterness')

    def test_lilith_proposes_acidity(self):
        result = self.scene.advance_to_acidity_wine_idea()
        idea = result['revised']['idea']
        self.assertTrue(idea['desired_property']['acidity'])

    def test_current_hypothesis_replaces_bitterness_with_acidity(self):
        self.scene.advance_to_acidity_wine_idea()
        hypothesis = self.scene.serpent_lilith_good_drink_discussion['current_hypothesis']
        self.assertEqual(hypothesis, {'fuller_flavor': True, 'sweetness': True, 'bitterness': False, 'acidity': True})

    def test_lilith_gives_serpent_her_drink_to_taste(self):
        result = self.scene.advance_to_acidity_wine_idea()
        event = result['tasted']
        self.assertEqual(event['giver'], 'lilith')
        self.assertEqual(event['taster'], 'serpent')
        self.assertEqual(event['drink'], 'lilith')

    def test_serpent_receives_lilith_effect_on_tasting(self):
        self.scene.advance_to_god_at_table()
        energy_before = float(getattr(self.scene.serpent, 'energy_j', 0.0))
        will_before = float(getattr(self.scene.serpent, 'creative_will', 0.0))
        effects = self.scene.lilith_order['final_drink'].effects
        self.scene.serpent_explains_wine_discussion_to_god()
        self.scene.lilith_rejects_bitterness_and_proposes_acidity()
        self.scene.lilith_gives_serpent_taste_of_lilith()
        self.assertEqual(self.scene.serpent.energy_j, energy_before + float(effects.get('energy_j', 0.0)))
        self.assertEqual(self.scene.serpent.creative_will, will_before + float(effects.get('creative_will', 0.0)))

    def test_discussion_stays_unresolved(self):
        self.scene.advance_to_acidity_wine_idea()
        self.assertFalse(self.scene.serpent_lilith_good_drink_discussion['resolved'])
if __name__ == '__main__':
    unittest.main()
