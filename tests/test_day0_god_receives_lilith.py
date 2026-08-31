import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0GodReceivesLilithTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def test_tree_is_stripped_after_one_plus_six_lemons(self):
        self.scene.advance_to_lemon_restock_after_god_order()
        tree = self.scene.bar_yard.lemon_tree
        self.assertEqual(tree.lemons, 0)
        self.assertFalse(tree.has_lemons)
        self.assertEqual(tree.state, 'stripped')
        self.assertEqual(tree.months_since_stripped, 0)

    def test_bar_has_six_lemons_before_second_attempt(self):
        self.scene.advance_to_lemon_restock_after_god_order()
        self.assertEqual(self.bar.back_room.bar_ingredients['lemon'].shots, 6)

    def test_gods_lilith_uses_current_two_sugar_recipe(self):
        result = self.scene.advance_to_god_holding_lilith()
        drink = result['drink']
        self.assertEqual(drink.ingredients['lemon'], 'whole')
        self.assertEqual(drink.ingredients['sugar'], 2)

    def test_successful_god_drink_consumes_one_of_six_lemons(self):
        self.scene.advance_to_god_holding_lilith()
        self.assertEqual(self.bar.back_room.bar_ingredients['lemon'].shots, 5)

    def test_god_receives_open_unpaid_receipt(self):
        result = self.scene.advance_to_god_holding_lilith()
        receipt = result['service']['receipt']
        self.assertFalse(receipt['paid'])
        self.assertEqual(receipt['status'], 'open_unpaid')

    def test_god_has_not_drunk_lilith_yet(self):
        result = self.scene.advance_to_god_holding_lilith()
        self.assertFalse(result['service']['receipt']['paid'])
        self.assertEqual(self.scene.god.bar_state['activity'], 'holding_lilith')

    def test_cronenberg_precedes_successful_second_attempt(self):
        self.scene.advance_to_god_holding_lilith()
        names = [event['name'] for event in self.scene.history]
        failure = names.index('gods_lilith_fails_without_lemon')
        restock = names.index('bartender_returns_with_lemon_stock')
        success = names.index('bartender_mixes_gods_lilith')
        service = names.index('bartender_serves_gods_lilith')
        self.assertLess(failure, restock)
        self.assertLess(restock, success)
        self.assertLess(success, service)
if __name__ == '__main__':
    unittest.main()
