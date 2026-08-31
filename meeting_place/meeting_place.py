import random
from cats.cat import Cat
from universe.logger import UniverseLogger
from .bartender import Bartender
from .how_to_mix_drinks import HowToMixDrinks
from .terminals import BarTerminals
from .bar_counter import BarCounter
from .bouncer import Bouncer
from .bar_blacklist import BarBlacklist
from .bar_incident_book import BarIncidentBook
from .dice_vial import DiceVial
from .dice_box import DiceBox
from .cat_d20_adapter import CatD20Adapter
from .fridge import BarFridge
from .reservoirs import BarEnergyReservoir, BarEntropyReservoir
from .service_rules import BarServiceRules
from .back_room import BackRoom
from .glass_shelf import GlassShelf
from .bottle_shelf import BottleShelf
from .bar_security_protocol import BarSecurityProtocol
from .bar_entity_policy import BarEntityPolicy
from .bar_geometry_terminal import BarGeometryTerminal
from .bar_hex_geometry import BarHexGeometry
from .back_room_black_box import BackRoomBlackBox
from .bar_clock import BarClock
from .bar_clock import BarClock
from .lemonade_reservoir import LemonadeReservoir
from .lemonade_signs import LemonadeSigns
from .bar_menu_sign import BarMenuSign
from cats.duplicate_consumption_energy import DuplicateConsumptionEnergy
from cats.kitten_growth import KittenGrowth
from universe.aroma_foundations import AromaFoundations

