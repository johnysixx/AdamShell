from core.entity.social_entity import SocialEntity
import unittest
from meeting_place.bar_hex_geometry import BarHexGeometry
from meeting_place.bar_arrival_protocol import BarArrivalProtocol
from meeting_place.bar_departure_protocol import BarDepartureProtocol

class BarDepartureProtocolTests(unittest.TestCase):

    def setUp(self):
        self.geometry = BarHexGeometry()
        self.arrival = BarArrivalProtocol(self.geometry)
        self.departure = BarDepartureProtocol(self.geometry)

    def test_guest_can_leave_bar_and_release_place(self):
        guest = SocialEntity.from_mapping(SocialEntity.from_mapping({'name': 'guest_1', 'type': 'human', 'state': 'entering', 'position': None}))
        arrived = self.arrival.arrive(guest)
        self.assertTrue(arrived)
        occupied_place = self.geometry.find_cell(x=guest['position']['x'], y=guest['position']['y'])
        self.assertEqual(occupied_place['occupied_by'], 'guest_1')
        customer_count_before = len([cell for cell in self.geometry.cells if cell['kind'] == 'customer_floor'])
        result = self.departure.leave_bar(guest)
        self.assertTrue(result)
        self.assertIsNone(occupied_place['occupied_by'])
        self.assertEqual(occupied_place['kind'], 'customer_floor')
        customer_count_after = len([cell for cell in self.geometry.cells if cell['kind'] == 'customer_floor'])
        self.assertEqual(customer_count_after, customer_count_before)
        self.assertEqual(guest['state'], 'leaving_bar')
        self.assertIsNone(guest['position'])

    def test_guest_cannot_release_other_guests_bar_place(self):
        guest_1 = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'human', 'state': 'entering', 'position': None})
        guest_2 = SocialEntity.from_mapping({'name': 'guest_2', 'type': 'human', 'state': 'entering', 'position': None})
        self.arrival.arrive(guest_1)
        self.arrival.arrive(guest_2)
        guest_1_position = dict(guest_1['position'])
        guest_2['position'] = dict(guest_1_position)
        result = self.departure.leave_bar(guest_2)
        self.assertFalse(result)
        place = self.geometry.find_cell(x=guest_1_position['x'], y=guest_1_position['y'])
        self.assertEqual(place['occupied_by'], 'guest_1')
        self.assertEqual(guest_2['state'], 'at_bar')

    def test_released_expanded_bar_place_is_reused(self):
        guests = [SocialEntity.from_mapping({'name': f'guest_{index}', 'type': 'human', 'state': 'entering', 'position': None}) for index in range(1, 5)]
        for guest in guests:
            self.assertTrue(self.arrival.arrive(guest))
        customer_floor_before = [cell for cell in self.geometry.cells if cell['kind'] == 'customer_floor']
        self.assertEqual(len(customer_floor_before), 4)
        fourth_position = dict(guests[3]['position'])
        self.assertTrue(self.departure.leave_bar(guests[3]))
        guest_5 = SocialEntity.from_mapping({'name': 'guest_5', 'type': 'human', 'state': 'entering', 'position': None})
        self.assertTrue(self.arrival.arrive(guest_5))
        self.assertEqual(guest_5['position'], fourth_position)
        customer_floor_after = [cell for cell in self.geometry.cells if cell['kind'] == 'customer_floor']
        self.assertEqual(len(customer_floor_after), 4)
        reused_place = self.geometry.find_cell(x=fourth_position['x'], y=fourth_position['y'])
        self.assertEqual(reused_place['occupied_by'], 'guest_5')
if __name__ == '__main__':
    unittest.main()
