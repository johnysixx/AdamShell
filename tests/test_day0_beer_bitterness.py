import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0BeerBitternessTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_god_says_beer_is_not_so_bad(self):
        result = self.scene.advance_to_bitterness_split_between_wine_and_beer()
        self.assertTrue(result['god_beer']['assessment']['not_so_bad'])

    def test_god_understands_bitterness(self):
        result = self.scene.advance_to_bitterness_split_between_wine_and_beer()
        self.assertTrue(result['god_beer']['understands']['bitterness'])
        self.assertTrue(self.scene.god.bar_knowledge['bitterness']['understood'])

    def test_god_rejects_bitterness_for_wine(self):
        result = self.scene.advance_to_bitterness_split_between_wine_and_beer()
        self.assertFalse(result['god_beer']['wine_conclusion']['bitterness_belongs_in_wine'])
        self.assertFalse(self.scene.serpent_lilith_good_drink_discussion.current_hypothesis.bitterness)

    def test_lilith_disagrees_that_beer_is_good(self):
        result = self.scene.advance_to_bitterness_split_between_wine_and_beer()
        self.assertTrue(result['lilith']['disagrees_beer_is_good'])

    def test_lilith_accepts_bitterness_for_good_beer(self):
        result = self.scene.advance_to_bitterness_split_between_wine_and_beer()
        self.assertTrue(result['lilith']['beer_conclusion']['bitterness_allowed'])
        beer = self.scene.serpent_lilith_good_drink_discussion.beer_hypothesis
        self.assertEqual(beer.bitterness, 'allowed')
        self.assertFalse(beer.resolved)

    def test_lilith_sip_applies_lilith_effects(self):
        self.scene.advance_to_three_way_drink_wager()
        energy_before = float(getattr(self.scene.lilith, 'energy_j', 0.0))
        will_before = float(getattr(self.scene.lilith, 'creative_will', 0.0))
        effects = self.scene.lilith_order.final_drink.effects
        self.scene.god_tastes_beer_and_understands_bitterness()
        self.scene.lilith_sips_lilith_and_reacts_to_beer()
        self.assertEqual(self.scene.lilith.energy_j, energy_before + float(effects.get('energy_j', 0.0)))
        self.assertEqual(self.scene.lilith.creative_will, will_before + float(effects.get('creative_will', 0.0)))
if __name__ == '__main__':
    unittest.main()
