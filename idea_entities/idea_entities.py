from core.entity.departure_state import EntityDepartureIntent
from core.entity.social_entity import SocialEntity
from universe.pre_cosmic_rules import IDEA_ENTITY_INITIAL_ENERGY_J, IDEA_ENTITY_ARCHETYPE_EXISTENCE_THRESHOLD_PCT
from universe.logger import UniverseLogger
from core.entity.serpent_d20 import SerpentD20
from idea_entities.idea_actor_state import IdeaPrePhysicalAttributes
from idea_entities.idea_entities_state import IdeaEntitiesState
from idea_entities.prefysical_fire_origin import PrefysicalFireOrigin

class IdeaEntities:

    def __init__(self, universe):
        self.universe = universe
        self.idea_entities_state = IdeaEntitiesState()
        self.state = self.idea_entities_state
        self.serpent_d20 = SerpentD20()
        self.prefysical_fire_origin = PrefysicalFireOrigin(eternal_fire=self.eternal_fire, serpent_d20=self.serpent_d20, universe=self.universe)
        self.write_to_world()
        UniverseLogger.boot('IDEA ENTITIES LAYER CREATED')

    @property
    def idea_entities(self):
        return self.idea_entities_state.idea_entities

    @property
    def events(self):
        return self.idea_entities_state.events

    @property
    def event_history(self):
        return self.idea_entities_state.event_history

    @property
    def tick_count(self):
        return self.idea_entities_state.tick_count

    @tick_count.setter
    def tick_count(self, value):
        self.idea_entities_state.tick_count = value

    @property
    def eternal_fire(self):
        return self.idea_entities_state.eternal_fire

    @property
    def permissions(self):
        return self.idea_entities_state.permissions

    @property
    def public_state(self):
        return {
            'type': self.idea_entities_state.layer_type,
            'state': self.idea_entities_state.status,
            'idea_entities': self.idea_entities,
            'eternal_fire': self.eternal_fire.to_dict(),
            'serpent_d20': self.serpent_d20.public_state,
            'prefysical_fire_origin': self.prefysical_fire_origin.public_state,
            'events': self.events,
            'event_history': self.event_history,
            'permissions': self.permissions,
            'idea_entities_state': self.idea_entities_state.to_dict()
        }

    def write_to_world(self):
        self.universe.world['idea_entities'] = self.public_state
        self.universe.world['idea_entities_state'] = (
            self.idea_entities_state
        )

    def update_archetype_manifestation_state(self, entity):
        existence_pct = getattr(entity, 'existence_pct', 0.0)
        threshold_pct = getattr(entity, 'archetype_manifestation_threshold_pct', IDEA_ENTITY_ARCHETYPE_EXISTENCE_THRESHOLD_PCT)
        possible = existence_pct >= threshold_pct
        entity.archetype_manifestation_possible = possible
        if possible:
            entity.archetype_manifestation_state = 'root_archetype_possible'
        else:
            entity.archetype_manifestation_state = 'not_enough_existence'
        return possible

    def create_idea_entity(self, name, role='primordial_idea_entity', active=False, existence_pct=0.0, native_world='idea_universe', existence_by_world=None):
        if existence_by_world is None:
            existence_by_world = {'idea_universe': existence_pct, 'root_universe': 0.0, 'eden': 0.0}
        idea_entity = SocialEntity(
            name=name,
            type='idea_entity',
            role=role,
            state='created',
            active=active,
            forbidden=False,
            existence_pct=existence_pct,
            native_world=native_world,
            existence_by_world=existence_by_world,
            departure_intent=EntityDepartureIntent(),
            will=0.0,
            energy_j=IDEA_ENTITY_INITIAL_ENERGY_J,
            idea_capacity=0.0,
            archetype_manifestation_possible=False,
            archetype_manifestation_state='not_enough_existence',
            archetype_manifestation_threshold_pct=(
                IDEA_ENTITY_ARCHETYPE_EXISTENCE_THRESHOLD_PCT
            ),
            pre_physical_attributes=IdeaPrePhysicalAttributes(),
            permissions=self.permissions,
        )
        self.idea_entities.append(idea_entity)
        self.write_to_world()
        UniverseLogger.event(f'IDEA ENTITY CREATED: {name}')
        return idea_entity

    def emit_event(self, event):
        self.events.append(event)
        self.event_history.append(event)
        self.write_to_world()
        UniverseLogger.event(f'IDEA ENTITIES EVENT: {event}')

    def record_idea_event(self, name, participants, observer=None, state='unresolved', meaning=None):
        event = {'name': name, 'layer': 'idea_entities', 'participants': participants, 'observer': observer, 'state': state, 'meaning': meaning, 'known_by': []}
        if observer is not None:
            event['known_by'].append(observer)
        self.emit_event(event)
        return event

    def record_fire_interaction(self, name, participants, observer=None, state='unresolved', meaning=None):
        interaction = {'name': name, 'layer': 'idea_entities', 'place': 'eternal_fire', 'participants': participants, 'observer': observer, 'state': state, 'meaning': meaning, 'known_by': []}
        if observer is not None:
            interaction['known_by'].append(observer)
        self.eternal_fire.interactions.append(interaction)
        self._refresh_eternal_fire_boundary()
        self.emit_event(interaction)
        return interaction

    def _refresh_eternal_fire_boundary(self):
        self.universe.world['idea_entities']['eternal_fire'] = (
            self.eternal_fire.to_dict()
        )
        self.universe.world['idea_entities'][
            'idea_entities_state'
        ] = self.idea_entities_state.to_dict()

    def tick(self):
        self.tick_count += 1
        UniverseLogger.event(f'IDEA ENTITIES TICK {self.tick_count}')
        self._clear_events()

    def _clear_events(self):
        self.events.clear()
        self.write_to_world()
