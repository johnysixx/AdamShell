from core.entity.cronenberg import Cronenberg
from core.entity.existence import ExistenceResolver

class BarSecurityProtocol:

    def __init__(self, geometry, bar_counter, bartender, bouncer):
        self.geometry = geometry
        self.bar_counter = bar_counter
        self.bartender = bartender
        self.bouncer = bouncer
        self.last_confiscation = None
        self.last_security_roll = None
        self.last_security_outcome = None
        self.last_security_creation = None
        self.last_security_box = None
        self.last_energy_allocation = None
        self.last_creation_energy_j = None
        self.last_bar_dark_energy_j = None

    def interpret_security_roll(self, value):
        value = int(value)
        if value < 1 or value > 20:
            raise ValueError('Security D20 value must be between 1 and 20.')
        if value <= 10:
            return 'cronenberg'
        return 'cat'

    def split_confiscated_energy(self, energy_j):
        energy_j = float(energy_j)
        return {'entity_energy_j': energy_j * 0.25, 'multiverse_energy_j': energy_j * 0.5, 'bar_energy_j': energy_j * 0.25}

    def handle_bartender_red_button_press(self, reason):
        red_button = self.bar_counter.red_button
        if reason == 'cat_alarm_clear':
            red_button.clear_alarm()
            return True
        pressed = self.bartender.respond_to_red_button_alarm(red_button)
        if not pressed:
            return False
        self.bouncer.state = 'responding_inside_bar'
        self.bouncer.position = 'inside_bar'
        return True

    def handle_security_incident(self, incident, resolve_immediately=True):
        incident_book = getattr(self, 'incident_book', None)
        if incident_book is None:
            return False
        self.last_incident_entry = incident_book.record(incident)
        red_button = self.bar_counter.red_button
        red_button.activate_alarm()
        handled = self.handle_bartender_red_button_press(reason=incident.get('reason', 'generic_security_call'))
        if not handled:
            return False
        if resolve_immediately:
            incident_book.resolve(self.last_incident_entry, resolution='bouncer_summoned')
        return True

    def handle_guest_entry(self, guest, target):
        if guest is None or target is None:
            return False
        if target.kind != 'service_floor':
            return False
        guest_name = getattr(guest, 'world_key', None) or getattr(guest, 'name', None)
        incident = {'name': 'bar_security_incident', 'category': 'access_violation', 'reason': 'unauthorized_area', 'offender': guest_name}
        handled = self.handle_security_incident(incident, resolve_immediately=False)
        if not handled:
            return False
        ejected = self.bouncer.eject(guest)
        if not ejected:
            return False
        if isinstance(guest, dict):
            guest_name = getattr(guest, 'world_key', None) or getattr(guest, 'name', None)
            existence_pct = float(getattr(guest, 'existence_pct', 0.0))
            energy_j = float(getattr(guest, 'energy_j', 0.0))
            self.last_confiscation = {'guest': guest_name, 'existence_pct': existence_pct, 'energy_j': energy_j}
            existence_result = ExistenceResolver.remove_from_strongest_world(guest)
            guest.existence_pct = 0.0
            guest.exists_somewhere = ExistenceResolver.exists_anywhere(guest)
            guest.energy_j = 0.0
            if existence_result['world'] is not None:
                self.last_confiscation['existence_world'] = existence_result['world']
                self.last_confiscation['removed_existence_pct'] = existence_result['removed_existence_pct']
        else:
            guest_name = getattr(guest, 'name', None)
            existence_pct = float(getattr(guest, 'existence_pct', 0.0))
            energy_j = float(getattr(guest, 'energy_j', 0.0))
            self.last_confiscation = {'guest': guest_name, 'existence_pct': existence_pct, 'energy_j': energy_j}
            existence_result = ExistenceResolver.remove_from_strongest_world(guest)
            guest.existence_pct = 0.0
            guest.exists_somewhere = ExistenceResolver.exists_anywhere(guest)
            guest.energy_j = 0.0
            if existence_result['world'] is not None:
                self.last_confiscation['existence_world'] = existence_result['world']
                self.last_confiscation['removed_existence_pct'] = existence_result['removed_existence_pct']
        self.last_energy_allocation = self.split_confiscated_energy(energy_j)
        self.last_creation_energy_j = self.last_energy_allocation['entity_energy_j']
        universe = getattr(self, 'universe', None)
        if universe is not None:
            energy_pool = getattr(universe, 'energy_pool', None)
            multiverse_energy_j = self.last_energy_allocation['multiverse_energy_j']
            multiverse_dark_energy_j = multiverse_energy_j * 0.1
            multiverse_ordinary_energy_j = multiverse_energy_j - multiverse_dark_energy_j
            if isinstance(energy_pool, (int, float)):
                universe.energy_pool = float(energy_pool) + multiverse_ordinary_energy_j
            dark_sector = getattr(universe, 'dark_sector', None)
            if dark_sector is not None:
                dark_energy_j = getattr(dark_sector, 'dark_energy_j', None)
                if isinstance(dark_energy_j, (int, float)):
                    dark_sector.dark_energy_j = float(dark_energy_j) + multiverse_dark_energy_j
        bar_energy_j = self.last_energy_allocation['bar_energy_j']
        bar_dark_energy_j = bar_energy_j * 0.2
        bar_ordinary_energy_j = bar_energy_j - bar_dark_energy_j
        self.last_bar_dark_energy_j = bar_dark_energy_j
        bar_energy_reservoir = getattr(self, 'bar_energy_reservoir', None)
        if bar_energy_reservoir is not None:
            bar_energy_reservoir.add_energy(source='bar_security_confiscation', amount_j=bar_ordinary_energy_j)
        bottle_shelf = getattr(self, 'bottle_shelf', None)
        if bottle_shelf is not None:
            bottle_shelf.add_dark_energy(bar_dark_energy_j)
        cat_d20 = getattr(self, 'cat_d20', None)
        if cat_d20 is not None:
            roll = cat_d20.roll()
            if isinstance(roll, dict) and roll.get('turned'):
                self.last_security_roll = roll.get('value')
                self.last_security_outcome = self.interpret_security_roll(self.last_security_roll)
                if self.last_security_outcome == 'cat':
                    universe = getattr(self, 'universe', None)
                    if universe is not None:
                        box = universe.create_quantum_box()
                        self.last_security_box = box
                        box.resolve_state(result='cat', cause='bar_security', observer='bartender', tick=None)
                        universe.open_quantum_box(box.id, observer='bartender')
                    else:
                        cats = getattr(self, 'cats', None)
                        if cats is not None:
                            self.last_security_creation = cats.create_cat(name=f'security_cat_{guest_name}', color='black', fur_length='short', origin='bar_security_confiscation')
                elif self.last_security_outcome == 'cronenberg':
                    self.last_security_creation = Cronenberg(error=RuntimeError('bar_security_roll_failed'), source_component='bar_security_protocol', source_operation='security_d20_failure')
        incident_book = getattr(self, 'incident_book', None)
        last_incident_entry = getattr(self, 'last_incident_entry', None)
        if incident_book is not None and last_incident_entry is not None:
            incident_book.resolve(last_incident_entry, resolution='ejected_and_blacklisted')
        blacklist = getattr(self.bouncer, 'blacklist', None)
        if blacklist is not None and guest_name is not None:
            blacklist.ban(guest_name)
        return True
