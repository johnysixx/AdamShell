from core.entity.social_entity import SocialEntity
import unittest
from meeting_place.bar_hex_geometry import BarHexGeometry
from meeting_place.bar_arrival_protocol import BarArrivalProtocol

class BarArrivalProtocolTests(unittest.TestCase):

    def setUp(self):
        self.geometry = BarHexGeometry()
        self.protocol = BarArrivalProtocol(self.geometry)

    def test_arriving_guest_ends_at_customer_side_of_bar(self):
        guest = SocialEntity.from_mapping(SocialEntity.from_mapping({'name': 'guest_1', 'type': 'human', 'state': 'entering', 'position': None}))
        result = self.protocol.arrive(guest)
        self.assertTrue(result)
        self.assertEqual(guest.state, 'at_bar')
        self.assertIsNotNone(guest.position)
        destination = self.geometry.find_cell(x=guest.position['x'], y=guest.position['y'])
        self.assertIsNotNone(destination)
        self.assertEqual(destination['kind'], 'customer_floor')
        self.assertNotEqual(destination['kind'], 'seating_place')
        self.assertNotEqual(destination['kind'], 'standing_place')

    def test_two_guests_take_different_bar_positions(self):
        guest_1 = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'human', 'state': 'entering', 'position': None})
        guest_2 = SocialEntity.from_mapping({'name': 'guest_2', 'type': 'human', 'state': 'entering', 'position': None})
        first_result = self.protocol.arrive(guest_1)
        second_result = self.protocol.arrive(guest_2)
        self.assertTrue(first_result)
        self.assertTrue(second_result)
        self.assertNotEqual(guest_1.position, guest_2.position)
        first_cell = self.geometry.find_cell(x=guest_1.position['x'], y=guest_1.position['y'])
        second_cell = self.geometry.find_cell(x=guest_2.position['x'], y=guest_2.position['y'])
        self.assertEqual(first_cell['occupied_by'], 'guest_1')
        self.assertEqual(second_cell['occupied_by'], 'guest_2')

    def test_fourth_guest_makes_additional_space_at_bar(self):
        initial_customer_floor = [cell for cell in self.geometry.cells if cell['kind'] == 'customer_floor']
        self.assertEqual(len(initial_customer_floor), 3)
        guests = [SocialEntity.from_mapping({'name': f'guest_{index}', 'type': 'human', 'state': 'entering', 'position': None}) for index in range(1, 5)]
        results = [self.protocol.arrive(guest) for guest in guests]
        self.assertEqual(results, [True, True, True, True])
        customer_floor = [cell for cell in self.geometry.cells if cell['kind'] == 'customer_floor']
        self.assertEqual(len(customer_floor), 4)
        occupied_customer_floor = [cell for cell in customer_floor if cell['occupied_by'] is not None]
        self.assertEqual(len(occupied_customer_floor), 4)
        self.assertEqual(guests[3].state, 'at_bar')
        self.assertIsNotNone(guests[3].position)
        fourth_place = self.geometry.find_cell(x=guests[3].position['x'], y=guests[3].position['y'])
        released = self.geometry.release_cell('guest_4', fourth_place)
        self.assertTrue(released)
        customer_floor_after_release = [cell for cell in self.geometry.cells if cell['kind'] == 'customer_floor']
        self.assertEqual(len(customer_floor_after_release), 4)
        self.assertEqual(fourth_place['kind'], 'customer_floor')
        self.assertIsNone(fourth_place['occupied_by'])

    def test_bar_frontage_can_grow_again_for_fifth_guest(self):
        guests = [SocialEntity.from_mapping({'name': f'guest_{index}', 'state': 'entering', 'position': None, 'type': 'human'}) for index in range(1, 6)]
        results = [self.protocol.arrive(guest) for guest in guests]
        self.assertEqual(results, [True, True, True, True, True])
        customer_floor = [cell for cell in self.geometry.cells if cell['kind'] == 'customer_floor']
        self.assertEqual(len(customer_floor), 5)
        occupied = [cell for cell in customer_floor if cell['occupied_by'] is not None]
        self.assertEqual(len(occupied), 5)
        positions = {(guest.position['x'], guest.position['y']) for guest in guests}
        self.assertEqual(len(positions), 5)

    def test_fourth_guest_expands_complete_bar_module(self):
        initial_customer = len([cell for cell in self.geometry.cells if cell['kind'] == 'customer_floor'])
        initial_bar = len([cell for cell in self.geometry.cells if cell['kind'] == 'bar'])
        initial_service = len([cell for cell in self.geometry.cells if cell['kind'] == 'service_floor'])
        guests = [SocialEntity.from_mapping({'name': f'guest_{index}', 'type': 'human', 'state': 'entering', 'position': None}) for index in range(1, 5)]
        for guest in guests:
            self.assertTrue(self.protocol.arrive(guest))
        customer = len([cell for cell in self.geometry.cells if cell['kind'] == 'customer_floor'])
        bar = len([cell for cell in self.geometry.cells if cell['kind'] == 'bar'])
        service = len([cell for cell in self.geometry.cells if cell['kind'] == 'service_floor'])
        self.assertEqual(customer, initial_customer + 1)
        self.assertEqual(bar, initial_bar + 1)
        self.assertEqual(service, initial_service + 2)

    def test_fifth_guest_expands_another_complete_bar_module(self):
        initial_customer = len([cell for cell in self.geometry.cells if cell['kind'] == 'customer_floor'])
        initial_bar = len([cell for cell in self.geometry.cells if cell['kind'] == 'bar'])
        initial_service = len([cell for cell in self.geometry.cells if cell['kind'] == 'service_floor'])
        guests = [SocialEntity.from_mapping({'name': f'guest_{index}', 'state': 'entering', 'position': None, 'type': 'human'}) for index in range(1, 6)]
        for guest in guests:
            self.assertTrue(self.protocol.arrive(guest))
        customer = len([cell for cell in self.geometry.cells if cell['kind'] == 'customer_floor'])
        bar = len([cell for cell in self.geometry.cells if cell['kind'] == 'bar'])
        service = len([cell for cell in self.geometry.cells if cell['kind'] == 'service_floor'])
        self.assertEqual(customer, initial_customer + 2)
        self.assertEqual(bar, initial_bar + 2)
        self.assertEqual(service, initial_service + 4)
if __name__ == '__main__':
    unittest.main()