class MeetingPlace:
    BAR_HALF_YEAR_DAYS = 180

    def __init__(self, universe):
        self.universe = universe
        self.universe.meeting_place = self
        self.entities = []
        self.events = []
        self.bar_banned_humans = set()
        self.cat_guest_incidents = []
        self.guest_visit_history = {}
        self.regular_guests = set()
        self.back_room_black_box = BackRoomBlackBox()
        self.bar_clock = BarClock()
        self.cronenberg_area = {'state': 'lemon_courtyard', 'location': 'behind_bar', 'tree': True, 'tree_type': 'lemon_tree', 'lemons_visible': True, 'bench': True}
        self.cronenberg_lemonade_total = 0.0
        self.cronenberg_processing_count = 0
        self.cronenberg_processing_history = []
        self.tick_count = 0
        self.bar_counter = BarCounter()
        self.glass_shelf = GlassShelf()
        self.bottle_shelf = BottleShelf()
        self.bar_entity_policy = BarEntityPolicy()
        self.dice_vial = DiceVial()
        self.universe.d20_registry.register(self.dice_vial)
        self.dice_box = DiceBox()
        self.aroma_foundations = AromaFoundations(self.universe)
        self.raspberry_rum = self.aroma_foundations.get_mixture('raspberry_rum')
        self.drink_menu = {}
        self.new_drinks = {}
        self.bar_menu_sign = BarMenuSign(drink_menu=self.drink_menu, new_drinks=self.new_drinks)
        self.bar_counter.attach_menu_sign(self.bar_menu_sign)
        self.ambient_aroma = {'dominant_source': 'raspberry_rum', 'profile': dict(self.raspberry_rum['aroma_profile'])}
        self.fridge = BarFridge()
        self.energy_reservoir = BarEnergyReservoir()
        self.entropy_reservoir = BarEntropyReservoir()
        self.lemonade_reservoir = LemonadeReservoir()
        self.lemonade_signs = LemonadeSigns()
        self.terminals = BarTerminals()
        self.geometry_terminal = BarGeometryTerminal()
        self.bar_geometry = BarHexGeometry()
        self.bar_blacklist = BarBlacklist()
        self.bar_incident_book = BarIncidentBook(recorder=self.back_room_black_box, event_emitter=self.emit_event)
        self.bouncer = Bouncer(blacklist=self.bar_blacklist)
        self.service_rules = BarServiceRules()
        self.back_room = BackRoom(self.universe.universe_registry)
        self.total_entropy_served_today = 0
        self.total_entropy_served_ever = 0
        self.entropy_terminal = {'name': 'entropy_terminal', 'type': 'bar_terminal', 'total_entropy_served_today': self.total_entropy_served_today, 'total_entropy_served_ever': self.total_entropy_served_ever}
        self.how_to_mix_drinks = HowToMixDrinks()
        self.bartender = Bartender(self.bar_counter.hidden_story_book, mix_book=self.how_to_mix_drinks, on_cocktail_approved=self.add_approved_cocktail)
        self.refresh_bar_ingredients()
        self.bar_security_protocol = BarSecurityProtocol(geometry=self.bar_geometry, bar_counter=self.bar_counter, bartender=self.bartender, bouncer=self.bouncer)
        self.bar_security_protocol.universe = self.universe
        self.bar_security_protocol.bar_energy_reservoir = self.energy_reservoir
        self.bar_security_protocol.bottle_shelf = self.bottle_shelf
        self.bar_security_protocol.incident_book = self.bar_incident_book
        self.bar_security_protocol.incident_book = self.bar_incident_book
        self.duplicate_consumption_energy = DuplicateConsumptionEnergy(universe)
        self.kitten_growth = KittenGrowth(universe)
        self.access = {'from': ['eden', 'library', 'quantum_layer'], 'exit_to': ['library', 'quantum_layer'], 'root_universe': False}
        self.permissions = {'god': 'enter', 'serpent': 'enter', 'pazuzu': 'enter', 'classical_probe_debug_entity': 'enter'}
        self.state = {'type': 'meeting_layer', 'state': 'initialized', 'access': self.access, 'permissions': self.permissions, 'entities': self.entities, 'bar_counter': self.bar_counter.name, 'hidden_story_book': self.bar_counter.hidden_story_book.name, 'bar_cloth': self.bar_counter.bar_cloth, 'milk_bowl': self.bar_counter.milk_bowl, 'dice_vial': self.dice_vial.public_state, 'dice_box': self.dice_box.public_state, 'fridge': self.fridge.public_state, 'drink_menu': self.drink_menu, 'ambient_aroma': self.ambient_aroma, 'energy_reservoir': self.energy_reservoir.public_state, 'entropy_reservoir': self.entropy_reservoir.public_state, 'geometry_terminal': self.geometry_terminal.public_state, 'back_room': self.back_room.public_state, 'back_room_black_box': self.back_room_black_box.public_state, 'terminals': self.terminals.terminals, 'bouncer': self.bouncer.name, 'service_rules': 'bar_service_rules', 'entropy_terminal': self.entropy_terminal, 'bartender': self.bartender.name}
        self.universe.world['meeting_place'] = self.state
        UniverseLogger.boot('MEETING PLACE INITIALIZED')

    def can_enter(self, entity_name):
        return self.permissions.get(entity_name) == 'enter'

    def observe_lemon_courtyard(self, observer_role):
        staff_roles = {'bartender', 'bouncer', 'bar_staff'}
        pen = getattr(self, 'cronenberg_pen', None)
        public_view = {'name': 'lemon_courtyard', 'location': 'behind_bar', 'tree': True, 'tree_type': 'lemon_tree', 'lemons_visible': True, 'bench': True, 'assumed_lemonade_source': 'lemons_from_tree', 'cronenberg_pen_visible': False}
        if observer_role not in staff_roles:
            return public_view
        staff_view = dict(public_view)
        staff_view['cronenberg_pen_visible'] = pen is not None
        staff_view['cronenberg_pen'] = pen.get_status() if pen is not None else None
        staff_view['actual_lemonade_source'] = 'cronenberg_processing'
        return staff_view

    def create_cronenberg_pen_area(self):
        self.cronenberg_area = {'state': 'lemon_courtyard_with_hidden_pen', 'location': 'behind_bar', 'tree': True, 'bench': True}
        UniverseLogger.event('A HIDDEN CRONENBERG PEN IS CREATED BEHIND THE LEMON COURTYARD')

    def restore_cronenberg_clearing(self):
        if hasattr(self, 'cronenberg_pen'):
            del self.cronenberg_pen
        self.cronenberg_area = {'state': 'lemon_courtyard', 'location': 'behind_bar', 'tree': True, 'tree_type': 'lemon_tree', 'lemons_visible': True, 'bench': True}
        UniverseLogger.event('HIDDEN CRONENBERG PEN DISAPPEARS; LEMON COURTYARD REMAINS UNCHANGED')

    def record_guest_visit(self, guest_name):
        current_day = self.bar_clock.day
        visits = self.guest_visit_history.setdefault(guest_name, [])
        visits.append(current_day)
        cutoff_day = current_day - self.BAR_HALF_YEAR_DAYS
        recent_visits = [visit_day for visit_day in visits if visit_day >= cutoff_day]
        self.guest_visit_history[guest_name] = recent_visits
        if len(recent_visits) >= 5 and guest_name not in self.regular_guests:
            self.regular_guests.add(guest_name)
            self.bartender.regular_guests.add(guest_name)
            UniverseLogger.event(f'BAR REGULAR GUEST RECOGNIZED: {guest_name}')
        return len(recent_visits)

    def refresh_regular_guest_status(self, guest_name):
        if guest_name not in self.regular_guests:
            return False
        current_day = self.bar_clock.day
        year_cutoff = current_day - 360
        visits = self.guest_visit_history.get(guest_name, [])
        yearly_visits = [visit_day for visit_day in visits if visit_day >= year_cutoff]
        if len(yearly_visits) >= 2:
            return True
        self.regular_guests.discard(guest_name)
        self.bartender.regular_guests.discard(guest_name)
        UniverseLogger.event(f'BAR REGULAR GUEST STATUS LOST: {guest_name}')
        return False

    def is_regular_guest(self, guest_name):
        return guest_name in self.regular_guests

    def add_entity(self, entity):
        if isinstance(entity, dict):
            raise TypeError('MeetingPlace accepts object entities only.')
        entity_name = self._get_entity_name(entity)
        if entity_name in self.bar_banned_humans:
            UniverseLogger.event(f'MEETING PLACE ENTRY DENIED: {entity_name} IS BAR BANNED')
            return {'name': 'meeting_place_entry_denied', 'entity': entity_name, 'reason': 'bar_entry_banned', 'entered': False}
        if not self.bouncer.can_enter(entity):
            UniverseLogger.event(f'MEETING PLACE ENTRY DENIED BY BOUNCER: {entity_name}')
            entity_type = getattr(entity, 'type', None)
            if entity_type == 'cronenberg':
                if not hasattr(self, 'cronenberg_pen'):
                    from .cronenberg_pen import CronenbergPen
                    self.cronenberg_pen = CronenbergPen(self.universe)
                    self.create_cronenberg_pen_area()
                self.cronenberg_pen.add_cronenberg(entity)
                return
            react = getattr(entity, 'react', None)
            if callable(react):
                react(universe=self.universe, event='entry_denied', source='bouncer')
            return
        self.bartender.prepare_for_guest()
        self.entities.append(entity)
        entity.current_layer = 'meeting_place'
        entity.location = 'meeting_place'
        self.universe.world['meeting_place']['entities'] = self.entities
        UniverseLogger.event(f'MEETING PLACE: entity joined {entity_name}')
        self.emit_event(f'{entity_name} arrived at the bar')
        if self._is_cat(entity):
            self.universe.statistics.record_cat_arrived()
            self.geometry_terminal.cat_arrived(entity_name)
            if self.bartender.knows_guest(entity_name):
                self.bartender.guest_arrives(entity_name)
            else:
                self.handle_cat_after_entry(entity)
                self.bartender.remember_guest(entity)
        else:
            if not self.bartender.knows_guest(entity_name):
                self.bartender.remember_guest(entity)
            self.record_guest_visit(entity_name)
            self.bartender.guest_arrives(entity_name)

    def add_cat_invited_human(self, human, cat, invitation_system):
        human_name = self._get_entity_name(human)
        cat_name = self._get_entity_name(cat)
        if human_name in self.bar_banned_humans:
            return {'name': 'cat_invited_human_entry_denied', 'human': human_name, 'cat': cat_name, 'reason': 'bar_entry_banned', 'entered': False}
        if cat is None:
            return {'name': 'cat_invited_human_entry_denied', 'human': human_name, 'cat': None, 'reason': 'inviting_cat_not_present', 'entered': False}
        suspended_until = int(getattr(cat.meow_invitations, 'suspended_until_tick', 0))
        if self.tick_count < suspended_until:
            return {'name': 'cat_invited_human_entry_denied', 'human': human_name, 'cat': cat_name, 'reason': 'cat_MEOW_cooldown', 'entered': False}
        if getattr(cat.meow_invitations, 'garfield_training_required', False):
            return {'name': 'cat_invited_human_entry_denied', 'human': human_name, 'cat': cat_name, 'reason': 'garfield_training_required', 'entered': False}
        register = getattr(self.bouncer, 'register_meow_invitation_system', None)
        if callable(register):
            register(invitation_system)
        authorization = self.bouncer.can_enter_with_cat(human, cat)
        if not authorization.get('authorized', False):
            UniverseLogger.event(f"MEETING PLACE CAT INVITED ENTRY DENIED: {human_name} REASON={authorization.get('reason')}")
            return {'name': 'cat_invited_human_entry_denied', 'human': human_name, 'cat': cat_name, 'reason': authorization.get('reason'), 'entered': False}
        if cat not in self.entities:
            self.add_entity(cat)
        if cat not in self.entities:
            return {'name': 'cat_invited_human_entry_denied', 'human': human_name, 'cat': cat_name, 'reason': 'inviting_cat_failed_to_enter', 'entered': False}
        if human not in self.entities:
            self.bartender.prepare_for_guest()
            self.entities.append(human)
        human.current_layer = 'meeting_place'
        human.location = 'meeting_place'
        self.universe.world['meeting_place']['entities'] = self.entities
        if not hasattr(self, 'cat_invited_guests'):
            self.cat_invited_guests = {}
        record = {'human': human_name, 'inviting_cat': cat_name, 'invitation_id': authorization['invitation_id'], 'cat_present': True, 'entered_together': True, 'permanent_access': False}
        self.cat_invited_guests[human_name] = record
        UniverseLogger.event(f'MEETING PLACE: CAT INVITED GUEST {human_name} ARRIVED WITH {cat_name}')
        self.emit_event({'name': 'cat_invited_guest_arrived', **record})
        return {'name': 'cat_invited_human_entered', **record, 'entered': True}

    def record_cat_guest_incident(self, human, category, description=None, cooldown_ticks=24):
        human_name = self._get_entity_name(human)
        guest_record = getattr(self, 'cat_invited_guests', {}).get(human_name)
        if guest_record is None:
            return {'name': 'cat_guest_incident_not_attributed', 'human': human_name, 'category': category, 'cat_responsibility': False}
        inviting_cat_name = guest_record.get('inviting_cat')
        inviting_cat = None
        for entity in self.entities:
            if self._get_entity_name(entity) == inviting_cat_name and self._is_cat(entity):
                inviting_cat = entity
                break
        if inviting_cat is None:
            return {'name': 'cat_guest_incident_not_attributed', 'human': human_name, 'category': category, 'inviting_cat': inviting_cat_name, 'reason': 'inviting_cat_not_found', 'cat_responsibility': False}
        from cats.cat_guest_responsibility_system import CatGuestResponsibilitySystem
        responsibility = CatGuestResponsibilitySystem(self)
        event = responsibility.handle_incident(human=human, cat=inviting_cat, invitation_id=guest_record.get('invitation_id'), category=category, description=description, cooldown_ticks=cooldown_ticks)
        event.cat_responsibility = True
        self.cat_guest_incidents.append(event)
        self.emit_event(event)
        return event

    def complete_garfield_training(self, cat):
        from cats.garfield_training_system import GarfieldTrainingSystem
        return GarfieldTrainingSystem().complete(cat)

    def emit_event(self, event):
        self.events.append(event)
        if isinstance(event, dict):
            self.back_room_black_box.record(event=event.get('name', 'meeting_place_event'), data=event, source='meeting_place', tick=self.tick_count)
        else:
            self.back_room_black_box.record(event=event, source='meeting_place', tick=self.tick_count)
        self.bartender.observe_event(event)
        self.show_bar_story_count()
        UniverseLogger.event(f'MEETING PLACE EVENT: {event}')

    def guest_asks_about_dice_vial(self, guest_name):
        self.emit_event(f'{guest_name} asked about the dice vial')
        self.bartender.answer_about_dice_vial(guest_name)

    def admit_cat(self, cat, bartender_available=True):
        if not self._is_cat(cat):
            raise TypeError('admit_cat requires a cat.')
        cat_name = self._get_entity_name(cat)
        already_inside = any((entity is cat for entity in self.entities))
        if already_inside:
            return {'name': 'cat_arrival_already_completed', 'cat': cat_name, 'entered': True, 'already_inside': True}
        self.handle_cat_created(cat_name)
        red_button = self.bar_counter.red_button
        alarm_before = bool(red_button.alarm_active)
        bartender_responded = self.bartender.respond_to_red_button_alarm(red_button, available=bartender_available)
        alarm_after_bartender = bool(red_button.alarm_active)
        self.add_entity(cat)
        entered = any((entity is cat for entity in self.entities))
        return {'name': 'cat_arrival_completed', 'cat': cat_name, 'alarm_before_bartender': alarm_before, 'bartender_available': bool(bartender_available), 'bartender_responded': bool(bartender_responded), 'alarm_after_bartender': alarm_after_bartender, 'entered': entered, 'already_inside': False}

    def handle_cat_created(self, cat_id):
        self.geometry_terminal.cat_detected(cat_id)
        self.bar_counter.red_button.activate_alarm()

    def handle_cat_after_entry(self, cat):
        meow_exchange = self.bartender.exchange_meow_with_cat(cat)
        self.emit_event({'name': 'cat_bartender_meow_exchange', 'cat': self._get_entity_name(cat), 'cat_meow': meow_exchange['cat_meow'], 'bartender_meow': meow_exchange['bartender_meow'], 'tick': self.tick_count})
        return self.serve_cat_milk(cat)

    def serve_cat_milk(self, cat):
        cat_name = self._get_entity_name(cat)
        milk = self.fridge.get_item('milk')
        milk_bowl = self.bar_counter.milk_bowl
        if milk is None:
            event = {'name': 'cat_milk_service_failed', 'cat': cat_name, 'reason': 'milk_missing', 'served': False}
            self.emit_event(event)
            return event
        self.bartender.serve_without_order(cat_name, milk, milk_bowl)
        growth_event = None
        if getattr(cat, 'type', None) == 'cat' and hasattr(cat, 'age_days') and (getattr(cat, 'developmental_stage', None) != 'adult'):
            growth_event = self.kitten_growth.feed_cat_milk(kitten=cat, day=self.tick_count, amount=1.0, source='bartender')
        event = {'name': 'cat_drank_milk_at_bar', 'cat': cat_name, 'milk': 'milk', 'bowl': milk_bowl.get('name', 'milk_bowl'), 'growth': growth_event, 'served': True, 'tick': self.tick_count}
        self.emit_event(event)
        cat_distribution_system = getattr(self, 'cat_distribution_system', None)
        if cat_distribution_system is not None:
            event['distribution'] = cat_distribution_system.handle_after_milk(cat)
        return event

    def welcome_cat_d20(self, name='cat_d20'):
        existing = next((cat for cat in getattr(getattr(self.universe, 'cats_layer', None), 'cats', []) if getattr(cat, 'name', None) == name), None)
        if existing is not None:
            return {'name': 'cat_d20_already_present', 'cat': existing, 'box': getattr(self, 'cat_d20_box', None), 'created': False}
        manifestation = self.universe.manifest_cat(name=name, source='cat_d20_arrival', position={'x': 0.0, 'y': 0.0, 'z': 0.0}, color='black', fur_length='short', pattern='solid', eye_color='gold', sex='female')
        cat = manifestation['cat']
        if not hasattr(self, 'cat_d20_secret_history'):
            self.cat_d20_secret_history = []
        cat.special_traits.extend(['d20_cat', 'born_as_cat_d20', 'secret_probability_sense'])
        cat.state = 'arrived_at_bar'
        cat.current_layer = 'meeting_place'
        cat.cat_d20 = {'is_cat': True, 'is_die': False, 'sides': 20, 'roll_method': 'turns_herself_in_box', 'can_be_thrown': False, 'visibility': 'appears_to_be_a_small_cat'}
        self.cat_d20_adapter = CatD20Adapter(self)
        self.universe.d20_registry.register(self.cat_d20_adapter)
        self.admit_cat(cat, bartender_available=True)
        cat_box = self.place_cat_d20_box(cat)
        event = {'name': 'cat_d20_welcomed_at_bar', 'cat': cat.name, 'milk_served': self.bar_counter.milk_bowl.get('contains') == 'milk', 'box': cat_box['name'], 'box_location': cat_box['location'], 'cat_entered_box': True, 'tick': getattr(self.universe, 'universe_tick', 0)}
        self.emit_event(event)
        UniverseLogger.event('CAT D20 ARRIVED AS A CAT, DRANK MILK, AND ENTERED HER OWN BOX ON THE BAR')
        return {'name': 'cat_d20_arrival_completed', 'cat': cat, 'entity': manifestation['entity'], 'box': cat_box, 'event': event, 'created': True}

    def turn_cat_d20_in_box(self, rng=None):
        cats_layer = getattr(self.universe, 'cats_layer', None)
        if cats_layer is None:
            return {'name': 'cat_d20_turn_failed', 'result': 'cats_layer_missing', 'turned': False}
        cat = next((candidate for candidate in cats_layer.cats if 'd20_cat' in getattr(candidate, 'special_traits', [])), None)
        if cat is None:
            return {'name': 'cat_d20_turn_failed', 'result': 'cat_d20_missing', 'turned': False}
        box = getattr(self, 'cat_d20_box', None)
        if box is None:
            return {'name': 'cat_d20_turn_failed', 'result': 'cat_d20_box_missing', 'cat': cat.name, 'turned': False}
        if box.get('occupied_by') != cat.name:
            return {'name': 'cat_d20_turn_failed', 'result': 'cat_d20_not_in_box', 'cat': cat.name, 'turned': False}
        rng = rng or random
        value = int(rng.randint(1, 20))
        cat_d20_state = cat.cat_d20
        previous_value = cat_d20_state.get('current_value')
        turn_count = int(cat_d20_state.get('turn_count', 0)) + 1
        turn_event = {'name': 'cat_d20_turned_in_box', 'cat': cat.name, 'box': box['name'], 'previous_value': previous_value, 'value': value, 'turn_number': turn_count, 'turned_by': 'herself', 'was_thrown': False, 'visibility': 'secret_cat_event', 'tick': getattr(self.universe, 'universe_tick', 0), 'turned': True}
        cat_d20_state['current_value'] = value
        cat_d20_state['turn_count'] = turn_count
        cat_d20_state.setdefault('turn_history', []).append(dict(turn_event))
        cat.state = 'turned_in_cat_d20_box'
        box['last_cat_d20_value'] = value
        box['turn_count'] = turn_count
        if not hasattr(self, 'cat_d20_secret_history'):
            self.cat_d20_secret_history = []
        self.cat_d20_secret_history.append(dict(turn_event))
        self.universe.quantum_events.append(dict(turn_event))
        UniverseLogger.event('CAT D20 SECRET ROTATION RECORDED')
        interpretation = self.interpret_cat_d20_value(value)
        turn_event['interpretation'] = interpretation
        energy_resolution = self.duplicate_consumption_energy.resolve_next(cat_d20_value=value)
        turn_event['duplicate_consumption_energy'] = energy_resolution
        return turn_event

    def cat_d20_prepare_pazuzu_profile(self):
        cats_layer = getattr(self.universe, 'cats_layer', None)
        if cats_layer is None:
            return {'name': 'cat_d20_pazuzu_profile_failed', 'result': 'cats_layer_missing', 'prepared': False}
        cat_d20 = next((cat for cat in cats_layer.cats if 'd20_cat' in getattr(cat, 'special_traits', [])), None)
        if cat_d20 is None:
            return {'name': 'cat_d20_pazuzu_profile_failed', 'result': 'cat_d20_missing', 'prepared': False}
        base_profile = {'color': 'black', 'fur_length': 'short', 'pattern': 'solid', 'eye_color': 'green', 'sex': 'female'}
        if not hasattr(self, 'cat_d20_canonical_profile_counts'):
            self.cat_d20_canonical_profile_counts = {}
        profile_key = (base_profile['color'], base_profile['fur_length'], base_profile['pattern'], base_profile['eye_color'], base_profile['sex'])
        occurrence = self.cat_d20_canonical_profile_counts.get(profile_key, 0) + 1
        self.cat_d20_canonical_profile_counts[profile_key] = occurrence
        if occurrence == 1:
            target_name = 'pazuzu'
            profile = dict(base_profile)
            all_dice_rotation_requested = False
        elif occurrence == 2:
            target_name = 'gib'
            profile = dict(base_profile)
            profile['fur_length'] = 'long'
            all_dice_rotation_requested = True
        else:
            target_name = None
            profile = dict(base_profile)
            all_dice_rotation_requested = False
        event = {'name': 'cat_d20_prepared_canonical_pazuzu_profile', 'cat': cat_d20.name, 'profile': dict(profile), 'base_profile': dict(base_profile), 'profile_occurrence': occurrence, 'target_name': target_name, 'all_dice_rotation_requested': all_dice_rotation_requested, 'mode': 'canonical_turn', 'random': False, 'prepared': target_name is not None, 'visibility': 'secret_cat_event', 'tick': getattr(self.universe, 'universe_tick', 0)}
        cat_d20.cat_d20['canonical_target'] = target_name
        cat_d20.cat_d20['canonical_profile'] = dict(profile)
        if not hasattr(self, 'cat_d20_secret_history'):
            self.cat_d20_secret_history = []
        self.cat_d20_secret_history.append(dict(event))
        self.universe.quantum_events.append(dict(event))
        UniverseLogger.event('CAT D20 CANONICAL ROTATION FOR PAZUZU RECORDED')
        return event

    def manifest_gib_from_cat_d20(self, prepared_event):
        if not isinstance(prepared_event, dict):
            return {'name': 'gib_manifestation_failed', 'result': 'invalid_prepared_event', 'created': False}
        if prepared_event.get('target_name') != 'gib':
            return {'name': 'gib_manifestation_failed', 'result': 'prepared_target_is_not_gib', 'created': False}
        if prepared_event.get('profile_occurrence') != 2:
            return {'name': 'gib_manifestation_failed', 'result': 'invalid_profile_occurrence', 'created': False}
        profile = dict(prepared_event.get('profile', {}))
        required_fields = {'color', 'fur_length', 'pattern', 'eye_color', 'sex'}
        if not required_fields.issubset(profile):
            return {'name': 'gib_manifestation_failed', 'result': 'incomplete_gib_profile', 'created': False}
        cats_layer = getattr(self.universe, 'cats_layer', None)
        existing = next((cat for cat in (cats_layer.cats if cats_layer is not None else []) if getattr(cat, 'name', None) == 'gib'), None)
        if existing is not None:
            return {'name': 'gib_already_exists', 'cat': existing, 'created': False}
        manifestation = self.universe.manifest_cat(name='gib', source='cat_d20_second_canonical_profile', color=profile['color'], fur_length=profile['fur_length'], pattern=profile['pattern'], eye_color=profile['eye_color'], sex=profile['sex'])
        if manifestation is None:
            return {'name': 'gib_manifestation_failed', 'result': 'manifest_cat_failed', 'created': False}
        gib = manifestation['cat']
        gib.special_traits.extend(['gib', 'pazuzu_profile_echo', 'second_canonical_cat'])
        gib.canonical_origin = {'base_profile': dict(prepared_event['base_profile']), 'mutation': {'fur_length': {'from': 'short', 'to': 'long'}}, 'profile_occurrence': 2, 'created_by': 'cat_d20'}
        event = {'name': 'gib_manifested', 'cat': gib.name, 'profile': dict(profile), 'profile_occurrence': 2, 'all_dice_rotation_requested': prepared_event.get('all_dice_rotation_requested', False), 'created': True, 'visibility': 'secret_cat_event', 'tick': getattr(self.universe, 'universe_tick', 0)}
        if not hasattr(self, 'cat_d20_secret_history'):
            self.cat_d20_secret_history = []
        self.cat_d20_secret_history.append(dict(event))
        self.universe.quantum_events.append(dict(event))
        UniverseLogger.event('GIB MANIFESTED FROM THE SECOND CANONICAL CAT D20 PROFILE')
        return {**event, 'cat': gib, 'entity': manifestation['entity']}

    def trigger_pazuzu_birth_dice_resonance(self, rng=None):
        existing_event = getattr(self, 'pazuzu_birth_dice_resonance_event', None)
        if existing_event is not None:
            return {**existing_event, 'already_triggered': True}
        cats_layer = getattr(self.universe, 'cats_layer', None)
        cat_d20 = next((cat for cat in (cats_layer.cats if cats_layer is not None else []) if 'd20_cat' in getattr(cat, 'special_traits', [])), None)
        if cat_d20 is None:
            return {'name': 'pazuzu_birth_dice_resonance_failed', 'result': 'cat_d20_missing', 'triggered': False}
        quantum_d20_result = self.universe.quantum_die.roll(rng=rng)
        cat_d20_result = self.turn_cat_d20_in_box(rng=rng)
        dice_vial_result = self.dice_vial.roll(rng=rng)
        dice_box_result = self.dice_box.rotate_random_die(rng=rng)
        event = {'name': 'pazuzu_birth_dice_resonance', 'quantum_d20': quantum_d20_result, 'cat_d20': cat_d20_result, 'dice_vial': dice_vial_result, 'dice_box': dice_box_result, 'triggered': True, 'visibility': 'secret_multiverse_event', 'tick': getattr(self.universe, 'universe_tick', 0)}
        if not hasattr(self, 'cat_d20_secret_history'):
            self.cat_d20_secret_history = []
        self.cat_d20_secret_history.append(dict(event))
        self.universe.quantum_events.append(dict(event))
        self.pazuzu_birth_dice_resonance_event = dict(event)
        UniverseLogger.event('PAZUZU BIRTH DICE RESONANCE RECORDED')
        return event

    def interpret_cat_d20_value(self, value):
        value = int(value)
        if value < 1 or value > 20:
            raise ValueError('CatD20 value must be between 1 and 20.')
        if value <= 14:
            meaning = 'accept_navigation_offer'
        elif value <= 18:
            meaning = 'decline_navigation_offer'
        elif value == 19:
            meaning = 'cat_does_something_else'
        else:
            meaning = 'cat_d20_surge'
        return {'name': 'cat_d20_value_interpreted', 'value': value, 'meaning': meaning}

    def place_cat_d20_box(self, cat):
        if not isinstance(cat, (Cat, dict)):
            raise TypeError('Cat D20 box requires a cat.')
        if 'd20_cat' not in getattr(cat, 'special_traits', []):
            raise ValueError('This box is reserved for Cat D20.')
        existing_box = getattr(self, 'cat_d20_box', None)
        if existing_box is not None:
            existing_box['occupied_by'] = cat.name
            cat.cat_d20_box = existing_box
            return existing_box
        self.cat_d20_box = {'name': 'cat_d20_box', 'type': 'cat_box', 'location': 'on_bar_counter', 'state': 'occupied', 'material': 'wood', 'size': 'kitten_sized', 'purpose': 'safe_place_for_cat_d20_to_sleep_and_turn', 'occupied_by': cat.name, 'access': {'cats': True, 'bartender': 'may_place_and_clean', 'guests': 'look_but_do_not_touch'}, 'throwable': False}
        cat.cat_d20_box = self.cat_d20_box
        cat.state = 'resting_in_cat_d20_box'
        self.universe.world['meeting_place']['cat_d20_box'] = self.cat_d20_box
        UniverseLogger.event('BARTENDER PLACES A SMALL WOODEN BOX ON THE BAR FOR CAT D20')
        UniverseLogger.event('CAT D20 ENTERS HER BOX')
        return self.cat_d20_box

    def sync_entropy_terminal_to_world(self):
        self.entropy_terminal['total_entropy_served_today'] = self.total_entropy_served_today
        self.entropy_terminal['total_entropy_served_ever'] = self.total_entropy_served_ever
        self.universe.world['meeting_place']['entropy_terminal'] = self.entropy_terminal

    def sync_reservoirs_to_world(self):
        self.universe.world['meeting_place']['energy_reservoir'] = self.energy_reservoir.public_state
        self.universe.world['meeting_place']['entropy_reservoir'] = self.entropy_reservoir.public_state

    def add_bar_energy(self, source, amount_j):
        event = self.energy_reservoir.add_energy(source, amount_j)
        self.sync_reservoirs_to_world()
        self.emit_event(f'bar energy increased from {source}')
        return event

    def add_bar_entropy(self, source, amount_units):
        event = self.entropy_reservoir.add_entropy(source, amount_units)
        self.sync_reservoirs_to_world()
        self.emit_event(f'bar entropy increased from {source}')
        return event

    def serve_lemonade(self, entity, location=None):
        entity_name = self._get_entity_name(entity)
        if location is None:
            location = getattr(entity, 'location', 'outside_bar')
        event = self.lemonade_reservoir.serve(drinker_name=entity_name, location=location)
        if event is None:
            return None
        self.dice_vial.roll()
        self.lemonade_signs.sync_with_reservoir(self.lemonade_reservoir)
        self.emit_event(f'{entity_name} drinks free lemonade at {location}')
        return {'lemonade_event': event}

    def serve_energy(self, entity):
        from universe.pre_cosmic_rules import ENERGY_SERVING_J
        entity_name = self._get_entity_name(entity)
        entity_type = self._get_entity_type(entity)
        if entity_type not in ['god', 'idea_entity']:
            self.emit_event(f'{entity_name} could not be served energy')
            return None
        try:
            reservoir_event = self.energy_reservoir.spend_energy(f'energy_serving_for_{entity_name}', ENERGY_SERVING_J)
        except ValueError:
            self.sync_reservoirs_to_world()
            self.emit_event(f'{entity_name} could not be served energy because bar energy was missing')
            return None
        service_effect = self.service_rules.apply_energy_drink(entity)
        self.sync_reservoirs_to_world()
        self.emit_event(f'{entity_name} drinks energy at the bar')
        self.emit_event(f'{entity_name} energy drink effect applied')
        return {'reservoir_event': reservoir_event, 'service_effect': service_effect}

    def quantum_entropy_tick(self, rng=None):
        event = self.entropy_reservoir.quantum_tick(rng)
        self.sync_reservoirs_to_world()
        self.emit_event('quantum entropy tick was stored in the bar')
        return event

    def serve_entropy(self, entity):
        entity_name = self._get_entity_name(entity)
        entity_type = self._get_entity_type(entity)
        if entity_type not in ['god', 'idea_entity']:
            self.emit_event(f'{entity_name} could not be served entropy')
            return None
        event = self.entropy_reservoir.serve_entropy(self.energy_reservoir, entity_name)
        self.sync_reservoirs_to_world()
        if event is None:
            self.emit_event(f'{entity_name} could not be served entropy')
            return None
        self.total_entropy_served_today += 1
        self.total_entropy_served_ever += 1
        self.sync_entropy_terminal_to_world()
        if self.total_entropy_served_ever % 10 == 0:
            secret_event = self.dice_vial.roll()
            if secret_event['quantum_tick_requested']:
                self.quantum_entropy_tick()
            if secret_event['box_created']:
                self.universe.create_quantum_box()
        effect = self.service_rules.apply_entropy_drink(entity, event.get('entity_energy_gain_j', 0.0))
        self.emit_event(f'{entity_name} drinks entropy at the bar')
        self.emit_event(f'{entity_name} entropy drink effect applied')
        return {'reservoir_event': event, 'service_effect': effect}

    def refresh_bar_ingredients(self):
        if 'sugar' not in self.back_room.bar_ingredients:
            self.back_room.bar_ingredients['sugar'] = {'available': True, 'fundamental': True, 'serve_directly': False, 'shots': 200, 'unit': 'cube'}
        if getattr(self.universe, 'liquid_hydrocarbons', False):
            self.back_room.bar_ingredients['liquid_hydrocarbons'] = {'available': True, 'fundamental': False, 'shots': 200}
        self.refresh_basic_drinks()
        return self.back_room.bar_ingredients

    def add_approved_cocktail(self, recipe):
        if not isinstance(recipe, dict):
            raise ValueError('Approved cocktail requires recipe.')
        if recipe.get('status') != 'approved' or not recipe.get('approved', False):
            raise ValueError('Cocktail is not approved.')
        drink_name = recipe.get('name')
        if not drink_name:
            raise ValueError('Approved cocktail requires name.')
        recipe['menu_added_day'] = self.bar_clock.day
        self.new_drinks[drink_name] = recipe
        self.bartender.chronicle_memory.append({'kind': 'new_menu_drink', 'drink': drink_name})
        UniverseLogger.event(f'BAR NEW DRINK ADDED: {drink_name}')
        return recipe

    def serve_basic_drinks_on_tab(self, entity, drink_names):
        self.refresh_basic_drinks()
        drink_names = list(drink_names)
        if not drink_names:
            raise ValueError('At least one drink is required.')
        drinks = []
        for drink_name in drink_names:
            menu_item = self.drink_menu.get(drink_name)
            if menu_item is None:
                raise ValueError(f'Drink is not currently available: {drink_name}')
            stock = self.back_room.bar_ingredients.get(drink_name)
            if stock is None:
                raise ValueError(f'Basic drink is not present in bar stock: {drink_name}')
            if stock.get('category') != 'basic_drink':
                raise ValueError(f'Drink is not a basic drink: {drink_name}')
            if not stock.get('available', False):
                raise ValueError(f'Basic drink is unavailable: {drink_name}')
            drink = {'name': drink_name, 'type': 'basic_bar_drink', 'category': 'basic_drink'}
            drinks.append(drink)
            self.bar_counter.cash_register.add_to_tab(entity=entity, drink=drink)
        receipt = self.bar_counter.cash_register.print_open_tab_receipt(entity)
        entity_name = self._get_entity_name(entity)
        event = {'name': 'bar_order_served_on_open_tab', 'guest': entity_name, 'drinks': [drink['name'] for drink in drinks], 'receipt_number': receipt['receipt_number'], 'paid': False}
        self.emit_event(event)
        return {'drinks': drinks, 'receipt': receipt, 'payment': None, 'tab_status': 'open'}

    def serve_basic_drink(self, entity, drink_name):
        self.refresh_basic_drinks()
        menu_item = self.drink_menu.get(drink_name)
        if menu_item is None:
            raise ValueError('Drink is not currently available.')
        stock = self.back_room.bar_ingredients.get(drink_name)
        if stock is None:
            raise ValueError('Basic drink is not present in bar stock.')
        if stock.get('category') != 'basic_drink':
            raise ValueError('Drink is not a basic drink.')
        if not stock.get('available', False):
            raise ValueError('Basic drink is currently unavailable.')
        payment = self.service_rules.apply_basic_drink_payment(entity)
        if payment.get('payment_kind') == 'unsupported':
            raise ValueError('Entity type cannot pay for a basic drink.')
        bar_energy_j = float(payment.get('bar_energy_j', 0.0))
        if bar_energy_j > 0.0:
            entity_name = self._get_entity_name(entity)
            self.add_bar_energy(source=f'basic_drink_payment:{entity_name}:{drink_name}', amount_j=bar_energy_j)
        drink = {'name': drink_name, 'type': 'basic_bar_drink', 'category': 'basic_drink'}
        entity_name = self._get_entity_name(entity)
        receipt = self.bar_counter.cash_register.print_receipt(entity=entity, drink=drink, payment=payment)
        self.emit_event(f'{entity_name} drinks {drink_name}')
        return {'drink': drink, 'payment': payment, 'receipt': receipt}

    def mix_basic_drink(self, drink_name):
        recipe = self.how_to_mix_drinks.recipes.get(drink_name)
        if recipe is None:
            raise ValueError('Unknown basic drink recipe.')
        ingredients = self.back_room.bar_ingredients
        for ingredient_name, requirement in recipe['ingredients'].items():
            if ingredient_name not in ingredients:
                raise ValueError('Missing drink ingredient.')
            stock = ingredients[ingredient_name]
            required_shots = requirement.get('shots', 0)
            if requirement.get('consumed', False) and stock.get('shots', 0) < required_shots:
                return self.universe.create_cronenberg_from_quantum_error(error=RuntimeError('Bar ingredient depleted.'), source_component='meeting_place', source_operation='mix_basic_drink')
        for ingredient_name, requirement in recipe['ingredients'].items():
            if not requirement.get('consumed', False):
                continue
            self.back_room.bar_ingredients[ingredient_name]['shots'] -= requirement['shots']
        return {'name': drink_name, 'type': 'mixed_bar_drink'}

    def refresh_basic_drinks(self):
        ingredients = self.back_room.bar_ingredients
        for drink_name in list(self.drink_menu.keys()):
            drink = self.drink_menu[drink_name]
            if drink.get('menu_source') in {'direct_stock', 'basic_recipe'}:
                del self.drink_menu[drink_name]
        for ingredient_name, stock in ingredients.items():
            if not stock.get('available', False):
                continue
            if not stock.get('serve_directly', False):
                continue
            self.drink_menu[ingredient_name] = {'name': ingredient_name, 'type': 'bar_drink', 'menu_source': 'direct_stock'}
        for drink_name, recipe in self.how_to_mix_drinks.recipes.items():
            if recipe.get('hidden', False):
                continue
            if not recipe.get('learned', True):
                continue
            can_serve = True
            for ingredient_name, requirement in recipe['ingredients'].items():
                stock = ingredients.get(ingredient_name)
                if stock is None:
                    can_serve = False
                    break
                if not stock.get('available', True):
                    can_serve = False
                    break
                if requirement.get('consumed', False):
                    required_shots = requirement.get('shots', 0)
                    if stock.get('shots', 0) < required_shots:
                        can_serve = False
                        break
            if can_serve:
                menu_item = dict(recipe)
                menu_item['menu_source'] = 'basic_recipe'
                self.drink_menu[drink_name] = menu_item
        return self.drink_menu

    def refresh_new_drinks(self):
        current_day = self.bar_clock.day
        to_promote = []
        for drink_name, recipe in self.new_drinks.items():
            added_day = recipe.get('menu_added_day')
            if added_day is None:
                continue
            if current_day - added_day >= 90:
                to_promote.append(drink_name)
        for drink_name in to_promote:
            self.promote_new_drink(drink_name)

    def promote_new_drink(self, drink_name):
        if drink_name not in self.new_drinks:
            raise ValueError('Unknown new drink.')
        recipe = self.new_drinks.pop(drink_name)
        self.drink_menu[drink_name] = recipe
        self.bartender.chronicle_memory.append({'kind': 'drink_promoted', 'drink': drink_name})
        UniverseLogger.event(f'BAR DRINK PROMOTED: {drink_name}')
        return recipe

    def remove_drink(self, drink_name):
        if drink_name not in self.drink_menu:
            return False
        self.drink_menu.pop(drink_name)
        UniverseLogger.event(f'BAR DRINK REMOVED: {drink_name}')
        return True

    def add_drink(self, drink, source='bar'):
        if isinstance(drink, dict):
            drink_name = drink.get('name')
        else:
            drink_name = getattr(drink, 'name', None)
        if not drink_name:
            raise ValueError('Bar drink requires name.')
        self.drink_menu[drink_name] = drink
        self.bartender.note_new_drink(drink=drink_name, source=source)
        UniverseLogger.event(f'BAR DRINK ADDED: {drink_name}')
        return drink

    def tick(self):
        self.tick_count += 1
        self.bar_clock.tick()
        if self.bar_clock.hour == 0:
            self.refresh_new_drinks()
        self.bar_menu_sign.advance_minutes(60)
        if self.bar_clock.hour == 0:
            self.bartender.end_shift(bar_day=self.bar_clock.day, shift_start_tick=self.bar_clock.tick_count - 24, shift_end_tick=self.bar_clock.tick_count)
        UniverseLogger.event(f'MEETING PLACE TICK {self.tick_count}')
        self.bartender.idle_work()
        cronenberg_pen = getattr(self, 'cronenberg_pen', None)
        if cronenberg_pen is not None:
            cronenberg_pen.tick()
        self._clear_events()

    def show_library_book_count(self, library):
        return self.terminals.show_book_count(library)

    def show_book_search_terminal(self):
        return self.terminals.show_book_search_placeholder()

    def show_random_library_excerpt(self, library):
        return self.terminals.show_random_excerpt(library)

    def show_bar_story_count(self):
        return self.terminals.show_bar_story_count(self.bar_counter)

    def show_cronenberg_pen_terminal(self):
        return self.back_room.cronenberg_pen_terminal.display(self)

    def _clear_events(self):
        self.events = []

    def ask_bartender_about_dice_box(self, entity=None):
        return self.dice_box.answer_about_contents()

    def ask_bartender_about_d20(self, entity=None):
        return self.dice_box.answer_about_d20()

    def _get_entity_name(self, entity):
        return getattr(
            entity,
            'name',
            None
        )

    def _get_entity_type(self, entity):
        return getattr(
            entity,
            'type',
            None
        )

    def _is_cat(self, entity):
        return (
            getattr(
                entity,
                'type',
                None
            )
            == 'cat'
        )

    def process_interactions(self):
        if len(self.entities) < 2:
            return
        energy_entities = [entity for entity in self.entities if hasattr(entity, 'energy')]
        if len(energy_entities) < 2:
            return
        sorted_entities = sorted(energy_entities, key=lambda entity: entity.energy, reverse=True)
        a = sorted_entities[0]
        b = sorted_entities[-1]
        transfer = 0.5
        a.energy -= transfer
        b.energy += transfer
        self.emit_event(f'{a.name} -> {b.name} energy transfer {transfer}')
