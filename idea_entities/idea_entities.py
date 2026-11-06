from copy import deepcopy
from core.entity.departure_state import EntityDepartureIntent
from core.entity.world_existence_state import (
    WorldExistenceState,
)
from core.entity.social_entity import SocialEntity
from universe.pre_cosmic_rules import IDEA_ENTITY_INITIAL_ENERGY_J, IDEA_ENTITY_ARCHETYPE_EXISTENCE_THRESHOLD_PCT
from universe.logger import UniverseLogger
from core.entity.serpent_d20 import SerpentD20
from idea_entities.idea_actor_state import IdeaPrePhysicalAttributes
from idea_entities.idea_entities_state import IdeaEntitiesState
from idea_entities.idea_event_state import IdeaEntityEvent
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
        # Export a point-in-time projection.
        # Domain event collections remain owned by
        # the canonical IdeaEntitiesState object.
        state_snapshot = self.idea_entities_state.to_dict()

        return {
            'type': self.idea_entities_state.layer_type,
            'state': self.idea_entities_state.status,
            'idea_entities': list(self.idea_entities),
            'eternal_fire': self.eternal_fire.to_dict(),
            'serpent_d20': self.serpent_d20.public_state,
            'prefysical_fire_origin': (
                self.prefysical_fire_origin.public_state
            ),
            'events': deepcopy(state_snapshot['events']),
            'event_history': deepcopy(
                state_snapshot['event_history']
            ),
            'permissions': self.permissions.to_dict(),
            'idea_entities_state': state_snapshot,
        }

    def write_to_world(self):
        self.universe.world['idea_entities'] = self.public_state

        # The canonical runtime state belongs to IdeaEntities.
        # Remove any legacy world alias on projection refresh.
        self.universe.world.pop('idea_entities_state', None)

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
            existence_by_world = WorldExistenceState.of(
                idea_universe=existence_pct,
                root_universe=0.0,
                eden=0.0,
            )
        elif not isinstance(
            existence_by_world,
            WorldExistenceState,
        ):
            raise TypeError(
                "Idea entity existence requires "
                "WorldExistenceState."
            )
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
        if not isinstance(event, IdeaEntityEvent):
            raise TypeError(
                "Idea Entities events require "
                "IdeaEntityEvent objects."
            )

        self.events.append(event)
        self.event_history.append(event)
        self.write_to_world()
        UniverseLogger.event(f'IDEA ENTITIES EVENT: {event}')

    def record_idea_event(self, name, participants, observer=None, state='unresolved', meaning=None):
        event = IdeaEntityEvent(
            name=name,
            participants=tuple(participants),
            observer=observer,
            state=state,
            meaning=meaning,
        )
        self.emit_event(event)
        return event

    def record_fire_interaction(self, name, participants, observer=None, state='unresolved', meaning=None):
        interaction = IdeaEntityEvent(
            name=name,
            participants=tuple(participants),
            observer=observer,
            state=state,
            meaning=meaning,
            place="eternal_fire",
        )
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
