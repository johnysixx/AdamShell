import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0BartenderJudgeProposalAndWaterTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_serpent_orders_water_at_bar(self):
        result = self.scene.advance_to_everyone_at_bar_with_serpents_water()
        self.assertEqual(result['water_order']['drink'], 'water')

    def test_god_rejects_participant_vote(self):
        result = self.scene.advance_to_everyone_at_bar_with_serpents_water()
        self.assertEqual(result['judge_proposal']['rejects']['type'], 'participant_vote')

    def test_god_proposes_bartender_as_judge(self):
        result = self.scene.advance_to_everyone_at_bar_with_serpents_water()
        proposal = result['judge_proposal']['proposes']
        self.assertEqual(proposal['type'], 'bartender_judges')
        self.assertEqual(proposal['judge'], 'bartender')

    def test_bartender_judge_proposal_is_not_accepted_yet(self):
        self.scene.advance_to_everyone_at_bar_with_serpents_water()
        proposal = self.scene.serpent_lilith_drink_wager['bartender_judge_proposal']
        self.assertFalse(proposal['accepted'])

    def test_lilith_and_god_move_to_bar(self):
        self.scene.advance_to_everyone_at_bar_with_serpents_water()
        self.assertEqual(self.scene.lilith.bar_state['location'], 'bar_counter')
        self.assertEqual(self.scene.god.bar_state['location'], 'bar_counter')

    def test_serpent_gets_water_with_free_lemon_slice(self):
        result = self.scene.advance_to_everyone_at_bar_with_serpents_water()
        drink = result['water']['drink']
        self.assertEqual(drink['name'], 'water_with_lemon_slice')
        self.assertEqual(drink['garnish']['ingredient'], 'lemon')
        self.assertEqual(drink['garnish']['price'], 0)

    def test_lemon_slice_does_not_consume_whole_lemon(self):
        self.scene.advance_to_wager_vote_proposal()
        lemon_before = self.bar.back_room.bar_ingredients['lemon'].shots
        self.scene.serpent_orders_water_at_bar()
        self.scene.god_rejects_participant_vote_and_proposes_bartender()
        self.scene.lilith_and_god_leave_table_for_bar()
        self.scene.bartender_serves_serpent_water_with_free_lemon_slice()
        lemon_after = self.bar.back_room.bar_ingredients['lemon'].shots
        self.assertEqual(lemon_after, lemon_before)

    def test_everyone_ends_at_bar(self):
        self.scene.advance_to_everyone_at_bar_with_serpents_water()
        self.assertEqual(self.scene.serpent.bar_state['location'], 'bar_counter')
        self.assertEqual(self.scene.lilith.bar_state['location'], 'bar_counter')
        self.assertEqual(self.scene.god.bar_state['location'], 'bar_counter')
if __name__ == '__main__':
    unittest.main()
