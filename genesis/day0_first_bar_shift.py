from meeting_place.bar_objects import (
    BarBeerHypothesis,
    BarConversation,
    BarDrink,
    BarDrinkDiscussion,
    BarDrinkIdea,
    BarDrinkOrder,
    BarDrinkWager,
    BarGuestBet,
    BarGuestKnowledge,
    BarGuestState,
    BarTasteKnowledge,
    BarIngredientStock,
    BarWagerKnowledge,
    BarWagerDecisionMethod,
    BarWineAssessment,
    BarWineDiscussionKnowledge,
    BarWineHypothesis,
    DrinkRecipe,
    RecipeIngredientRequirement,
)
from core.entity.social_entity import _entity_attr_setdefault
from meeting_place.bar_yard import BarYard
from cats.cat_birth_resolver import CatBirthResolver

class Day0FirstBarShift:

    def _entity_attr_setdefault(self, entity, name, default):
        if not hasattr(entity, name):
            setattr(entity, name, default)
        return getattr(entity, name)

    def __init__(self, universe, meeting_place, library, gods, idea_entities):
        self.universe = universe
        self.meeting_place = meeting_place
        self.library = library
        self.gods = gods
        self.idea_entities = idea_entities
        self.history = []
        self.serpent = None
        self.god = None
        self.lilith = None
        self.cat_d20 = None
        self.garfield = None
        self.first_book = None
        self.bar_yard = BarYard()
        self.lilith_order = None
        self.serpent_lilith_conversation = (
            BarConversation()
        )

    def start_shift(self):
        event = self.meeting_place.bartender.begin_shift(bar_day=0, shift_start_tick=self.meeting_place.tick_count)
        self.history.append(event)
        return event

    def serpent_is_born_and_enters(self):
        while self.meeting_place.bar_clock.hour < 4:
            self.meeting_place.bar_clock.tick()
        while self.meeting_place.bar_clock.minute < 20:
            self.meeting_place.bar_clock.advance_minute()
        self.serpent = self.idea_entities.create_idea_entity(name='serpent', role='primordial_idea_entity', active=True, existence_pct=100.0, native_world='idea_universe', existence_by_world={'idea_universe': 100.0, 'root_universe': 0.0, 'eden': 0.0})
        self.serpent.energy_j = 0.0
        self.serpent.access = {'meeting_place': True, 'quantum_layer': 'via_meeting_place'}
        self.universe.world['serpent'] = self.serpent
        self.history.append({'name': 'serpent_born'})
        self.meeting_place.add_entity(self.serpent)
        self.history.append({'name': 'serpent_entered_bar', 'bar_time': self.meeting_place.bar_clock.time_text, 'bar_hour': self.meeting_place.bar_clock.hour, 'bar_minute': self.meeting_place.bar_clock.minute})
        return self.serpent

    def serpent_orders_first_drinks(self):
        if self.serpent is None:
            raise RuntimeError('Serpent does not exist yet.')
        result = self.meeting_place.serve_basic_drinks_on_tab(entity=self.serpent, drink_names=['wine', 'beer', 'mead'])
        self.serpent.bar_state = BarGuestState(
            seat='at_bar',
            drinks=[
                'wine',
                'beer',
                'mead',
            ],
            activity='tasting_ordered_drinks',
            tab='open',
            paid=False,
            receipt_number=(
                result['receipt'][
                    'receipt_number'
                ]
            ),
        )
        self.history.append({'name': 'serpent_orders_wine_beer_and_mead'})
        return result

    def serpent_proposes_bet(self):
        if self.serpent is None:
            raise RuntimeError('Serpent does not exist yet.')
        proposal = {'name': 'serpent_proposes_bet', 'guest': 'serpent', 'target': 'bartender'}
        self.meeting_place.emit_event(proposal)
        refusal = self.meeting_place.bartender.refuse_bet('serpent')
        self.serpent.bar_state.bet = (
            BarGuestBet(
                offered=True,
                accepted=False,
            )
        )
        self.history.extend([proposal, refusal])
        return {'proposal': proposal, 'response': refusal}

    def god_is_born_and_goes_to_library(self):
        self.god = self.gods.create_god(name='god', role='librarian')
        self.universe.god = self.god
        self.universe.world['god'] = self.god
        self.history.append({'name': 'god_born'})
        self.library.assign_librarian(self.god)
        self.library.god_enters(self.god)
        self.history.append({'name': 'god_entered_library'})
        self.first_book = self.gods.create_book(self.god)
        self.first_book.title = None
        self.first_book.entries = []
        self.first_book.state = 'being_written'
        self.first_book.location = 'library_with_author'
        self.history.append({'name': 'god_begins_first_unnamed_book'})
        return {'god': self.god, 'book': self.first_book}

    def god_leaves_library_and_enters_bar(self):
        if self.god is None:
            raise RuntimeError('God does not exist yet.')
        if self.first_book is None:
            raise RuntimeError('God has not created his first book.')
        if self.first_book.entries != []:
            raise RuntimeError("God's first book must still be empty.")
        if self.first_book not in self.library.books:
            self.library.shelve_book(self.first_book)
        self.first_book.title = None
        self.first_book.state = 'being_written'
        self.first_book.location = 'library'
        leave_result = self.library.god_leaves(self.god)
        self.history.append({'name': 'god_left_library', 'result': leave_result})
        self.meeting_place.add_entity(self.god)
        self.history.append({'name': 'god_entered_bar'})
        return self.god

    def lilith_orders_vodka_with_lemon(self):
        if self.lilith is None:
            raise RuntimeError('Lilith does not exist yet.')
        self.lilith_order = BarDrinkOrder(
            guest='lilith',
            drink='vodka_with_lemon',
            base='vodka',
            garnish='lemon',
            waiting_for='lemon',
        )
        self.history.append({'name': 'lilith_orders_vodka_with_lemon'})
        unavailable = {'name': 'bartender_reports_missing_lemon', 'guest': 'lilith', 'ingredient': 'lemon', 'available': False}
        self.meeting_place.emit_event(unavailable)
        self.history.append(unavailable)
        points_out_tree = {'name': 'lilith_points_out_lemon_tree', 'guest': 'lilith', 'location': 'bar_yard', 'tree': 'lemon_tree'}
        self.meeting_place.emit_event(points_out_tree)
        self.history.append(points_out_tree)
        learned = self.meeting_place.bartender.learn_requested_drink(guest_name='lilith', drink_name='vodka_with_lemon')
        self.history.append(learned)
        left = self.meeting_place.bartender.leave_for_lemon(guest_name='lilith')
        self.history.append(left)
        return {
            'order': self.lilith_order.to_dict(),
            'bartender': left,
        }

    def serpent_and_lilith_begin_conversation(self):
        if self.serpent is None:
            raise RuntimeError('Serpent is not in the scene.')
        if self.lilith is None:
            raise RuntimeError('Lilith is not in the scene.')
        if self.meeting_place.bartender.current_location != 'bar_yard':
            raise RuntimeError('This conversation begins while the bartender is away for the lemon.')
        self.serpent_lilith_conversation.begin(
            participants=[
                'serpent',
                'lilith',
            ]
        )
        event = {'name': 'serpent_and_lilith_begin_conversation', 'participants': ['serpent', 'lilith'], 'bartender_present': False}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def serpent_and_lilith_taste_first_drinks(self):
        if not self.serpent_lilith_conversation.started:
            raise RuntimeError('Serpent and Lilith are not talking yet.')
        drinks = ['wine', 'beer', 'mead']
        serpent_tasting = {drink: 'dislikes' for drink in drinks}
        lilith_tasting = {drink: 'dislikes' for drink in drinks}
        event = {'name': 'serpent_and_lilith_taste_first_drinks', 'offered_by': 'serpent', 'shared_with': 'lilith', 'drinks': list(drinks), 'serpent_reaction': serpent_tasting, 'lilith_reaction': lilith_tasting}
        self.serpent.first_bar_drink_tasting = serpent_tasting
        self.lilith.first_bar_drink_tasting = lilith_tasting
        self.meeting_place.emit_event(event)
        self.history.append(event)
        self.serpent_lilith_conversation.add_line(
            speaker='serpent',
            meaning=(
                'none_of_the_existing_wine_'
                'beer_or_mead_tastes_good'
            ),
        )
        self.serpent_lilith_conversation.add_line(
            speaker='lilith',
            meaning='agrees',
        )
        return event

    def serpent_proposes_drink_wager_to_lilith(self):
        if not self.serpent_lilith_conversation.started:
            raise RuntimeError('Serpent and Lilith are not talking yet.')
        if not hasattr(self.serpent, 'first_bar_drink_tasting') or not hasattr(self.lilith, 'first_bar_drink_tasting'):
            raise RuntimeError('They must taste the drinks first.')
        wager = BarDrinkWager()
        self.serpent_lilith_drink_wager = wager
        event = {'name': 'serpent_proposes_drink_wager_to_lilith', 'wager': wager.to_dict()}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        self.serpent_lilith_conversation.add_line(
            speaker='serpent',
            meaning='proposes_drink_wager',
        )
        return wager

    def lilith_accepts_drink_wager(self):
        wager = getattr(self, 'serpent_lilith_drink_wager', None)
        if wager is None:
            raise RuntimeError('Serpent has not proposed the wager.')
        if wager.accepted:
            raise RuntimeError('The wager is already accepted.')
        wager.accept(
            participant='lilith'
        )
        event = {'name': 'lilith_accepts_drink_wager', 'wager': wager.to_dict()}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        self.serpent_lilith_conversation.add_line(
            speaker='lilith',
            meaning='accepts_drink_wager',
        )
        return wager

    def play_serpent_lilith_first_conversation(self):
        tasting = self.serpent_and_lilith_taste_first_drinks()
        wager = self.serpent_proposes_drink_wager_to_lilith()
        accepted = self.lilith_accepts_drink_wager()
        return {'tasting': tasting, 'wager': wager, 'accepted': accepted}

    def serpent_and_lilith_agree_on_table(self):
        if not self.serpent_lilith_conversation.started:
            raise RuntimeError('Serpent and Lilith are not talking.')
        wager = getattr(self, 'serpent_lilith_drink_wager', None)
        if wager is None or not wager.accepted:
            raise RuntimeError('Their wager must already be accepted.')
        event = {'name': 'serpent_and_lilith_agree_on_table', 'participants': ['serpent', 'lilith'], 'agreed': True}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        self.serpent_lilith_conversation.add_line(
            speaker='serpent_and_lilith',
            meaning='agree_to_move_to_table',
        )
        return event

    def serpent_moves_from_bar_to_existing_table(self):
        if self.serpent is None:
            raise RuntimeError('Serpent does not exist.')
        seating_cells = [cell for cell in self.meeting_place.bar_geometry.cells if cell.seating]
        if not seating_cells:
            raise RuntimeError('No existing seating place in bar.')
        seat = seating_cells[0]
        self.serpent.bar_state.seat = seat.name
        self.serpent.bar_state.location = 'table'
        self.serpent.bar_state.activity = 'waiting_for_lilith'
        event = {'name': 'serpent_moves_to_existing_table', 'guest': 'serpent', 'from': 'bar_counter', 'to': seat.name}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def bartender_returns_with_lemon(self):
        if self.meeting_place.bartender.current_location != 'bar_yard':
            raise RuntimeError('Bartender is not in the bar yard.')
        result = self.bar_yard.pick_lemon('bartender')
        if not result['picked']:
            raise RuntimeError('Bartender failed to pick lemon.')
        stock = self.meeting_place.back_room.bar_ingredients
        lemon_stock = stock.get('lemon')
        if lemon_stock is None:
            lemon_stock = BarIngredientStock(name='lemon', available=True, fundamental=False, serve_directly=False, shots=0, unit='fruit')
            stock['lemon'] = lemon_stock
        lemon_stock.shots += 1
        lemon_stock.available = True
        returned = self.meeting_place.bartender.return_with_lemon(guest_name='lilith')
        self.meeting_place.refresh_basic_drinks()
        self.history.append({'name': 'lemon_added_to_bar_stock', 'amount': 1})
        self.history.append(returned)
        return {'picked': result, 'stock': lemon_stock.to_dict(), 'returned': returned}

    def bartender_makes_vodka_with_lemon(self):
        if 'lemon' not in self.meeting_place.back_room.bar_ingredients:
            raise RuntimeError('No lemon in bar stock.')
        drink = self.meeting_place.mix_basic_drink('vodka_with_lemon')
        drink.price_basis = 'vodka'
        drink.effects = {}
        drink.preparation = {'vodka': 1, 'lemon': 'drop'}
        self.lilith_order.record_attempt(
            drink
        )
        event = {'name': 'bartender_makes_vodka_with_lemon', 'guest': 'lilith', 'drink': 'vodka_with_lemon', 'price_basis': 'vodka', 'effects': {}}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return drink

    def lilith_corrects_vodka_with_lemon(self):
        if self.lilith_order is None:
            raise RuntimeError('Lilith has no pending order.')
        correction = {'name': 'lilith_corrects_vodka_with_lemon', 'guest': 'lilith', 'requested_recipe': {'vodka': 1, 'lemon': 'whole', 'sugar': 1}}
        self.meeting_place.emit_event(correction)
        self.history.append(correction)
        return correction

    def bartender_learns_lilith_drink(self):
        mix_book = self.meeting_place.how_to_mix_drinks
        recipe = DrinkRecipe(name='lilith', origin='taught_by_lilith', hidden=False, learned=True, teacher='lilith', category='learned_drink', price_basis='vodka', effects={'energy_j': 1.0, 'creative_will': 0.1}, ingredients={'vodka': RecipeIngredientRequirement(shots=1, consumed=False), 'lemon': RecipeIngredientRequirement(shots=1, consumed=True, use='whole'), 'sugar': RecipeIngredientRequirement(shots=1, consumed=True, unit='cube')})
        mix_book.recipes['lilith'] = recipe
        learned = self.meeting_place.bartender.learn_guest_drink(drink_name='lilith', teacher='lilith', ingredients=['vodka', 'whole_lemon', 'sugar_cube'], effects={'energy_j': 1.0, 'creative_will': 0.1}, price_basis='vodka')
        self.meeting_place.refresh_basic_drinks()
        self.history.append({'name': 'bartender_learns_lilith', 'recipe': recipe})
        return {'recipe': recipe, 'learned': learned}

    def apply_lilith_drink_effect(self, entity):
        recipe = self.meeting_place.how_to_mix_drinks.recipes['lilith']
        effects = recipe.effects
        entity.energy_j = float(getattr(entity, 'energy_j', 0.0)) + float(effects['energy_j'])
        entity.creative_will = float(getattr(entity, 'creative_will', 0.0)) + float(effects['creative_will'])
        return {'name': 'lilith_drink_effect_applied', 'energy_j': effects['energy_j'], 'creative_will': effects['creative_will']}

    def bartender_mixes_final_lilith(self):
        recipe = self.meeting_place.how_to_mix_drinks.recipes.get('lilith')
        if recipe is None:
            raise RuntimeError('Bartender has not learned lilith.')
        stock = self.meeting_place.back_room.bar_ingredients
        for ingredient_name in ('vodka', 'lemon', 'sugar'):
            if ingredient_name not in stock:
                raise RuntimeError(f'Missing ingredient for lilith: {ingredient_name}')
        if stock['lemon'].shots < 1:
            return self.universe.create_cronenberg_from_quantum_error(error=RuntimeError('No lemon for lilith.'), source_component='meeting_place', source_operation='bartender_mixes_final_lilith')
        if stock['sugar'].shots < 1:
            return self.universe.create_cronenberg_from_quantum_error(error=RuntimeError('No sugar for lilith.'), source_component='meeting_place', source_operation='bartender_mixes_final_lilith')
        stock['lemon'].consume(1)
        stock['sugar'].consume(1)
        drink = BarDrink(
            name='lilith',
            type='learned_bar_drink',
            category='learned_drink',
            ingredients={
                'vodka': 1,
                'lemon': 'whole',
                'sugar': 1,
            },
            price_basis='vodka',
            effects=dict(recipe.effects),
        )
        self.lilith_order.complete(
            drink
        )
        event = {'name': 'bartender_mixes_final_lilith', 'guest': 'lilith', 'drink': 'lilith', 'sugar_cubes': 1}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return drink

    def bartender_hands_lilith_drink_and_receipt(self):
        drink = self.bartender_mixes_final_lilith()
        self.meeting_place.bar_counter.cash_register.add_to_tab(entity=self.lilith, drink=drink)
        receipt = self.meeting_place.bar_counter.cash_register.print_open_tab_receipt(self.lilith)
        self.lilith_order.attach_receipt(
            receipt['receipt_number']
        )
        event = {'name': 'bartender_hands_lilith_drink_and_receipt', 'guest': 'lilith', 'drink': 'lilith', 'receipt_number': receipt['receipt_number'], 'paid': False}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return {'drink': drink, 'receipt': receipt}

    def lilith_tastes_and_requests_second_sugar_cube(self):
        drink = self.lilith_order.final_drink
        if drink is None:
            raise RuntimeError('Lilith has no drink to taste.')
        event = {'name': 'lilith_tastes_and_requests_second_sugar_cube', 'guest': 'lilith', 'drink': 'lilith', 'request': {'ingredient': 'sugar', 'amount': 1, 'unit': 'cube'}}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def bartender_adds_second_sugar_cube(self):
        sugar = self.meeting_place.back_room.bar_ingredients.get('sugar')
        if sugar is None:
            raise RuntimeError('Sugar is not in bar stock.')
        if sugar.shots < 1:
            return self.universe.create_cronenberg_from_quantum_error(error=RuntimeError('Bar sugar depleted.'), source_component='meeting_place', source_operation='bartender_adds_second_sugar_cube')
        sugar.consume(1)
        drink = self.lilith_order.final_drink
        drink.ingredients['sugar'] = 2
        recipe = self.meeting_place.how_to_mix_drinks.recipes['lilith']
        recipe.ingredients['sugar'].shots = 2
        recipe.revision = 2
        recipe.revision_reason = 'lilith_requested_second_sugar_cube'
        event = {'name': 'bartender_adds_second_sugar_cube', 'guest': 'lilith', 'drink': 'lilith', 'final_sugar_cubes': 2, 'recipe_updated': True}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return {'drink': drink, 'recipe': recipe}

    def lilith_joins_serpent_at_existing_table(self):
        if self.serpent.bar_state.location != 'table':
            raise RuntimeError('Serpent is not waiting at table.')
        self._entity_attr_setdefault(
            self.lilith,
            'bar_state',
            BarGuestState()
        )
        self.lilith.bar_state.location = 'table'
        self.lilith.bar_state.table_with = 'serpent'
        self.lilith.bar_state.activity = (
            'discussing_good_drinks'
        )
        self.serpent.bar_state.activity = (
            'discussing_good_drinks'
        )
        event = {'name': 'lilith_joins_serpent_at_table', 'guest': 'lilith', 'with': 'serpent', 'drink_in_hand': 'lilith'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def lilith_and_serpent_take_first_table_drinks(self):
        discussion = getattr(self, 'serpent_lilith_good_drink_discussion', None)
        if discussion is None:
            raise RuntimeError('Good drink discussion has not started.')
        lilith_drink = self.lilith_order.final_drink
        if lilith_drink is None:
            raise RuntimeError('Lilith has no drink.')
        effects = lilith_drink.effects
        self.lilith.energy_j = getattr(self.lilith, 'energy_j', 0.0) + effects.get('energy_j', 0.0)
        self.lilith.creative_will = getattr(self.lilith, 'creative_will', 0.0) + effects.get('creative_will', 0.0)
        lilith_event = {'name': 'lilith_takes_first_sip_of_lilith', 'guest': 'lilith', 'drink': 'lilith', 'effects_applied': True}
        self.meeting_place.emit_event(lilith_event)
        self.history.append(lilith_event)
        serpent_event = {'name': 'serpent_finishes_wine_at_table', 'guest': 'serpent', 'drink': 'wine', 'finished': True}
        self.meeting_place.emit_event(serpent_event)
        self.history.append(serpent_event)
        return {'lilith': lilith_event, 'serpent': serpent_event}

    def lilith_and_serpent_make_first_wine_observation(self):
        discussion = getattr(self, 'serpent_lilith_good_drink_discussion', None)
        if discussion is None:
            raise RuntimeError('Good drink discussion has not started.')
        observation = BarDrinkIdea(
            subject='wine',
            lilith={
                'observation':
                    'wine_tastes_like_water',
            },
            serpent={
                'agrees': True,
                'proposal':
                    'flavor_should_be_fuller',
            },
        )
        discussion.add_idea(
            observation
        )
        event = {'name': 'first_good_wine_observation', 'subject': 'wine', 'wine_tastes_like_water': True, 'desired_flavor': 'fuller'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return observation

    def god_arrives_after_first_wine_observation(self):
        discussion = getattr(self, 'serpent_lilith_good_drink_discussion', None)
        if discussion is None:
            raise RuntimeError('Good drink discussion has not started.')
        if not discussion.ideas:
            raise RuntimeError('First wine observation has not happened yet.')
        god = self.god_leaves_library_and_enters_bar()
        event = {'name': 'god_arrives_during_wine_discussion', 'guest': 'god', 'from': 'library', 'to': 'bar'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return god

    def god_looks_around_bar(self):
        if self.god is None:
            raise RuntimeError('God does not exist.')
        if self.god not in self.meeting_place.entities:
            raise RuntimeError('God is not in the bar.')
        self.god.bar_state = BarGuestState(
            location='entrance_area',
            activity='looking_around',
        )
        event = {'name': 'god_looks_around_bar', 'guest': 'god', 'activity': 'looking_around'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def god_moves_to_drink_menu(self):
        if getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'activity',
            None
        ) != 'looking_around':
            raise RuntimeError('God has not looked around yet.')
        self.god.bar_state.location = 'drink_menu'
        self.god.bar_state.activity = 'browsing_drinks'
        self.meeting_place.refresh_basic_drinks()
        available_drinks = sorted(self.meeting_place.drink_menu.keys())
        event = {'name': 'god_browses_drink_menu', 'guest': 'god', 'available_drinks': available_drinks}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def serpent_and_lilith_continue_wine_discussion(self):
        discussion = getattr(self, 'serpent_lilith_good_drink_discussion', None)
        if discussion is None:
            raise RuntimeError('Good drink discussion has not started.')
        event = {'name': 'serpent_and_lilith_continue_wine_discussion', 'participants': ['serpent', 'lilith'], 'subject': 'wine', 'previous_idea': 'flavor_should_be_fuller', 'new_idea': None}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        discussion.resolved = False
        return event

    def bartender_asks_god_for_order(self):
        if getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'activity',
            None
        ) != 'browsing_drinks':
            raise RuntimeError('God is not browsing the drink menu.')
        event = {'name': 'bartender_asks_god_for_order', 'guest': 'god', 'question': 'what_will_you_have'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def god_says_still_choosing(self):
        if getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'activity',
            None
        ) != 'browsing_drinks':
            raise RuntimeError('God is not choosing a drink.')
        self.god.bar_state.activity = 'still_choosing'
        event = {'name': 'god_says_still_choosing', 'guest': 'god', 'ordered': False}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def lilith_tastes_mead_and_adds_sweetness_idea(self):
        discussion = getattr(self, 'serpent_lilith_good_drink_discussion', None)
        if discussion is None:
            raise RuntimeError('Good drink discussion has not started.')
        tasting = {'name': 'lilith_tastes_mead', 'guest': 'lilith', 'drink': 'mead'}
        self.meeting_place.emit_event(tasting)
        self.history.append(tasting)
        idea = BarDrinkIdea(
            subject='wine',
            source='lilith',
            observation='wine_should_be_sweet',
            desired_property={
                'sweetness': True,
            },
        )
        discussion.add_idea(
            idea
        )
        event = {'name': 'lilith_says_wine_should_be_sweet', 'subject': 'wine', 'desired_property': 'sweet'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return {'tasting': tasting, 'idea': idea}

    def god_finishes_browsing_and_orders_lilith(self):
        if self.god is None:
            raise RuntimeError('God does not exist.')
        activity = getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'activity',
            None
        )
        if activity not in ('browsing_drinks', 'still_choosing'):
            raise RuntimeError('God is not choosing from the menu.')
        if 'lilith' not in self.meeting_place.how_to_mix_drinks.recipes:
            raise RuntimeError('Lilith drink has not been learned yet.')
        self.god.bar_state.activity = 'ordered_lilith'
        self.god.bar_state.order = 'lilith'
        event = {'name': 'god_orders_lilith', 'guest': 'god', 'drink': 'lilith'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def serpent_tastes_mead_then_beer(self):
        discussion = getattr(self, 'serpent_lilith_good_drink_discussion', None)
        if discussion is None:
            raise RuntimeError('Good drink discussion has not started.')
        mead_event = {'name': 'serpent_tastes_mead', 'guest': 'serpent', 'drink': 'mead'}
        self.meeting_place.emit_event(mead_event)
        self.history.append(mead_event)
        beer_event = {'name': 'serpent_tastes_beer', 'guest': 'serpent', 'drink': 'beer'}
        self.meeting_place.emit_event(beer_event)
        self.history.append(beer_event)
        return {'mead': mead_event, 'beer': beer_event}

    def serpent_adds_bitterness_as_wine_idea(self):
        discussion = getattr(self, 'serpent_lilith_good_drink_discussion', None)
        if discussion is None:
            raise RuntimeError('Good drink discussion has not started.')
        observation = BarDrinkIdea(
            subject='wine',
            source='serpent',
            assessment={
                'sweetness': 'good',
                'full_body': 'still_missing',
            },
            proposal={
                'bitterness': True,
            },
        )
        discussion.add_idea(
            observation
        )
        event = {'name': 'serpent_proposes_bitterness_for_wine', 'subject': 'wine', 'sweetness': 'good_but_not_enough', 'desired_property': 'bitterness'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return observation

    def bartender_attempts_gods_lilith_without_lemon(self):
        if getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'order',
            None
        ) != 'lilith':
            raise RuntimeError('God has not ordered lilith.')
        lemon = self.meeting_place.back_room.bar_ingredients.get('lemon')
        lemon_count = lemon.shots if lemon is not None else 0
        if lemon_count > 0:
            raise RuntimeError('This scene requires the bar to be out of lemons.')
        error = RuntimeError("No lemon available for God's lilith.")
        cronenberg = self.universe.create_cronenberg_from_quantum_error(error=error, source_component='meeting_place', source_operation='bartender_attempts_gods_lilith')
        event = {'name': 'gods_lilith_fails_without_lemon', 'guest': 'god', 'drink': 'lilith', 'reason': 'no_lemon', 'cronenberg_created': True}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return {'event': event, 'cronenberg': cronenberg}

    def bartender_runs_to_yard_for_more_lemons(self, amount=6):
        amount = int(amount)
        if amount <= 1:
            raise ValueError('Bartender must bring back more than one lemon.')
        self.meeting_place.bartender.current_location = 'bar_yard'
        departure = {'name': 'bartender_runs_to_yard_for_more_lemons', 'destination': 'bar_yard', 'reason': 'restock_lemons', 'target_amount': amount}
        self.meeting_place.emit_event(departure)
        self.history.append(departure)
        picked = []
        for _ in range(amount):
            result = self.bar_yard.pick_lemon('bartender')
            if not result.get('picked', False):
                raise RuntimeError('Bartender failed while restocking lemons.')
            picked.append(result)
        stock = self.meeting_place.back_room.bar_ingredients
        lemon_stock = stock.get('lemon')
        if lemon_stock is None:
            lemon_stock = BarIngredientStock(name='lemon', available=True, fundamental=False, serve_directly=False, shots=0, unit='fruit')
            stock['lemon'] = lemon_stock
        lemon_stock.shots += amount
        lemon_stock.available = True
        self.meeting_place.bartender.current_location = 'bar'
        returned = {'name': 'bartender_returns_with_lemon_stock', 'source': 'bar_yard', 'ingredient': 'lemon', 'amount': amount, 'stock_after': lemon_stock.shots}
        self.meeting_place.emit_event(returned)
        self.history.append(returned)
        self.meeting_place.refresh_basic_drinks()
        return {'picked': picked, 'returned': returned, 'stock': lemon_stock.to_dict()}

    def bartender_mixes_gods_lilith_after_restock(self):
        if getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'order',
            None
        ) != 'lilith':
            raise RuntimeError('God is not waiting for lilith.')
        recipe = self.meeting_place.how_to_mix_drinks.recipes.get('lilith')
        if recipe is None:
            raise RuntimeError('Bartender does not know lilith.')
        stock = self.meeting_place.back_room.bar_ingredients
        lemon = stock.get('lemon')
        sugar = stock.get('sugar')
        if lemon is None or lemon.shots < 1:
            return self.universe.create_cronenberg_from_quantum_error(error=RuntimeError('No lemon after lemon restock.'), source_component='meeting_place', source_operation='bartender_mixes_gods_lilith_after_restock')
        required_sugar = recipe.ingredients['sugar'].shots
        if sugar is None or sugar.shots < required_sugar:
            return self.universe.create_cronenberg_from_quantum_error(error=RuntimeError("Not enough sugar for God's lilith."), source_component='meeting_place', source_operation='bartender_mixes_gods_lilith_after_restock')
        lemon.consume(1)
        sugar.consume(required_sugar)
        drink = BarDrink(
            name='lilith',
            type='learned_bar_drink',
            category='learned_drink',
            ingredients={
                'vodka': 1,
                'lemon': 'whole',
                'sugar': required_sugar,
            },
            price_basis=recipe.price_basis or 'vodka',
            effects=dict(recipe.effects),
        )
        self.god.bar_state.prepared_drink = drink
        self.god.bar_state.activity = (
            'waiting_for_lilith_service'
        )
        event = {'name': 'bartender_mixes_gods_lilith', 'guest': 'god', 'drink': 'lilith', 'lemon_used': 1, 'sugar_cubes_used': required_sugar, 'lemons_remaining': lemon.shots}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return drink

    def bartender_serves_gods_lilith_with_receipt(self):
        drink = getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'prepared_drink',
            None
        )
        if drink is None:
            raise RuntimeError("God's lilith has not been prepared.")
        self.meeting_place.bar_counter.cash_register.add_to_tab(entity=self.god, drink=drink)
        receipt = self.meeting_place.bar_counter.cash_register.print_open_tab_receipt(self.god)
        self.god.bar_state.drink = drink
        self.god.bar_state.receipt_number = (
            receipt['receipt_number']
        )
        self.god.bar_state.activity = 'holding_lilith'
        event = {'name': 'bartender_serves_gods_lilith', 'guest': 'god', 'drink': 'lilith', 'receipt_number': receipt['receipt_number'], 'paid': False, 'drunk': False}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return {'drink': drink, 'receipt': receipt}

    def god_tastes_lilith(self):
        if self.god is None:
            raise RuntimeError('God does not exist.')
        bar_state = getattr(
            self.god,
            'bar_state',
            None
        )
        if (
            bar_state is None
            or bar_state.activity != 'holding_lilith'
        ):
            raise RuntimeError('God is not holding lilith.')
        drink = bar_state.drink
        if drink is None:
            raise RuntimeError('God has no lilith to taste.')
        effects = drink.effects
        energy_gain = float(effects.get('energy_j', 0.0))
        creative_will_gain = float(effects.get('creative_will', 0.0))
        energy_before = float(getattr(self.god, 'energy_j', 0.0))
        creative_will_before = float(getattr(self.god, 'creative_will', 0.0))
        self.god.energy_j = energy_before + energy_gain
        self.god.creative_will = creative_will_before + creative_will_gain
        bar_state.activity = 'tasting_lilith'
        bar_state.lilith_tasted = True
        event = {'name': 'god_tastes_lilith', 'guest': 'god', 'drink': 'lilith', 'energy_before': energy_before, 'energy_after': self.god.energy_j, 'creative_will_before': creative_will_before, 'creative_will_after': self.god.creative_will, 'effects_applied': True}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def serpent_notices_god_and_calls_him_over(self):
        if self.god is None:
            raise RuntimeError('God does not exist.')
        if getattr(
            getattr(
                self.serpent,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'table':
            raise RuntimeError('Serpent is not at the table.')
        if getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'activity',
            None
        ) != 'tasting_lilith':
            raise RuntimeError('God is not at the expected bar checkpoint.')
        event = {'name': 'serpent_notices_god_and_calls_him_over', 'caller': 'serpent', 'called': 'god', 'from': 'table'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        self.god.bar_state.called_to_table_by = 'serpent'
        return event

    def god_joins_serpent_and_lilith_at_table(self):
        if getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'called_to_table_by',
            None
        ) != 'serpent':
            raise RuntimeError('Serpent has not called God over.')
        if getattr(
            getattr(
                self.lilith,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'table':
            raise RuntimeError('Lilith is not at the table.')
        if getattr(
            getattr(
                self.serpent,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'table':
            raise RuntimeError('Serpent is not at the table.')
        self.god.bar_state.location = 'table'
        self.god.bar_state.table_with = [
            'serpent',
            'lilith',
        ]
        self.god.bar_state.activity = 'at_table'
        event = {'name': 'god_joins_serpent_and_lilith_at_table', 'guest': 'god', 'with': ['serpent', 'lilith'], 'drink_in_hand': 'lilith'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def serpent_explains_wine_discussion_to_god(self):
        if getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'table':
            raise RuntimeError('God is not at the table.')
        discussion = self.serpent_lilith_good_drink_discussion
        event = {'name': 'serpent_explains_wine_discussion_to_god', 'speaker': 'serpent', 'listener': 'god', 'summary': {'fuller_flavor': True, 'sweetness': True, 'bitterness': True}}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        knowledge = self._entity_attr_setdefault(
            self.god,
            'bar_knowledge',
            BarGuestKnowledge()
        )
        knowledge.wine_discussion = (
            BarWineDiscussionKnowledge
            .from_discussion(
                discussion
            )
        )
        return event

    def lilith_rejects_bitterness_and_proposes_acidity(self):
        discussion = self.serpent_lilith_good_drink_discussion
        event = {'name': 'lilith_rejects_bitterness_for_wine', 'speaker': 'lilith', 'rejected_property': 'bitterness', 'reason': 'does_not_feel_right_for_wine'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        idea = BarDrinkIdea(
            subject='wine',
            source='lilith',
            revision={
                'remove': 'bitterness',
                'add': 'acidity',
            },
            desired_property={
                'acidity': True,
            },
        )
        discussion.add_idea(
            idea
        )
        discussion.current_hypothesis = (
            BarWineHypothesis(
                fuller_flavor=True,
                sweetness=True,
                bitterness=False,
                acidity=True,
            )
        )
        proposal_event = {'name': 'lilith_proposes_acidity_for_wine', 'subject': 'wine', 'desired_property': 'acidity'}
        self.meeting_place.emit_event(proposal_event)
        self.history.append(proposal_event)
        return {'rejection': event, 'idea': idea, 'proposal': proposal_event}

    def lilith_gives_serpent_taste_of_lilith(self):
        drink = self.lilith_order.final_drink
        if drink is None:
            raise RuntimeError('Lilith does not have her drink.')
        effects = drink.effects
        energy_gain = float(effects.get('energy_j', 0.0))
        will_gain = float(effects.get('creative_will', 0.0))
        energy_before = float(getattr(self.serpent, 'energy_j', 0.0))
        will_before = float(getattr(self.serpent, 'creative_will', 0.0))
        self.serpent.energy_j = energy_before + energy_gain
        self.serpent.creative_will = will_before + will_gain
        event = {'name': 'lilith_gives_serpent_taste_of_lilith', 'giver': 'lilith', 'taster': 'serpent', 'drink': 'lilith', 'energy_before': energy_before, 'energy_after': self.serpent.energy_j, 'creative_will_before': will_before, 'creative_will_after': self.serpent.creative_will, 'effects_applied': True}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def serpent_grimaces_at_lilith_and_turns_to_god(self):
        if not self.history or self.history[-1].get('name') != 'lilith_gives_serpent_taste_of_lilith':
            raise RuntimeError('Serpent has not just tasted lilith.')
        event = {'name': 'serpent_grimaces_at_lilith_and_turns_to_god', 'serpent': 'serpent', 'reaction': 'grimace', 'drink': 'lilith', 'turns_to': 'god'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def god_orders_wine_to_judge_discussion(self):
        if getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'table':
            raise RuntimeError('God is not at the table.')
        self.god.bar_state.wine_order = (
            BarDrinkOrder(
                guest='god',
                drink='wine',
                purpose='judge_wine_discussion',
                tasted=False,
            )
        )
        event = {'name': 'god_orders_wine_to_judge_discussion', 'guest': 'god', 'drink': 'wine', 'purpose': 'judge_wine_discussion'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def bartender_serves_god_wine_and_receipt(self):
        order = getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'wine_order',
            None
        )
        if order is None or order.drink != 'wine':
            raise RuntimeError('God has not ordered wine.')
        drink = BarDrink(
            name='wine',
            type='basic_bar_drink',
            category='basic_drink',
        )
        cash_register = self.meeting_place.bar_counter.cash_register
        cash_register.add_to_tab(entity=self.god, drink=drink)
        receipt = cash_register.print_open_tab_receipt(self.god)
        order.complete(
            drink
        )
        order.attach_receipt(
            receipt['receipt_number']
        )
        self.god.bar_state.wine = drink
        self.god.bar_state.receipt_number = (
            receipt['receipt_number']
        )
        event = {'name': 'bartender_serves_god_wine_and_receipt', 'guest': 'god', 'drink': 'wine', 'receipt_number': receipt['receipt_number'], 'paid': False, 'tasted': False}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return {'drink': drink, 'receipt': receipt, 'event': event}

    def serpent_agrees_with_acidity_but_wants_balance(self):
        discussion = self.serpent_lilith_good_drink_discussion
        hypothesis = discussion.current_hypothesis
        if hypothesis is None:
            raise RuntimeError('Current wine hypothesis does not exist.')
        if not hypothesis.acidity:
            raise RuntimeError('Acidity has not been proposed yet.')
        idea = BarDrinkIdea(
            subject='wine',
            source='serpent',
            agrees_with='acidity',
            qualification={
                'acidity': 'moderate',
            },
            meaning=(
                'acidity_is_right_but_too_much_'
                'would_make_the_wine_bad'
            ),
        )
        discussion.add_idea(
            idea
        )
        hypothesis.acidity = 'moderate'
        event = {'name': 'serpent_says_wine_needs_moderate_acidity', 'speaker': 'serpent', 'subject': 'wine', 'agrees_acidity': True, 'too_much_acidity': 'bad', 'desired_acidity': 'moderate'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return {'idea': idea, 'event': event}

    def god_tastes_existing_wine_and_rejects_it(self):
        wine_order = getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'wine_order',
            None
        )
        if wine_order is None:
            raise RuntimeError('God has no wine to taste.')
        if not wine_order.served:
            raise RuntimeError("God's wine has not been served.")
        wine_order.mark_tasted()
        assessment = BarWineAssessment(
            quality='bad',
            body='watery',
            comparison=(
                'water_in_which_someone_'
                'soaked_grapes'
            ),
        )
        knowledge = self._entity_attr_setdefault(
            self.god,
            'bar_knowledge',
            BarGuestKnowledge()
        )
        knowledge.existing_wine = assessment
        event = {'name': 'god_tastes_existing_wine', 'guest': 'god', 'drink': 'wine', 'assessment': assessment.to_dict()}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def lilith_explains_sweetness_to_god(self):
        discussion = self.serpent_lilith_good_drink_discussion
        hypothesis = discussion.current_hypothesis
        if hypothesis is None or not hypothesis.sweetness:
            raise RuntimeError('Sweetness is not part of the wine hypothesis.')
        explanation = {'name': 'lilith_explains_sweetness_to_god', 'speaker': 'lilith', 'listener': 'god', 'principle': 'sweetness', 'meaning': 'good_wine_should_have_some_sweetness'}
        self.meeting_place.emit_event(explanation)
        self.history.append(explanation)
        self._entity_attr_setdefault(
            self.god,
            'bar_knowledge',
            BarGuestKnowledge()
        ).sweetness_explained = True
        return explanation

    def god_finishes_serpents_mead_and_understands_sweetness(self):
        knowledge = getattr(
            self.god,
            'bar_knowledge',
            None
        )
        if (
            knowledge is None
            or not knowledge.sweetness_explained
        ):
            raise RuntimeError('Lilith has not explained sweetness yet.')
        event = {'name': 'god_finishes_serpents_mead_and_understands_sweetness', 'guest': 'god', 'drink': 'mead', 'source': 'serpent', 'finished': True, 'understands': {'sweetness': True}, 'assessment': {'sweet': True, 'good': False}}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        knowledge.sweetness = BarTasteKnowledge(
            understood=True,
            example='mead',
            example_is_sweet=True,
            example_is_good=False,
        )
        self._entity_attr_setdefault(
            self.serpent,
            'bar_state',
            BarGuestState()
        ).mead_finished_by = 'god'
        return event

    def serpent_tells_god_about_drink_wager(self):
        wager = getattr(self, 'serpent_lilith_drink_wager', None)
        if wager is None:
            raise RuntimeError('Serpent and Lilith have no drink wager.')
        event = {'name': 'serpent_tells_god_about_drink_wager', 'speaker': 'serpent', 'listener': 'god', 'wager': wager.to_dict(), 'contest': ['wine', 'mead', 'beer']}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        self._entity_attr_setdefault(
            self.god,
            'bar_knowledge',
            BarGuestKnowledge()
        ).drink_wager = BarWagerKnowledge(
            known=True,
            source='serpent',
        )
        return event

    def serpent_offers_god_wager_participation(self):
        knowledge = getattr(
            self.god,
            'bar_knowledge',
            None
        )
        if (
            knowledge is None
            or knowledge.drink_wager is None
            or not knowledge.drink_wager.known
        ):
            raise RuntimeError('God does not know about the wager.')
        event = {'name': 'serpent_offers_god_wager_participation', 'offered_by': 'serpent', 'offered_to': 'god', 'accepted': None}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def god_accepts_drink_wager(self):
        offers = [event for event in self.history if event.get('name') == 'serpent_offers_god_wager_participation']
        if not offers:
            raise RuntimeError('God has not been offered participation.')
        offers[-1]['accepted'] = True
        wager = self.serpent_lilith_drink_wager
        wager.add_participant(
            participant='god',
            wager_type='three_way_drink_wager'
        )
        self.god.bar_state.participates_in_drink_wager = (
            True
        )
        event = {'name': 'god_accepts_drink_wager', 'participant': 'god', 'participants': list(wager.participants), 'resolved': False}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def god_tastes_beer_and_understands_bitterness(self):
        event = {'name': 'god_tastes_beer_and_understands_bitterness', 'guest': 'god', 'drink': 'beer', 'assessment': {'good': None, 'not_so_bad': True}, 'understands': {'bitterness': True}, 'wine_conclusion': {'bitterness_belongs_in_wine': False}}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        self._entity_attr_setdefault(
            self.god,
            'bar_knowledge',
            BarGuestKnowledge()
        ).bitterness = BarTasteKnowledge(
            understood=True,
            example='beer',
        )
        discussion = self.serpent_lilith_good_drink_discussion
        discussion.current_hypothesis.bitterness = False
        return event

    def lilith_sips_lilith_and_reacts_to_beer(self):
        drink = self.lilith_order.final_drink
        if drink is None:
            raise RuntimeError('Lilith has no lilith to sip.')
        effects = drink.effects
        self.lilith.energy_j = getattr(self.lilith, 'energy_j', 0.0) + float(effects.get('energy_j', 0.0))
        self.lilith.creative_will = getattr(self.lilith, 'creative_will', 0.0) + float(effects.get('creative_will', 0.0))
        event = {'name': 'lilith_sips_lilith_and_reacts_to_beer', 'guest': 'lilith', 'drink': 'lilith', 'disagrees_beer_is_good': True, 'beer_conclusion': {'bitterness_allowed': True}, 'effects_applied': True}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        discussion = self.serpent_lilith_good_drink_discussion
        if discussion.beer_hypothesis is None:
            discussion.beer_hypothesis = (
                BarBeerHypothesis()
            )
        discussion.beer_hypothesis.bitterness = (
            'allowed'
        )
        discussion.beer_hypothesis.resolved = False
        return event

    def serpent_leaves_table_for_bar(self):
        if getattr(
            getattr(
                self.serpent,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'table':
            raise RuntimeError('Serpent is not at the table.')
        event = {'name': 'serpent_leaves_table_for_bar', 'guest': 'serpent', 'reason': 'nothing_good_left_to_drink', 'remaining_drink': 'bad_beer', 'from': 'table', 'to': 'bar_counter'}
        self.serpent.bar_state.location = 'bar_counter'
        self.serpent.bar_state.activity = 'at_bar'
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def lilith_and_god_continue_talking_at_table(self):
        if getattr(
            getattr(
                self.lilith,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'table':
            raise RuntimeError('Lilith is not at the table.')
        if getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'table':
            raise RuntimeError('God is not at the table.')
        event = {'name': 'lilith_and_god_continue_talking_at_table', 'participants': ['lilith', 'god'], 'serpent_present': False, 'new_conclusion': None}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def god_asks_who_will_decide_wager(self):
        if getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'table':
            raise RuntimeError('God is not at the table.')
        if getattr(
            getattr(
                self.lilith,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'table':
            raise RuntimeError('Lilith is not at the table.')
        event = {'name': 'god_asks_who_will_decide_wager', 'speaker': 'god', 'listener': 'lilith', 'question': 'who_decides_winner'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def lilith_proposes_participant_vote(self):
        wager = getattr(self, 'serpent_lilith_drink_wager', None)
        if wager is None:
            raise RuntimeError('Drink wager does not exist.')
        method = BarWagerDecisionMethod(
            type='participant_vote',
            voters=[
                'serpent',
                'lilith',
                'god',
            ],
            proposed=True,
            accepted=False,
        )
        wager.decision_method_proposal = method
        proposal = {'name': 'lilith_proposes_participant_vote', 'speaker': 'lilith', 'decision_method': method.to_dict()}
        self.meeting_place.emit_event(proposal)
        self.history.append(proposal)
        return proposal

    def serpent_orders_water_at_bar(self):
        if getattr(
            getattr(
                self.serpent,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'bar_counter':
            raise RuntimeError('Serpent is not at the bar.')
        order = {'name': 'serpent_orders_water', 'guest': 'serpent', 'drink': 'water'}
        self.meeting_place.emit_event(order)
        self.history.append(order)
        self.serpent.bar_state.water_order = (
            BarDrinkOrder(
                guest='serpent',
                drink='water',
                tasted=False,
            )
        )
        return order

    def bartender_serves_serpent_water_with_free_lemon_slice(self):
        order = getattr(
            getattr(
                self.serpent,
                'bar_state',
                None
            ),
            'water_order',
            None
        )
        if order is None:
            raise RuntimeError('Serpent has not ordered water.')
        lemon = self.meeting_place.back_room.bar_ingredients.get('lemon')
        if lemon is None or lemon.shots < 1:
            return self.universe.create_cronenberg_from_quantum_error(error=RuntimeError('No lemon available for water garnish.'), source_component='meeting_place', source_operation='bartender_serves_serpent_water')
        drink = BarDrink(
            name='water_with_lemon_slice',
            type='basic_bar_drink',
            category='basic_drink',
            base='water',
            garnish={
                'ingredient': 'lemon',
                'amount': 'slice',
                'price': 0,
            },
            price_basis='water',
        )
        order.complete(
            drink
        )
        self.serpent.bar_state.drink = drink
        self.serpent.bar_state.activity = 'holding_water'
        event = {'name': 'bartender_serves_serpent_water_with_free_lemon_slice', 'guest': 'serpent', 'drink': 'water', 'lemon_slice': True, 'lemon_slice_price': 0, 'whole_lemon_consumed': False}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return {'drink': drink, 'event': event}

    def god_rejects_participant_vote_and_proposes_bartender(self):
        wager = self.serpent_lilith_drink_wager
        proposal = wager.decision_method_proposal
        if proposal is None:
            raise RuntimeError('Lilith has not proposed participant voting.')
        event = {'name': 'god_rejects_participant_vote_and_proposes_bartender', 'speaker': 'god', 'rejects': {'type': 'participant_vote'}, 'proposes': {'type': 'bartender_judges', 'judge': 'bartender'}}
        wager.bartender_judge_proposal = (
            BarWagerDecisionMethod(
                type='bartender_judges',
                judge='bartender',
                proposed_by='god',
                accepted=False,
            )
        )
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def lilith_and_god_leave_table_for_bar(self):
        if getattr(
            getattr(
                self.lilith,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'table':
            raise RuntimeError('Lilith is not at the table.')
        if getattr(
            getattr(
                self.god,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'table':
            raise RuntimeError('God is not at the table.')
        self.lilith.bar_state.location = 'bar_counter'
        self.lilith.bar_state.activity = 'at_bar'
        self.god.bar_state.location = 'bar_counter'
        self.god.bar_state.activity = 'at_bar'
        event = {'name': 'lilith_and_god_move_to_bar', 'guests': ['lilith', 'god'], 'from': 'table', 'to': 'bar_counter'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def lilith_explains_wager_and_bartender_judge_proposal(self):
        wager = self.serpent_lilith_drink_wager
        bartender_proposal = (
            wager.bartender_judge_proposal
        )
        if bartender_proposal is None:
            raise RuntimeError('God has not proposed bartender as judge.')
        event = {'name': 'lilith_explains_wager_and_bartender_judge_proposal', 'speaker': 'lilith', 'listener': 'bartender', 'wager': {'participants': list(wager.participants), 'contest': ['wine', 'mead', 'beer']}, 'proposal': {'judge': 'bartender'}}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def serpent_objects_single_bartender_is_not_enough(self):
        event = {'name': 'serpent_objects_single_judge_is_not_enough', 'speaker': 'serpent', 'single_judge': 'bartender', 'objection': 'one_judge_is_not_enough'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def bartender_proposes_bouncer_as_second_taster(self):
        wager = self.serpent_lilith_drink_wager
        proposal = BarWagerDecisionMethod(
            type='tasting_panel',
            judges=[
                'bartender',
                'bouncer',
            ],
            proposed_by='bartender',
            accepted=False,
        )
        wager.tasting_panel_proposal = proposal
        event = {'name': 'bartender_proposes_bouncer_as_second_taster', 'speaker': 'bartender', 'proposal': proposal.to_dict()}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def cat_d20_arrives_during_judge_discussion(self):
        result = self.meeting_place.welcome_cat_d20()
        cat = result.get('cat')
        if cat is None:
            raise RuntimeError('CatD20 arrival returned no cat.')
        self.cat_d20 = cat
        event = {'name': 'cat_d20_arrives_during_judge_discussion', 'cat': cat.name, 'current_layer': getattr(cat, 'current_layer', None), 'state': getattr(cat, 'state', None)}
        self.history.append(event)
        return {'arrival': result, 'event': event, 'cat': cat}

    def wager_participants_accept_two_judge_panel(self):
        wager = self.serpent_lilith_drink_wager
        proposal = wager.tasting_panel_proposal
        if proposal is None:
            raise RuntimeError('Bartender+bouncer panel was not proposed.')
        approvals = ['lilith', 'god', 'serpent']
        proposal.accept(
            participants=approvals
        )
        wager.decision_method = (
            BarWagerDecisionMethod(
                type='tasting_panel',
                judges=[
                    'bartender',
                    'bouncer',
                ],
            )
        )
        event = {'name': 'wager_participants_accept_two_judge_panel', 'accepted_by': approvals, 'judges': ['bartender', 'bouncer']}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def bartender_suggests_inviting_bouncer_inside(self):
        proposal = (
            self.serpent_lilith_drink_wager
            .tasting_panel_proposal
        )
        if proposal is None or not proposal.accepted:
            raise RuntimeError('Two-judge panel has not been accepted.')
        event = {'name': 'bartender_suggests_inviting_bouncer_inside', 'speaker': 'bartender', 'invite': 'bouncer', 'purpose': 'agree_on_wager_judging', 'bouncer_entered': False}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return event

    def everyone_scratches_cat_d20(self):
        if self.cat_d20 is None:
            raise RuntimeError('CatD20 is not in the bar.')
        scratchers = ['serpent', 'lilith', 'god', 'bartender']
        events = []
        for scratcher in scratchers:
            event = {'name': 'cat_d20_scratched', 'cat': 'cat_d20', 'scratched_by': scratcher, 'pleasant': True}
            self.meeting_place.emit_event(event)
            self.history.append(event)
            events.append(event)
        _entity_attr_setdefault(self.cat_d20, 'social_state', {})['scratched_by'] = list(scratchers)
        return events

    def cat_d20_sets_next_birth_to_garfield(self):
        if self.cat_d20 is None:
            raise RuntimeError('CatD20 does not exist.')
        resolver = CatBirthResolver(self.universe, self.meeting_place)
        garfield_profile = dict(resolver.garfield_profile)
        _entity_attr_setdefault(self.cat_d20, 'cat_d20', {})
        self.cat_d20.cat_d20['canonical_target'] = 'garfield'
        self.cat_d20.cat_d20['canonical_profile'] = dict(garfield_profile)
        self.cat_d20.cat_d20['garfield_pending'] = True
        event = {'name': 'cat_d20_sets_next_birth_to_garfield', 'cat': 'cat_d20', 'target_name': 'garfield', 'profile': dict(garfield_profile), 'pending': True}
        if not hasattr(self.meeting_place, 'cat_d20_secret_history'):
            self.meeting_place.cat_d20_secret_history = []
        self.meeting_place.cat_d20_secret_history.append(dict(event))
        self.universe.quantum_events.append(dict(event))
        self.history.append(event)
        return event

    def garfield_arrives_from_cat_d20_setting(self):
        cat_d20_state = getattr(self.cat_d20, 'cat_d20', {})
        if not cat_d20_state.get('garfield_pending', False):
            raise RuntimeError('CatD20 has not prepared Garfield.')
        if cat_d20_state.get('canonical_target') != 'garfield':
            raise RuntimeError('CatD20 target is not Garfield.')
        profile = dict(cat_d20_state['canonical_profile'])
        cats_layer = getattr(self.universe, 'cats_layer', None)
        if cats_layer is None:
            raise RuntimeError('Garfield arrival requires cats_layer.')

        def cat_name_of(cat):
            return getattr(cat, 'name', None)
        existing = next((cat for cat in cats_layer.cats if cat_name_of(cat) == 'garfield'), None)
        created = False
        if existing is not None:
            garfield = existing
        else:
            manifestation = self.universe.manifest_cat(name='garfield', source='cat_d20_garfield_setting', color=profile['color'], fur_length=profile['fur_length'], pattern=profile['pattern'], eye_color=profile['eye_color'], sex=profile['sex'])
            if manifestation is None:
                raise RuntimeError('Garfield manifestation failed.')
            garfield = manifestation['cat']
            created = True
        traits = getattr(
            garfield,
            'special_traits',
            None
        )
        if traits is None:
            garfield.special_traits = []
            traits = garfield.special_traits

        garfield.canonical_identity = 'garfield'
        for trait in ('garfield', 'canonical_cat_garfield'):
            if trait not in traits:
                traits.append(trait)
        ordinary_arrival = self.meeting_place.admit_cat(garfield, bartender_available=True)
        cat_d20_state['garfield_pending'] = False
        cat_d20_state['last_manifested_target'] = 'garfield'
        self.garfield = garfield
        event = {'name': 'garfield_arrives_at_bar', 'cat': 'garfield', 'source': 'cat_d20', 'created': created, 'arrival': ordinary_arrival}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return {'garfield': garfield, 'event': event, 'profile': profile, 'ordinary_arrival': ordinary_arrival}

    def bouncer_enters_bar_with_garfield(self):
        bouncer = self.meeting_place.bouncer
        locations = ['outside_bar', 'inside_bar']
        bouncer.locations = list(locations)
        bouncer.location = 'dual_presence'
        bouncer.state = 'inside_and_outside_bar'
        bouncer.guards_entrance = True
        bouncer.present_in_bar = True
        event = {'name': 'bouncer_enters_bar_with_garfield', 'bouncer': 'bouncer', 'with': 'garfield', 'locations': list(locations), 'still_guards_entrance': True, 'present_inside': True, 'purpose': 'discuss_wager_judging'}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        proposal = (
            self.serpent_lilith_drink_wager
            .tasting_panel_proposal
        )
        if proposal is not None:
            proposal.bouncer_present = True
        return event

    def serpent_explains_wager_to_bouncer(self):
        bouncer = self.meeting_place.bouncer
        present_inside = getattr(
            bouncer,
            'present_in_bar',
            False
        )
        if not present_inside:
            raise RuntimeError('Bouncer is not present inside the bar.')
        wager = self.serpent_lilith_drink_wager
        event = {'name': 'serpent_explains_wager_to_bouncer', 'speaker': 'serpent', 'listener': 'bouncer', 'participants': list(wager.participants), 'contest': ['wine', 'mead', 'beer'], 'proposed_judges': ['bartender', 'bouncer']}
        self.meeting_place.emit_event(event)
        self.history.append(event)
        bouncer.wager_knowledge = (
            BarWagerKnowledge(
                known=True,
                source='serpent',
            )
        )
        return event

    def everyone_scratches_garfield(self):
        if self.garfield is None:
            raise RuntimeError('Garfield is not present.')
        actors = [self.serpent, self.lilith, self.god, self.meeting_place.bartender, self.meeting_place.bouncer]
        events = []
        for actor in actors:
            event = actor.pet_cat(self.garfield)
            self.meeting_place.emit_event(event)
            self.history.append(event)
            events.append(event)
        return events

    def bouncer_orders_tasting_drinks(self):
        bouncer = self.meeting_place.bouncer
        drink_names = ['wine', 'mead', 'beer']
        self.meeting_place.refresh_basic_drinks()
        drinks = []
        for drink_name in drink_names:
            menu_item = self.meeting_place.drink_menu.get(drink_name)
            if menu_item is None:
                raise RuntimeError(f'{drink_name} is not available.')
            drink = BarDrink(
                name=drink_name,
                type='basic_bar_drink',
                category='basic_drink',
            )
            drinks.append(drink)
        order_event = {'name': 'bouncer_orders_tasting_drinks', 'bouncer': 'bouncer', 'drinks': list(drink_names), 'purpose': 'judge_wager'}
        self.meeting_place.emit_event(order_event)
        self.history.append(order_event)
        receipt = self.meeting_place.bar_counter.cash_register.print_staff_purchase_receipt(entity=bouncer, drinks=drinks)
        served_event = {'name': 'bartender_serves_bouncer_tasting_drinks', 'bartender': 'bartender', 'bouncer': 'bouncer', 'drinks': list(drink_names), 'receipt_number': receipt['receipt_number'], 'receipt_kind': 'staff_purchase', 'paid': False, 'charge': 0}
        self.meeting_place.emit_event(served_event)
        self.history.append(served_event)
        return {'drinks': drinks, 'receipt': receipt, 'order_event': order_event, 'served_event': served_event}

    def bouncer_tastes_and_accepts_judge_role(self, service):
        tasting_events = []
        for drink_name in ('wine', 'mead', 'beer'):
            event = {'name': 'bouncer_tastes_drink', 'bouncer': 'bouncer', 'drink': drink_name, 'purpose': 'judge_wager'}
            self.meeting_place.emit_event(event)
            self.history.append(event)
            tasting_events.append(event)
        verdict = {'name': 'bouncer_gives_initial_drink_verdict', 'bouncer': 'bouncer', 'drinks': ['wine', 'mead', 'beer'], 'verdict': 'disgusting', 'statement': 'this_is_disgusting'}
        self.meeting_place.emit_event(verdict)
        self.history.append(verdict)
        accepted = {'name': 'bouncer_accepts_wager_judge_role', 'bouncer': 'bouncer', 'role': 'tasting_judge', 'accepted': True}
        self.meeting_place.emit_event(accepted)
        self.history.append(accepted)
        proposal = (
            self.serpent_lilith_drink_wager
            .tasting_panel_proposal
        )
        if proposal is not None:
            proposal.bouncer_accepted = True
        bouncer = self.meeting_place.bouncer
        bouncer.wager_judge = True
        return {'tastings': tasting_events, 'verdict': verdict, 'accepted': accepted, 'receipt': service['receipt']}

    def advance_to_bouncer_accepts_judge_role(self):
        previous = self.advance_to_bouncer_knows_wager()
        scratches = self.everyone_scratches_garfield()
        service = self.bouncer_orders_tasting_drinks()
        tasting = self.bouncer_tastes_and_accepts_judge_role(service)
        return {'previous': previous, 'garfield_scratches': scratches, 'service': service, 'tasting': tasting}

    def advance_to_bouncer_knows_wager(self):
        previous = self.advance_to_bouncer_inside_after_garfield()
        explanation = self.serpent_explains_wager_to_bouncer()
        return {'previous': previous, 'explanation': explanation}

    def advance_to_bouncer_inside_after_garfield(self):
        previous = self.advance_to_garfield_arrival()
        bouncer = self.bouncer_enters_bar_with_garfield()
        return {'previous': previous, 'bouncer': bouncer}

    def advance_to_garfield_arrival(self):
        previous = self.advance_to_cat_d20_arrival()
        accepted = self.wager_participants_accept_two_judge_panel()
        invite = self.bartender_suggests_inviting_bouncer_inside()
        scratches = self.everyone_scratches_cat_d20()
        prepared = self.cat_d20_sets_next_birth_to_garfield()
        garfield = self.garfield_arrives_from_cat_d20_setting()
        return {'previous': previous, 'accepted': accepted, 'invite': invite, 'scratches': scratches, 'prepared': prepared, 'garfield': garfield}

    def advance_to_cat_d20_arrival(self):
        previous = self.advance_to_bartender_bouncer_panel_proposal()
        cat_d20 = self.cat_d20_arrives_during_judge_discussion()
        return {'previous': previous, 'cat_d20': cat_d20}

    def advance_to_bartender_bouncer_panel_proposal(self):
        previous = self.advance_to_everyone_at_bar_with_serpents_water()
        explanation = self.lilith_explains_wager_and_bartender_judge_proposal()
        objection = self.serpent_objects_single_bartender_is_not_enough()
        panel = self.bartender_proposes_bouncer_as_second_taster()
        return {'previous': previous, 'explanation': explanation, 'objection': objection, 'panel': panel}

    def advance_to_everyone_at_bar_with_serpents_water(self):
        previous = self.advance_to_wager_vote_proposal()
        water_order = self.serpent_orders_water_at_bar()
        judge_proposal = self.god_rejects_participant_vote_and_proposes_bartender()
        move = self.lilith_and_god_leave_table_for_bar()
        water = self.bartender_serves_serpent_water_with_free_lemon_slice()
        return {'previous': previous, 'water_order': water_order, 'judge_proposal': judge_proposal, 'move': move, 'water': water}

    def advance_to_wager_vote_proposal(self):
        previous = self.advance_to_serpent_at_bar_lilith_with_god()
        question = self.god_asks_who_will_decide_wager()
        proposal = self.lilith_proposes_participant_vote()
        return {'previous': previous, 'question': question, 'proposal': proposal}

    def advance_to_serpent_at_bar_lilith_with_god(self):
        previous = self.advance_to_bitterness_split_between_wine_and_beer()
        serpent = self.serpent_leaves_table_for_bar()
        conversation = self.lilith_and_god_continue_talking_at_table()
        return {'previous': previous, 'serpent': serpent, 'conversation': conversation}

    def advance_to_bitterness_split_between_wine_and_beer(self):
        previous = self.advance_to_three_way_drink_wager()
        god_beer = self.god_tastes_beer_and_understands_bitterness()
        lilith = self.lilith_sips_lilith_and_reacts_to_beer()
        return {'previous': previous, 'god_beer': god_beer, 'lilith': lilith}

    def advance_to_three_way_drink_wager(self):
        previous = self.advance_to_god_understands_sweetness()
        explained = self.serpent_tells_god_about_drink_wager()
        offered = self.serpent_offers_god_wager_participation()
        accepted = self.god_accepts_drink_wager()
        return {'previous': previous, 'explained': explained, 'offered': offered, 'accepted': accepted}

    def advance_to_god_understands_sweetness(self):
        previous = self.advance_to_balanced_acidity_idea()
        wine = self.god_tastes_existing_wine_and_rejects_it()
        explanation = self.lilith_explains_sweetness_to_god()
        mead = self.god_finishes_serpents_mead_and_understands_sweetness()
        return {'previous': previous, 'wine': wine, 'explanation': explanation, 'mead': mead}

    def advance_to_balanced_acidity_idea(self):
        previous = self.advance_to_god_receives_wine()
        balance = self.serpent_agrees_with_acidity_but_wants_balance()
        return {'previous': previous, 'balance': balance}

    def advance_to_god_receives_wine(self):
        previous = self.advance_to_acidity_wine_idea()
        reaction = self.serpent_grimaces_at_lilith_and_turns_to_god()
        order = self.god_orders_wine_to_judge_discussion()
        service = self.bartender_serves_god_wine_and_receipt()
        return {'previous': previous, 'reaction': reaction, 'order': order, 'service': service}

    def advance_to_acidity_wine_idea(self):
        previous = self.advance_to_god_at_table()
        explained = self.serpent_explains_wine_discussion_to_god()
        revised = self.lilith_rejects_bitterness_and_proposes_acidity()
        tasted = self.lilith_gives_serpent_taste_of_lilith()
        return {'previous': previous, 'explained': explained, 'revised': revised, 'tasted': tasted}

    def advance_to_god_at_table(self):
        previous = self.advance_to_god_first_lilith_taste()
        called = self.serpent_notices_god_and_calls_him_over()
        joined = self.god_joins_serpent_and_lilith_at_table()
        return {'previous': previous, 'called': called, 'joined': joined}

    def advance_to_god_first_lilith_taste(self):
        previous = self.advance_to_god_holding_lilith()
        tasting = self.god_tastes_lilith()
        return {'previous': previous, 'tasting': tasting}

    def advance_to_god_holding_lilith(self):
        previous = self.advance_to_lemon_restock_after_god_order()
        drink = self.bartender_mixes_gods_lilith_after_restock()
        service = self.bartender_serves_gods_lilith_with_receipt()
        return {'previous': previous, 'drink': drink, 'service': service}

    def advance_to_lemon_restock_after_god_order(self):
        state = self.advance_to_third_wine_idea()
        failure = self.bartender_attempts_gods_lilith_without_lemon()
        restock = self.bartender_runs_to_yard_for_more_lemons(amount=6)
        return {'previous': state, 'failure': failure, 'restock': restock}

    def advance_to_third_wine_idea(self):
        self.advance_to_second_wine_idea()
        god_order = self.god_finishes_browsing_and_orders_lilith()
        tasting = self.serpent_tastes_mead_then_beer()
        idea = self.serpent_adds_bitterness_as_wine_idea()
        return {'god_order': god_order, 'tasting': tasting, 'wine_idea': idea}

    def advance_to_second_wine_idea(self):
        self.advance_to_god_browsing_menu()
        asked = self.bartender_asks_god_for_order()
        answer = self.god_says_still_choosing()
        wine_idea = self.lilith_tastes_mead_and_adds_sweetness_idea()
        return {'bartender': asked, 'god': answer, 'wine_idea': wine_idea}

    def advance_to_god_browsing_menu(self):
        self.advance_to_good_drink_discussion()
        self.lilith_and_serpent_take_first_table_drinks()
        self.lilith_and_serpent_make_first_wine_observation()
        self.god_arrives_after_first_wine_observation()
        looked = self.god_looks_around_bar()
        continued = self.serpent_and_lilith_continue_wine_discussion()
        browsed = self.god_moves_to_drink_menu()
        return {'looked': looked, 'continued': continued, 'browsed': browsed}

    def serpent_and_lilith_begin_good_drink_discussion(self):
        if self.serpent.bar_state.location != 'table':
            raise RuntimeError('Serpent is not at table.')
        if getattr(
            getattr(
                self.lilith,
                'bar_state',
                None
            ),
            'location',
            None
        ) != 'table':
            raise RuntimeError('Lilith is not at table.')
        discussion = BarDrinkDiscussion()
        self.serpent_lilith_good_drink_discussion = discussion
        event = discussion.to_dict()
        self.meeting_place.emit_event(event)
        self.history.append(event)
        return discussion

    def advance_to_good_drink_discussion(self):
        self.advance_to_lilith_entry()
        self.lilith_orders_vodka_with_lemon()
        self.serpent_and_lilith_begin_conversation()
        self.play_serpent_lilith_first_conversation()
        self.serpent_and_lilith_agree_on_table()
        self.serpent_moves_from_bar_to_existing_table()
        self.bartender_returns_with_lemon()
        self.bartender_makes_vodka_with_lemon()
        self.lilith_corrects_vodka_with_lemon()
        self.bartender_learns_lilith_drink()
        served = self.bartender_hands_lilith_drink_and_receipt()
        tasted = self.lilith_tastes_and_requests_second_sugar_cube()
        revised = self.bartender_adds_second_sugar_cube()
        moved = self.lilith_joins_serpent_at_existing_table()
        discussion = self.serpent_and_lilith_begin_good_drink_discussion()
        return {'served': served, 'tasted': tasted, 'revised': revised, 'moved': moved, 'discussion': discussion}

    def advance_to_lilith_drink_learned(self):
        self.advance_to_lilith_entry()
        self.lilith_orders_vodka_with_lemon()
        self.serpent_and_lilith_begin_conversation()
        self.play_serpent_lilith_first_conversation()
        self.serpent_and_lilith_agree_on_table()
        self.serpent_moves_from_bar_to_existing_table()
        returned = self.bartender_returns_with_lemon()
        vodka_with_lemon = self.bartender_makes_vodka_with_lemon()
        correction = self.lilith_corrects_vodka_with_lemon()
        learned = self.bartender_learns_lilith_drink()
        return {'returned': returned, 'vodka_with_lemon': vodka_with_lemon, 'correction': correction, 'learned': learned}

    def advance_to_first_private_conversation(self):
        state = self.advance_to_lilith_entry()
        self.lilith_orders_vodka_with_lemon()
        conversation = self.serpent_and_lilith_begin_conversation()
        return {'previous_checkpoint': state, 'current': self.checkpoint(), 'conversation': conversation}

    def lilith_is_born_and_enters_bar(self):
        self.lilith = self.idea_entities.create_idea_entity(name='lilith', role='archetype_principle', active=True)
        self.lilith.principle = {'name': 'feminine_principle', 'domain': ['woman', 'creation', 'feminine_archetype'], 'origin': 'lilith'}
        self.lilith.access = {'meeting_place': True, 'library': 'read', 'quantum_layer': 'via_meeting_place'}
        self.universe.world['lilith'] = self.lilith
        self.history.append({'name': 'lilith_born'})
        self.meeting_place.add_entity(self.lilith)
        self.history.append({'name': 'lilith_entered_bar'})
        return self.lilith

    def advance_to_lilith_entry(self):
        self.start_shift()
        self.serpent_is_born_and_enters()
        self.serpent_orders_first_drinks()
        self.serpent_proposes_bet()
        self.god_is_born_and_goes_to_library()
        self.lilith_is_born_and_enters_bar()
        return self.checkpoint()

    def checkpoint(self):
        serpent_tab = None
        serpent_bar_state = None
        if self.serpent is not None:
            serpent_tab = self.meeting_place.bar_counter.cash_register.open_tabs.get('serpent')
            serpent_bar_state = getattr(
                self.serpent,
                'bar_state',
                None
            )
        return {'bar_time': self.meeting_place.bar_clock.time_text, 'shift_active': getattr(self.meeting_place.bartender, 'shift_active', False), 'serpent': {'exists': self.serpent is not None, 'in_bar': self.serpent in self.meeting_place.entities if self.serpent is not None else False, 'bar_state': serpent_bar_state.to_dict() if serpent_bar_state is not None else None, 'tab': serpent_tab.to_dict() if serpent_tab is not None else None}, 'god': {'exists': self.god is not None, 'in_library': self.library.god_present if self.god is not None else False, 'role': getattr(self.god, 'role', None) if self.god is not None else None, 'book': self.first_book}, 'lilith': {'exists': self.lilith is not None, 'in_bar': self.lilith in self.meeting_place.entities if self.lilith is not None else False}, 'history': list(self.history)}
