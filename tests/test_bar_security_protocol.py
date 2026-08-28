from core.entity.social_entity import SocialEntity
from meeting_place.back_room_black_box import BackRoomBlackBox
import unittest
from unittest.mock import Mock, patch
from universe.dark_sector import DarkSector
from meeting_place.bar_counter import BarCounter
from meeting_place.bartender import Bartender
from meeting_place.bouncer import Bouncer
from meeting_place.bar_blacklist import BarBlacklist
from meeting_place.bar_incident_book import BarIncidentBook
from meeting_place.bar_hex_geometry import BarHexGeometry
from meeting_place.bar_security_protocol import BarSecurityProtocol
from core.entity.cronenberg import Cronenberg

class BarSecurityProtocolTests(unittest.TestCase):

    def setUp(self):
        self.geometry = BarHexGeometry()
        self.bar_counter = BarCounter()
        self.bartender = Bartender(self.bar_counter.hidden_story_book)
        self.blacklist = BarBlacklist()
        self.back_room_black_box = BackRoomBlackBox()
        self.incident_book = BarIncidentBook(recorder=self.back_room_black_box)
        self.bouncer = Bouncer(blacklist=self.blacklist)
        self.protocol = BarSecurityProtocol(geometry=self.geometry, bar_counter=self.bar_counter, bartender=self.bartender, bouncer=self.bouncer)
        self.protocol.incident_book = self.incident_book

    def test_guest_behind_bar_makes_bartender_press_red_button(self):
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest'})
        service = self.geometry.find_cell(name='bar_service_floor')
        with patch.object(self.bar_counter.red_button, 'press', wraps=self.bar_counter.red_button.press) as press_mock:
            result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        press_mock.assert_called_once_with()

    def test_red_button_brings_bouncer_inside_bar(self):
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest'})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        self.assertEqual(self.bouncer.state, 'responding_inside_bar')
        self.assertEqual(self.bouncer.position, 'inside_bar')

    def test_bouncer_ejects_guest_and_bans_reentry(self):
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        self.assertEqual(guest.state, 'ejected')
        self.assertIsNone(guest.position)
        self.assertTrue(self.blacklist.is_banned('guest_1'))
        self.assertFalse(self.bouncer.can_enter(guest))

    def test_ejected_guest_pays_all_existence_and_energy(self):
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 73.5, 'energy_j': 42.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        self.assertEqual(guest.state, 'ejected')
        self.assertEqual(guest.existence_pct, 0.0)
        self.assertEqual(guest.energy_j, 0.0)
        self.assertEqual(self.protocol.last_confiscation, {'guest': 'guest_1', 'existence_pct': 73.5, 'energy_j': 42.0})

    def test_confiscation_is_followed_by_cat_d20_roll(self):
        cat_d20 = Mock()
        cat_d20.roll.return_value = {'value': 17, 'turned': True}
        self.protocol.cat_d20 = cat_d20
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 42.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        cat_d20.roll.assert_called_once_with()
        self.assertEqual(self.protocol.last_security_roll, 17)

    def test_security_roll_selects_cat_or_cronenberg(self):
        self.assertEqual(self.protocol.interpret_security_roll(1), 'cronenberg')
        self.assertEqual(self.protocol.interpret_security_roll(10), 'cronenberg')
        self.assertEqual(self.protocol.interpret_security_roll(11), 'cat')
        self.assertEqual(self.protocol.interpret_security_roll(20), 'cat')

    def test_security_roll_is_interpreted_after_confiscation(self):
        cat_d20 = Mock()
        cat_d20.roll.return_value = {'value': 17, 'turned': True}
        self.protocol.cat_d20 = cat_d20
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 42.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        self.assertEqual(self.protocol.last_security_roll, 17)
        self.assertEqual(self.protocol.last_security_outcome, 'cat')

    def test_successful_security_roll_creates_real_cat_via_cats_system(self):
        cat_d20 = Mock()
        cat_d20.roll.return_value = {'value': 17, 'turned': True}
        cats = Mock()
        created_cat = SocialEntity.from_mapping({'name': 'security_cat_guest_1', 'type': 'cat', 'state': 'created'})
        cats.create_cat.return_value = created_cat
        self.protocol.cat_d20 = cat_d20
        self.protocol.cats = cats
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 42.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        cats.create_cat.assert_called_once_with(name='security_cat_guest_1', color='black', fur_length='short', origin='bar_security_confiscation')
        self.assertIs(self.protocol.last_security_creation, created_cat)
        self.assertEqual(self.protocol.last_security_creation.type, 'cat')

    def test_failed_security_roll_creates_real_cronenberg(self):
        cat_d20 = Mock()
        cat_d20.roll.return_value = {'value': 7, 'turned': True}
        self.protocol.cat_d20 = cat_d20
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 42.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        self.assertEqual(self.protocol.last_security_roll, 7)
        self.assertEqual(self.protocol.last_security_outcome, 'cronenberg')
        self.assertIsInstance(self.protocol.last_security_creation, Cronenberg)
        self.assertEqual(self.protocol.last_security_creation.type, 'cronenberg')
        self.assertEqual(self.protocol.last_security_creation.traits.source_component, 'bar_security_protocol')
        self.assertEqual(self.protocol.last_security_creation.traits.source_operation, 'security_d20_failure')

    def test_failed_security_roll_leaves_cronenberg_in_quantum_layer(self):
        cat_d20 = Mock()
        cat_d20.roll.return_value = {'value': 7, 'turned': True}
        self.protocol.cat_d20 = cat_d20
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 42.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        cronenberg = self.protocol.last_security_creation
        self.assertIsInstance(cronenberg, Cronenberg)
        self.assertEqual(cronenberg.type, 'cronenberg')
        self.assertEqual(cronenberg.location, 'quantum_layer')
        self.assertEqual(cronenberg.state, 'born_from_quantum_error')

    def test_confiscated_energy_is_split_25_50_25(self):
        allocation = self.protocol.split_confiscated_energy(100.0)
        self.assertEqual(allocation, {'entity_energy_j': 25.0, 'multiverse_energy_j': 50.0, 'bar_energy_j': 25.0})

    def test_confiscated_energy_is_allocated_after_ejection(self):
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 80.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        self.assertEqual(self.protocol.last_energy_allocation, {'entity_energy_j': 20.0, 'multiverse_energy_j': 40.0, 'bar_energy_j': 20.0})

    def test_security_cat_uses_quantum_box_with_forced_cat_result(self):
        cat_d20 = Mock()
        cat_d20.roll.return_value = {'value': 17, 'turned': True}
        universe = Mock()
        box = Mock()
        box.id = 'quantum_box_security'
        box.resolve_state.return_value = {'type': 'quantum_box_collapsed', 'quantum_box_id': box.id, 'result': 'cat', 'cause': 'bar_security', 'observer': 'bartender', 'tick': None}
        universe.create_quantum_box.return_value = box
        self.protocol.cat_d20 = cat_d20
        self.protocol.universe = universe
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 100.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        universe.create_quantum_box.assert_called_once_with()
        box.resolve_state.assert_called_once_with(result='cat', cause='bar_security', observer='bartender', tick=None)
        self.assertIs(self.protocol.last_security_box, box)

    def test_entity_share_is_consumed_as_creation_energy(self):
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 100.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        self.assertEqual(self.protocol.last_creation_energy_j, 25.0)
        self.assertEqual(self.protocol.last_energy_allocation, {'entity_energy_j': 25.0, 'multiverse_energy_j': 50.0, 'bar_energy_j': 25.0})

    def test_multiverse_share_returns_to_universe_energy_pool(self):
        universe = Mock()
        universe.energy_pool = 100.0
        universe.dark_sector = DarkSector()
        self.protocol.universe = universe
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 100.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        self.assertEqual(universe.energy_pool, 145.0)
        self.assertEqual(universe.dark_sector.dark_energy_j, 5.0)
        self.assertEqual(self.protocol.last_energy_allocation['multiverse_energy_j'], 50.0)

    def test_bar_share_goes_to_bar_energy_reservoir(self):
        bar_energy_reservoir = Mock()
        self.protocol.bar_energy_reservoir = bar_energy_reservoir
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 100.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        bar_energy_reservoir.add_energy.assert_called_once_with(source='bar_security_confiscation', amount_j=20.0)
        self.assertEqual(self.protocol.last_energy_allocation['bar_energy_j'], 25.0)
        self.assertEqual(self.protocol.last_bar_dark_energy_j, 5.0)

    def test_bar_share_splits_energy_and_dark_energy(self):
        bar_energy_reservoir = Mock()
        bottle_shelf = Mock()
        self.protocol.bar_energy_reservoir = bar_energy_reservoir
        self.protocol.bottle_shelf = bottle_shelf
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 100.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        bar_energy_reservoir.add_energy.assert_called_once_with(source='bar_security_confiscation', amount_j=20.0)
        bottle_shelf.add_dark_energy.assert_called_once_with(5.0)

    def test_ejection_removes_existence_only_from_strongest_world(self):
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 70.0, 'native_world': 'idea_universe', 'existence_by_world': {'idea_universe': 20.0, 'root_universe': 70.0, 'eden': 40.0}, 'energy_j': 100.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        self.assertEqual(guest.existence_by_world, {'idea_universe': 20.0, 'root_universe': 0.0, 'eden': 40.0})
        self.assertTrue(guest.exists_somewhere)

    def test_ejection_marks_entity_gone_if_no_world_existence_remains(self):
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 70.0, 'native_world': 'root_universe', 'existence_by_world': {'idea_universe': 0.0, 'root_universe': 70.0, 'eden': 0.0}, 'energy_j': 100.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        self.assertEqual(guest.existence_by_world, {'idea_universe': 0.0, 'root_universe': 0.0, 'eden': 0.0})
        self.assertFalse(guest.exists_somewhere)

    def test_ban_applies_to_new_manifestation_of_same_identity(self):
        first_manifestation = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 70.0, 'native_world': 'root_universe', 'existence_by_world': {'root_universe': 70.0, 'eden': 40.0}, 'energy_j': 100.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(first_manifestation, service)
        self.assertTrue(result)
        second_manifestation = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'arriving', 'position': None, 'existence_pct': 40.0, 'native_world': 'eden', 'existence_by_world': {'root_universe': 0.0, 'eden': 40.0}, 'energy_j': 10.0})
        self.assertFalse(self.bouncer.can_enter(second_manifestation))

    def test_unauthorized_bar_entry_adds_identity_to_blacklist(self):
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 100.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        self.assertTrue(self.blacklist.is_banned('guest_1'))

    def test_generic_bartender_red_button_press_summons_bouncer_without_blacklist(self):
        self.bar_counter.red_button.activate_alarm()
        pressed = self.protocol.handle_bartender_red_button_press(reason='generic_security_call')
        self.assertTrue(pressed)
        self.assertEqual(self.bouncer.state, 'responding_inside_bar')
        self.assertEqual(self.bouncer.position, 'inside_bar')
        self.assertEqual(self.blacklist.denied_identities, [])

    def test_cat_alarm_clear_does_not_summon_bouncer(self):
        self.bar_counter.red_button.activate_alarm()
        result = self.protocol.handle_bartender_red_button_press(reason='cat_alarm_clear')
        self.assertTrue(result)
        self.assertFalse(self.bar_counter.red_button.alarm_active)
        self.assertEqual(self.bouncer.state, 'standing_outside_bar')
        self.assertEqual(self.bouncer.position, 'outside_bar')
        self.assertEqual(self.blacklist.denied_identities, [])

    def test_generic_security_incident_summons_bouncer_without_blacklist(self):
        incident = {'name': 'bar_security_incident', 'category': 'disturbance', 'reason': 'unknown_disturbance', 'offender': None, 'blacklist_after': False}
        result = self.protocol.handle_security_incident(incident)
        self.assertTrue(result)
        self.assertEqual(self.bouncer.state, 'responding_inside_bar')
        self.assertEqual(self.bouncer.position, 'inside_bar')
        self.assertEqual(self.blacklist.denied_identities, [])

    def test_security_incident_is_recorded_before_response(self):
        from meeting_place.bar_incident_book import BarIncidentBook
        incident_book = BarIncidentBook(recorder=BackRoomBlackBox())
        self.protocol.incident_book = incident_book
        incident = {'name': 'bar_security_incident', 'category': 'disturbance', 'reason': 'unknown_disturbance', 'offender': None}
        result = self.protocol.handle_security_incident(incident)
        self.assertTrue(result)
        self.assertEqual(len(incident_book.incidents), 1)
        self.assertEqual(incident_book.incidents[0]['reason'], 'unknown_disturbance')
        self.assertEqual(self.bouncer.state, 'responding_inside_bar')

    def test_unauthorized_area_incident_is_recorded_with_offender(self):
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 100.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        self.assertEqual(len(self.incident_book.incidents), 1)
        incident = self.incident_book.incidents[0]
        self.assertEqual(incident['reason'], 'unauthorized_area')
        self.assertEqual(incident['offender'], 'guest_1')

    def test_unauthorized_area_incident_is_marked_resolved(self):
        guest = SocialEntity.from_mapping({'name': 'guest_1', 'type': 'guest', 'state': 'behind_bar', 'position': {'x': 4000, 'y': 0}, 'existence_pct': 100.0, 'energy_j': 100.0})
        service = self.geometry.find_cell(name='bar_service_floor')
        result = self.protocol.handle_guest_entry(guest, service)
        self.assertTrue(result)
        incident = self.incident_book.incidents[-1]
        self.assertTrue(incident['resolved'])

    def test_generic_security_incident_is_resolved_as_bouncer_summoned(self):
        incident = {'name': 'bar_security_incident', 'category': 'disturbance', 'reason': 'unknown_disturbance', 'offender': None}
        result = self.protocol.handle_security_incident(incident)
        self.assertTrue(result)
        entry = self.incident_book.incidents[-1]
        self.assertTrue(entry['resolved'])
        self.assertEqual(entry['resolution'], 'bouncer_summoned')
        self.assertEqual(self.blacklist.denied_identities, [])
if __name__ == '__main__':
    unittest.main()
