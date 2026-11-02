from idea_universe.idea_universe_state import IdeaUniverseState
from idea_universe.primordial_identity_cursor import (
    PrimordialIdentityCursor,
)
from idea_universe.primordial_creation_history import (
    PrimordialCreationHistory,
    PrimordialNebulaCreated,
    PrimordialRemnantCreation,
    PrimordialStarCreated,
    PrimordialStarTransition,
)
from idea_universe.primordial_idea_star_state import (
    PrimordialIdeaStarState,
)
from idea_universe.primordial_idea_star import PrimordialIdeaStar
from idea_universe.primordial_nebula import PrimordialNebula
from idea_universe.primordial_waters import PrimordialWaters
from idea_universe.primordial_stellar_state import (
    PrimordialStellarEpochResult,
)


class IdeaUniverse:

    def __init__(self, universe):
        self.universe = universe
        self.name = "idea_universe"
        self.type = "pre_physical_idea_reality"

        self.entities = []
        self.events = []
        self.starry_sky = []

        self.idea_universe_state = IdeaUniverseState()
        self.state = self.idea_universe_state

        registry = getattr(
            self.universe,
            "universe_registry",
            None,
        )

        if registry is None:
            raise RuntimeError(
                "Idea Universe requires UniverseRegistry"
            )

        self.universe_id = registry.register_universe(
            name=self.name,
            universe_type=self.type,
        )

        self._primordial_identity_cursor = (
            PrimordialIdentityCursor(
                scope=(
                    f"{self.universe.id}:"
                    f"idea_universe:{self.universe_id}"
                )
            )
        )

        self._primordial_creation_history = (
            PrimordialCreationHistory(
                scope=self.primordial_identity_cursor.scope
            )
        )

        self.primordial_waters = PrimordialWaters()
        self.primordial_nebula = None

        self.write_to_world()

        print("IDEA UNIVERSE INITIALIZED")

    def _set_state_value(self, name, value):
        setattr(
            self.idea_universe_state,
            name,
            value,
        )

        if "idea_universe" in self.universe.world:
            self.write_to_world()

    @property
    def status(self):
        return self.idea_universe_state.status

    @status.setter
    def status(self, value):
        self._set_state_value("status", value)

    @property
    def part_of_physics(self):
        return self.idea_universe_state.part_of_physics

    @part_of_physics.setter
    def part_of_physics(self, value):
        self._set_state_value("part_of_physics", value)

    @property
    def tick_count(self):
        return self.idea_universe_state.tick_count

    @tick_count.setter
    def tick_count(self, value):
        self._set_state_value("tick_count", value)

    @property
    def stellar_epoch_started(self):
        return self.idea_universe_state.stellar_epoch_started

    @stellar_epoch_started.setter
    def stellar_epoch_started(self, value):
        self._set_state_value(
            "stellar_epoch_started",
            value,
        )

    @property
    def heavenly_lights_created(self):
        return self.idea_universe_state.heavenly_lights_created

    @heavenly_lights_created.setter
    def heavenly_lights_created(self, value):
        self._set_state_value(
            "heavenly_lights_created",
            value,
        )

    @property
    def heaven_ordered(self):
        return self.idea_universe_state.heaven_ordered

    @heaven_ordered.setter
    def heaven_ordered(self, value):
        self._set_state_value("heaven_ordered", value)

    @property
    def celestial_stations_established(self):
        return (
            self
            .idea_universe_state
            .celestial_stations_established
        )

    @celestial_stations_established.setter
    def celestial_stations_established(self, value):
        self._set_state_value(
            "celestial_stations_established",
            value,
        )

    @property
    def divine_order_established(self):
        return self.idea_universe_state.divine_order_established

    @divine_order_established.setter
    def divine_order_established(self, value):
        self._set_state_value(
            "divine_order_established",
            value,
        )

    @property
    def aquatic_life_archetype(self):
        return self.idea_universe_state.aquatic_life_archetype

    @aquatic_life_archetype.setter
    def aquatic_life_archetype(self, value):
        self._set_state_value(
            "aquatic_life_archetype",
            value,
        )

    @property
    def flying_life_archetype(self):
        return self.idea_universe_state.flying_life_archetype

    @flying_life_archetype.setter
    def flying_life_archetype(self, value):
        self._set_state_value(
            "flying_life_archetype",
            value,
        )

    @property
    def land_life_archetype(self):
        return self.idea_universe_state.land_life_archetype

    @land_life_archetype.setter
    def land_life_archetype(self, value):
        self._set_state_value(
            "land_life_archetype",
            value,
        )

    @property
    def primordial_creation_history(self):
        return self._primordial_creation_history

    @property
    def primordial_identity_cursor(self):
        return self._primordial_identity_cursor

    def restore_primordial_identity_cursor(self, cursor):
        if not isinstance(cursor, PrimordialIdentityCursor):
            raise TypeError(
                "Replay requires PrimordialIdentityCursor."
            )

        current = self._primordial_identity_cursor

        if cursor.scope != current.scope:
            raise ValueError(
                "Replay identity scope does not match "
                "the target IdeaUniverse."
            )

        if (
            self.starry_sky
            or self.primordial_nebula is not None
            or current.star_serial != 0
            or current.nebula_serial != 0
        ):
            raise RuntimeError(
                "Identity cursor can be restored only "
                "into a fresh IdeaUniverse."
            )

        self._primordial_identity_cursor = cursor
        self.write_to_world()

        return cursor

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.status,
            "part_of_physics": self.part_of_physics,
            "primordial_waters": self.primordial_waters,
            "primordial_nebula": self.primordial_nebula,
            "entities": self.entities,
            "events": self.events,
            "starry_sky": self.starry_sky,
            "primordial_identity_cursor": (
                self.primordial_identity_cursor.to_dict()
            ),
            "idea_universe_state": (
                self.idea_universe_state.to_dict()
            ),
        }

    def write_to_world(self):
        self.universe.world["idea_universe"] = (
            self.public_state
        )
        self.universe.world["idea_universe_state"] = (
            self.idea_universe_state
        )

    def tick(self):
        self.tick_count += 1

        if self.primordial_nebula is not None:
            self.primordial_nebula.tick()

        return self.tick_count

    def create_primordial_star(self):
        if not self.stellar_epoch_started:
            raise RuntimeError(
                "Primordial idea star requires stellar epoch."
            )

        cursor = (
            self.primordial_identity_cursor.with_next_star()
        )

        star = PrimordialIdeaStar(
            object_id=cursor.star_id
        )

        history = (
            self.primordial_creation_history.with_event(
                PrimordialStarCreated(
                    object_id=star.id
                )
            )
        )

        self.starry_sky.append(star)
        self._primordial_identity_cursor = cursor
        self._primordial_creation_history = history
        self.write_to_world()

        return star

    def run_primordial_stellar_epoch(self, star_count=1):
        if not self.stellar_epoch_started:
            raise RuntimeError(
                "Primordial stellar epoch has not started."
            )

        stars = []
        remnants = []

        for _ in range(star_count):
            star = self.create_primordial_star()

            star.ignite()

            self._primordial_creation_history = (
                self.primordial_creation_history.with_event(
                    PrimordialStarTransition(
                        object_id=star.id,
                        state=star.state,
                    )
                )
            )

            remnant = star.explode()

            self._primordial_creation_history = (
                self.primordial_creation_history.with_event(
                    PrimordialStarTransition(
                        object_id=star.id,
                        state=star.state,
                    )
                )
            )

            stars.append(star)
            remnants.append(remnant)

        cursor = (
            self.primordial_identity_cursor.with_next_nebula()
        )

        nebula = PrimordialNebula(
            source_remnants=remnants,
            object_id=cursor.nebula_id,
        )

        history = (
            self.primordial_creation_history.with_event(
                PrimordialNebulaCreated(
                    object_id=nebula.id,
                    remnants=tuple(
                        PrimordialRemnantCreation.from_remnant(
                            remnant
                        )
                        for remnant in remnants
                    ),
                )
            )
        )

        self._primordial_identity_cursor = cursor
        self._primordial_creation_history = history
        self.primordial_nebula = nebula
        self.write_to_world()

        return PrimordialStellarEpochResult(
            primordial_nebula=(
                self.primordial_nebula
            ),
            stars=stars,
            remnants=remnants,
        )

    def replay_primordial_creation_history(self, history):
        if not isinstance(
            history,
            PrimordialCreationHistory,
        ):
            raise TypeError(
                "Replay requires PrimordialCreationHistory."
            )

        current_cursor = self.primordial_identity_cursor

        if history.scope != current_cursor.scope:
            raise ValueError(
                "Creation history scope does not match."
            )

        if (
            self.starry_sky
            or self.primordial_nebula is not None
            or current_cursor.star_serial != 0
            or current_cursor.nebula_serial != 0
            or self.primordial_creation_history.events
        ):
            raise RuntimeError(
                "Creation history replay requires "
                "a fresh IdeaUniverse."
            )

        # Rebuild everything before mutating target layer.
        cursor = PrimordialIdentityCursor(
            scope=history.scope
        )

        stars = []
        by_id = {}
        nebula = None

        for event in history.events:
            if type(event) is PrimordialStarCreated:
                next_cursor = cursor.with_next_star()

                if event.object_id != next_cursor.star_id:
                    raise ValueError(
                        "Star creation history contains "
                        "an unexpected canonical ID."
                    )

                star = PrimordialIdeaStar(
                    object_id=event.object_id
                )

                stars.append(star)
                by_id[star.id] = star
                cursor = next_cursor

            elif type(event) is PrimordialStarTransition:
                star = by_id.get(event.object_id)

                if star is None:
                    raise ValueError(
                        "Star transition references "
                        "an unknown star."
                    )

                valid_transition = (
                    (
                        star.state
                        is PrimordialIdeaStarState.CREATED
                        and event.state
                        is PrimordialIdeaStarState.BURNING
                    )
                    or (
                        star.state
                        is PrimordialIdeaStarState.BURNING
                        and event.state
                        is PrimordialIdeaStarState.EXPLODED
                    )
                )

                if not valid_transition:
                    raise ValueError(
                        "Invalid primordial star transition."
                    )

                star.state = event.state

            elif type(event) is PrimordialNebulaCreated:
                next_cursor = cursor.with_next_nebula()

                if event.object_id != next_cursor.nebula_id:
                    raise ValueError(
                        "Nebula creation history contains "
                        "an unexpected canonical ID."
                    )

                nebula = PrimordialNebula(
                    object_id=event.object_id,
                    source_remnants=[
                        remnant.to_remnant()
                        for remnant in event.remnants
                    ],
                )

                cursor = next_cursor

            else:
                raise TypeError(
                    "Unsupported primordial history event."
                )

        # Commit reconstructed state only after validation.
        self.starry_sky[:] = stars
        self.primordial_nebula = nebula
        self._primordial_identity_cursor = cursor
        self._primordial_creation_history = history

        self.write_to_world()

        return tuple(stars), nebula

    def add_entity(self, entity):
        entity.origin_layer = "idea_universe"
        entity.current_layer = "idea_universe"
        self.entities.append(entity)

        meeting_place = getattr(
            self.universe,
            "meeting_place",
            None,
        )

        if meeting_place is not None:
            meeting_place.entities.append(entity)

        print(
            "IDEA UNIVERSE ENTITY BORN: "
            f"{getattr(entity, 'name', None)}"
        )
