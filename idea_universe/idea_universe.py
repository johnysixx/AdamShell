from idea_universe.idea_universe_state import IdeaUniverseState
from idea_universe.primordial_idea_star import PrimordialIdeaStar
from idea_universe.primordial_nebula import PrimordialNebula
from idea_universe.primordial_waters import PrimordialWaters


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

        star = PrimordialIdeaStar()
        self.starry_sky.append(star)

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
            remnant = star.explode()
            stars.append(star)
            remnants.append(remnant)

        self.primordial_nebula = PrimordialNebula(
            source_remnants=remnants
        )
        self.write_to_world()

        return {
            "primordial_nebula": self.primordial_nebula,
            "stars": stars,
            "remnants": remnants,
        }

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
