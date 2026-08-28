from core.entity.social_entity import SocialMixin
from universe.logger import UniverseLogger

class Bartender(SocialMixin):

    def __init__(self, story_book, name='bartender', mix_book=None, on_cocktail_approved=None):
        self.name = name
        self.type = 'bar_observer'
        self.state = 'present'
        self.story_book = story_book
        self.mix_book = mix_book
        self.on_cocktail_approved = on_cocktail_approved
        self.current_location = 'meeting_place'
        self.origin = {'layer': 'meeting_place', 'event': 'bartender was born in the bar'}
        self.event_memory = []
        self.chronicle_memory = []
        self.regular_drinks = {}
        self.known_histories = {}
        self.known_guests = set()
        self.regular_guests = set()
        self.cat_meow_history = []
        self.current_task = 'wiping_glasses'
        self.glasses_clean = False
        self.bar_counter_clean = False
        UniverseLogger.boot('BARTENDER CREATED')

    def answer_about_lemonade_origin(self):
        answer = 'When life gives you lemons, make lemonade.'
        UniverseLogger.event(f'BARTENDER ANSWERS ABOUT LEMONADE: {answer}')
        return answer

    def respond_to_red_button_alarm(self, red_button, available=True):
        if not red_button.alarm_active:
            UniverseLogger.event('BARTENDER HEARS NO RED BUTTON ALARM')
            return False
        if not available:
            UniverseLogger.event('BARTENDER DOES NOT RESPOND TO RED BUTTON ALARM')
            return False
        UniverseLogger.event('BARTENDER RESPONDS TO RED BUTTON ALARM')
        return red_button.press()

    def observe_event(self, event):
        self.event_memory.append(event)
        UniverseLogger.event(f'BARTENDER OBSERVED EVENT: {event}')

    def begin_shift(self, bar_day=0, shift_start_tick=0):
        if getattr(self, 'shift_active', False):
            return {'name': 'bartender_shift_already_active', 'bar_day': self.current_shift['bar_day'], 'shift_start_tick': self.current_shift['shift_start_tick']}
        self.shift_active = True
        self.current_shift = {'bar_day': bar_day, 'shift_start_tick': shift_start_tick, 'state': 'active'}
        event = {'name': 'bartender_shift_started', 'bar_day': bar_day, 'shift_start_tick': shift_start_tick}
        self.observe_event(event)
        UniverseLogger.event('BARTENDER FIRST SHIFT STARTED')
        return event

    def refuse_bet(self, guest_name):
        event = {'name': 'bartender_refused_bet', 'guest': guest_name, 'accepted': False}
        self.observe_event(event)
        UniverseLogger.event(f'BARTENDER REFUSES BET FROM {guest_name}')
        return event

    def learn_requested_drink(self, guest_name, drink_name):
        self.remember_first_order(guest_name, drink_name)
        event = {'name': 'bartender_learned_requested_drink', 'guest': guest_name, 'drink': drink_name}
        self.observe_event(event)
        return event

    def leave_for_lemon(self, guest_name):
        self.current_location = 'bar_yard'
        event = {'name': 'bartender_left_for_lemon', 'guest': guest_name, 'destination': 'bar_yard', 'reason': 'fetch_lemon'}
        self.observe_event(event)
        UniverseLogger.event('BARTENDER LEAVES BAR FOR A LEMON')
        return event

    def return_with_lemon(self, guest_name):
        self.current_location = 'bar'
        event = {'name': 'bartender_returned_with_lemon', 'guest': guest_name, 'source': 'bar_yard', 'ingredient': 'lemon'}
        self.observe_event(event)
        UniverseLogger.event('BARTENDER RETURNS WITH LEMON')
        return event

    def learn_guest_drink(self, drink_name, teacher, ingredients, effects=None, price_basis=None):
        effects = dict(effects or {})
        entry = {'kind': 'learned_cocktail', 'drink': drink_name, 'teacher': teacher, 'ingredients': list(ingredients), 'effects': effects, 'price_basis': price_basis}
        self.chronicle_memory.append(entry)
        UniverseLogger.event(f'BARTENDER LEARNED DRINK: {drink_name} FROM {teacher}')
        return entry

    def end_shift(self, bar_day=None, shift_start_tick=None, shift_end_tick=None):
        observed_events = []
        for event in self.event_memory:
            if isinstance(event, dict) and event.get('name') == 'bar_security_incident' and (event.get('resolution') == 'ejected_and_blacklisted'):
                observed = {'kind': 'ejection', 'subject': event.get('offender'), 'observed_reason': event.get('reason'), 'observed_outcome': 'ejected'}
            else:
                observed = {'kind': 'ordinary', 'observed_event': event}
            observed_events.append(observed)
        observed_events.extend(self.chronicle_memory)
        shift_entries = []
        if observed_events:
            chronicle = {'type': 'bartender_shift_chronicle', 'observer': self.name, 'perspective': 'subjective', 'bar_day': bar_day, 'shift_start_tick': shift_start_tick, 'shift_end_tick': shift_end_tick, 'events': observed_events}
            self.story_book.write_entry(chronicle)
            shift_entries.append(chronicle)
        self.event_memory = []
        self.chronicle_memory = []
        UniverseLogger.event('BARTENDER SHIFT ENDED')
        return shift_entries

    def learn_cocktail(self, drink, teacher, ingredients):
        entry = {'kind': 'learned_cocktail', 'drink': drink, 'teacher': teacher, 'ingredients': list(ingredients)}
        self.chronicle_memory.append(entry)
        UniverseLogger.event(f'BARTENDER LEARNED COCKTAIL: {drink} FROM {teacher}')
        return entry

    def create_cocktail(self, drink, ingredients):
        if self.mix_book is not None:
            recipe = self.mix_book.add_created_recipe(name=drink, ingredients=ingredients)
        else:
            recipe = {'name': drink, 'origin': 'created_by_bartender', 'status': 'testing', 'ingredients': list(ingredients), 'tastings': [], 'votes_for': 0, 'votes_against': 0, 'approved': False}
        event = {'kind': 'created_cocktail', 'drink': drink}
        self.chronicle_memory.append(event)
        UniverseLogger.event(f'BARTENDER CREATED COCKTAIL: {drink}')
        return recipe

    def note_new_drink(self, drink, source):
        entry = {'kind': 'new_drink', 'drink': drink, 'source': source}
        self.chronicle_memory.append(entry)
        UniverseLogger.event(f'BARTENDER NOTED NEW DRINK: {drink} FROM {source}')
        return entry

    def note_interesting_guest(self, guest, reason):
        entry = {'kind': 'interesting_guest', 'guest': guest, 'reason': reason}
        self.chronicle_memory.append(entry)
        UniverseLogger.event(f'BARTENDER NOTED INTERESTING GUEST: {guest} BECAUSE {reason}')
        return entry

    def offer_cocktail_tasting(self, guest, drink):
        if guest not in self.regular_guests:
            return False
        if self.mix_book is None:
            return False
        recipe = self.mix_book.recipes.get(drink)
        if recipe is None:
            return False
        if recipe.get('status') != 'testing':
            return False
        UniverseLogger.event(f'BARTENDER OFFERS COCKTAIL TASTING: {drink} TO {guest}')
        return True

    def record_cocktail_tasting(self, guest, drink, liked, comment=None):
        if guest not in self.regular_guests:
            raise ValueError('Cocktail tasting requires regular guest.')
        if self.mix_book is None:
            raise ValueError('Bartender has no mix book.')
        recipe = self.mix_book.recipes.get(drink)
        if recipe is None:
            raise ValueError('Unknown cocktail recipe.')
        if recipe.get('status') != 'testing':
            raise ValueError('Cocktail is not in testing.')
        tasting = self.mix_book.record_tasting(drink=drink, guest=guest, liked=liked, comment=comment)
        recipe = self.mix_book.recipes[drink]
        if len(recipe['tastings']) == 5:
            if recipe['status'] == 'approved':
                result_event = {'kind': 'cocktail_approved', 'drink': drink, 'votes_for': recipe['votes_for'], 'votes_against': recipe['votes_against']}
                if self.on_cocktail_approved is not None:
                    self.on_cocktail_approved(recipe)
            else:
                result_event = {'kind': 'cocktail_rejected', 'drink': drink, 'votes_for': recipe['votes_for'], 'votes_against': recipe['votes_against']}
            self.chronicle_memory.append(result_event)
        UniverseLogger.event(f'BARTENDER RECORDS COCKTAIL TASTING: {drink} BY {guest}')
        return tasting

    def knows_guest(self, guest_name):
        return guest_name in self.known_guests

    def remember_guest(self, guest):
        guest_name = (
            getattr(guest, 'world_key', None)
            or getattr(guest, 'name', None)
        )
        life_history = getattr(
            guest,
            'life_history',
            None
        )
        if not guest_name:
            raise ValueError('Guest requires identity.')
        self.known_guests.add(guest_name)
        if life_history is not None:
            self.known_histories[guest_name] = life_history
        UniverseLogger.event(f'BARTENDER REMEMBERED GUEST: {guest_name}')
        return guest_name

    def guest_arrives(self, guest_name):
        if self.knows_drink(guest_name):
            drink = self.regular_drinks[guest_name]
            UniverseLogger.event(f'BARTENDER ASKS: {guest_name}, do you want your usual {drink}?')
            return
        UniverseLogger.event(f'BARTENDER ASKS: {guest_name}, what would you like to drink?')

    def answer_about_dice_vial(self, guest_name):
        UniverseLogger.event('BARTENDER ANSWERS: It is just a kind of dice. It was here before me.')

    def remember_first_order(self, guest_name, drink_name):
        if guest_name not in self.regular_drinks:
            self.regular_drinks[guest_name] = drink_name
            UniverseLogger.event(f'BARTENDER REMEMBERED FIRST ORDER: {guest_name} drinks {drink_name}')
            return
        UniverseLogger.event(f'BARTENDER ALREADY KNOWS: {guest_name} drinks {self.regular_drinks[guest_name]}')

    def knows_drink(self, guest_name):
        return guest_name in self.regular_drinks

    def mix_drink(self, guest_name, drink_name):
        self.remember_first_order(guest_name, drink_name)
        event = f'{guest_name} ordered {drink_name}'
        self.observe_event(event)
        UniverseLogger.event(f'BARTENDER MIXES DRINK: {drink_name} for {guest_name}')

    def pour_drink(self, guest_name, drink, serving_object):
        drink_name = self.get_drink_name(drink)
        serving_object_name = self.get_drink_name(serving_object)
        self.remember_first_order(guest_name, drink_name)
        if isinstance(serving_object, dict):
            serving_object['state'] = 'filled'
            serving_object['contains'] = drink_name
        event = f'{guest_name} was served {drink_name} in {serving_object_name}'
        self.observe_event(event)
        UniverseLogger.event(f'BARTENDER POURS DRINK: {drink_name} into {serving_object_name} for {guest_name}')
        return serving_object

    def get_drink_name(self, drink):
        if isinstance(drink, dict):
            return drink.get('name')
        return getattr(drink, 'name', drink)

    def idle_work(self):
        if not self.glasses_clean:
            self.current_task = 'wiping_glasses'
            self.glasses_clean = True
            UniverseLogger.event('BARTENDER WIPES ALL GLASSES')
            return
        if not self.bar_counter_clean:
            self.current_task = 'wiping_bar_counter'
            self.bar_counter_clean = True
            UniverseLogger.event('BARTENDER WIPES BAR COUNTER')
            return
        self.current_task = 'observing_bar'
        UniverseLogger.event('BARTENDER OBSERVES THE BAR')

    def read_universe_manual(self, universe_manual):
        return universe_manual.read(self)

    def enter_back_room(self, back_room):
        access_route = back_room.access.get(self.name)
        if access_route != 'main_door':
            return False
        self.current_location = back_room.name
        UniverseLogger.event('BARTENDER ENTERS BACK ROOM')
        return True

    def sleep_in_back_room(self, back_room, bar_has_guests):
        if bar_has_guests:
            return False
        if self.current_location != back_room.name:
            entered = self.enter_back_room(back_room)
            if not entered:
                return False
        self.current_task = 'sleeping'
        UniverseLogger.event('BARTENDER SLEEPS IN BACK ROOM')
        return True

    def prepare_for_guest(self):
        self.current_location = 'meeting_place'
        self.current_task = 'wiping_glasses'
        self.glasses_clean = False
        UniverseLogger.event('BARTENDER APPEARS BEHIND THE BAR')
        UniverseLogger.event('BARTENDER POLISHES A GLASS')

    def exchange_meow_with_cat(self, cat):
        cat_name = (
            getattr(cat, 'world_key', None)
            or getattr(cat, 'name', None)
        )
        meow = getattr(
            cat,
            'learning',
            {}
        ).get(
            'meow_knowledge',
            {}
        )
        cat_knows_meow = bool(
            meow.get('learned', False)
            and meow.get('can_speak', False)
        )
        cat_event = {'name': 'cat_meowed_at_bartender', 'cat': cat_name, 'sound': 'MEOW', 'understood': cat_knows_meow}
        self.cat_meow_history.append(cat_event)
        UniverseLogger.event(f'CAT MEOWS AT BARTENDER: {cat_name}')
        reply_event = {'name': 'bartender_replied_meow', 'bartender': self.name, 'cat': cat_name, 'sound': 'MEOW', 'reply': True}
        self.cat_meow_history.append(reply_event)
        UniverseLogger.event(f'BARTENDER REPLIES MEOW TO: {cat_name}')
        return {'cat_meow': cat_event, 'bartender_meow': reply_event}

    def serve_without_order(self, guest_name, drink, serving_object):
        drink_name = self.get_drink_name(drink)
        serving_object_name = self.get_drink_name(serving_object)
        if isinstance(serving_object, dict):
            serving_object['state'] = 'filled'
            serving_object['contains'] = drink_name
        event = f'{guest_name} was served {drink_name} in {serving_object_name}'
        self.observe_event(event)
        UniverseLogger.event(f'BARTENDER SERVES WITHOUT ORDER: {drink_name} into {serving_object_name} for {guest_name}')
        return serving_object
