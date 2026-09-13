from library.god_book import GodBook
from core.entity.social_entity import _entity_attr_setdefault
from core.entity.social_entity import SocialEntity
from gods.gods_state import GodsState
from universe.pre_cosmic_rules import GOD_INITIAL_ENERGY_J
from universe.logger import UniverseLogger

class Gods:

    def __init__(self, universe):
        self.universe = universe
        self.gods_state = GodsState()
        self.state = self.gods_state

        self.write_to_world()
        UniverseLogger.boot('GODS LAYER CREATED')

    @property
    def gods(self):
        return self.gods_state.gods

    @property
    def events(self):
        return self.gods_state.events

    @property
    def tick_count(self):
        return self.gods_state.tick_count

    @tick_count.setter
    def tick_count(self, value):
        self.gods_state.tick_count = value

    @property
    def permissions(self):
        return self.gods_state.permissions

    @property
    def public_state(self):
        return {
            'type': self.gods_state.layer_type,
            'state': self.gods_state.status,
            'gods': self.gods,
            'permissions': self.permissions,
            'gods_state': self.gods_state.to_dict(),
        }

    def write_to_world(self):
        self.universe.world['gods'] = self.public_state
        self.universe.world['gods_state'] = self.gods_state

    def create_god(self, name, role='god_entity'):
        god = SocialEntity.from_mapping({'name': name, 'type': 'god', 'role': role, 'state': 'present', 'active': True, 'forbidden': False, 'existence_pct': 100.0, 'native_world': 'gods_layer', 'existence_by_world': {'gods_layer': 100.0, 'idea_universe': 100.0, 'root_universe': 0.0, 'eden': 0.0}, 'departure_intent': {'wants_to_leave': False}, 'creative_will': 0.0, 'energy_j': GOD_INITIAL_ENERGY_J, 'creation_capacity': 0.0, 'divine_attributes': {'aseity': True, 'eternity': True, 'transcendence': True, 'immanence': True, 'creative_authority': 'potential', 'sovereignty': 'potential', 'providence': 'potential', 'omniscience': 'potential', 'omnipotence': 'potential', 'omnipresence': 'potential', 'immutability': 'limited_by_story_state', 'simplicity': 'symbolic', 'perfect_goodness': 'not_assumed'}, 'creation_limits': {'limited_by_existence_pct': True, 'limited_by_creative_will': True, 'limited_by_current_reality_rules': True}, 'permissions': self.permissions, 'created_entities': [], 'administers': [], 'book_created': False})
        self.gods.append(god)
        self.write_to_world()
        UniverseLogger.event(f'GOD CREATED: {name}')
        return god

    def create_book(self, god):
        if getattr(god, 'type', None) != 'god':
            raise TypeError('God must be a god object entity.')
        if getattr(god, 'type', None) != 'god':
            raise ValueError('Only a god can create a god book.')
        if getattr(god, 'book_created', False):
            return god.book
        book = GodBook(
            author=god.name
        )
        god.book = book
        god.book_created = True
        event = {'name': 'god_book_created', 'god': god.name, 'book': book}
        self.emit_event(event)
        UniverseLogger.event(f'GOD BOOK CREATED: {god.name}')
        return book

    def emit_event(self, event):
        self.events.append(event)
        self.write_to_world()
        UniverseLogger.event(f'GODS EVENT: {event}')

    def tick(self):
        self.tick_count += 1
        UniverseLogger.event(f'GODS TICK {self.tick_count}')
        self._clear_events()
        self.write_to_world()

    def _clear_events(self):
        self.events.clear()

    def assume_mask(self, god, mask_name, role):
        knowledge = _entity_attr_setdefault(god, 'knowledge', set())
        research_book = _entity_attr_setdefault(god, 'research_book', [])
        masks = _entity_attr_setdefault(god, 'masks', {})
        mask = SocialEntity.from_mapping({'name': mask_name, 'type': 'god_mask', 'role': role, 'active': True, 'mask_of': god, 'knowledge': knowledge, 'research_book': research_book})
        masks[mask_name] = mask
        god.active_mask = mask_name
        return mask

    def release_mask(self, god, mask_name):
        masks = getattr(god, 'masks', {})
        if mask_name not in masks:
            raise RuntimeError(f'Mask not found: {mask_name}')
        mask = masks[mask_name]
        mask.active = False
        if getattr(god, 'active_mask', None) == mask_name:
            god.active_mask = None
        return {'released_mask': mask_name, 'god': god, 'mask': mask}
