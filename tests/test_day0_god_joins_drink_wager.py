import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0GodJoinsDrinkWagerTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_serpent_tells_god_about_existing_wager(self):
        result = self.scene.advance_to_three_way_drink_wager()
        self.assertEqual(result['explained']['speaker'], 'serpent')
        self.assertEqual(result['explained']['listener'], 'god')
        self.assertTrue(self.scene.god.bar_knowledge['drink_wager']['known'])

    def test_serpent_offers_participation(self):
        result = self.scene.advance_to_three_way_drink_wager()
        self.assertEqual(result['offered']['offered_by'], 'serpent')
        self.assertEqual(result['offered']['offered_to'], 'god')
        self.assertTrue(result['offered']['accepted'])

    def test_god_accepts(self):
        result = self.scene.advance_to_three_way_drink_wager()
        self.assertEqual(result['accepted']['participant'], 'god')
        self.assertTrue(self.scene.god.bar_state['participates_in_drink_wager'])

    def test_wager_now_has_three_participants(self):
        self.scene.advance_to_three_way_drink_wager()
        wager = self.scene.serpent_lilith_drink_wager
        self.assertEqual(wager.participants, ['serpent', 'lilith', 'god'])
        self.assertEqual(wager.type, 'three_way_drink_wager')

    def test_wager_is_still_unresolved(self):
        self.scene.advance_to_three_way_drink_wager()
        wager = self.scene.serpent_lilith_drink_wager
        self.assertFalse(wager.resolved)
        self.assertIsNone(wager.winner)

    def test_joining_wager_does_not_create_creator_mask(self):
        self.scene.advance_to_three_way_drink_wager()
        self.assertNotIn('creator', getattr(self.scene.god, 'masks', {}))

    def test_event_order(self):
        self.scene.advance_to_three_way_drink_wager()
        names = [event['name'] for event in self.scene.history]
        explained = names.index('serpent_tells_god_about_drink_wager')
        offered = names.index('serpent_offers_god_wager_participation')
        accepted = names.index('god_accepts_drink_wager')
        self.assertLess(explained, offered)
        self.assertLess(offered, accepted)
if __name__ == '__main__':
    unittest.main()
