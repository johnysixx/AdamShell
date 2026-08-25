from .primordial_waters import PrimordialWaters
from .primordial_idea_star import PrimordialIdeaStar
from .primordial_nebula import PrimordialNebula

class IdeaUniverse:

    def __init__(self, universe):
        self.universe = universe
        self.entities = []
        self.events = []
        self.tick_count = 0
        self.stellar_epoch_started = False
        self.heavenly_lights_created = False
        self.heaven_ordered = False
        self.celestial_stations_established = False
        self.divine_order_established = False
        self.aquatic_life_archetype = False
        self.flying_life_archetype = False
        self.land_life_archetype = False

        registry = getattr(
            self.universe,
            "universe_registry",
            None
        )

        if registry is None:
            raise RuntimeError(
                "Idea Universe requires UniverseRegistry"
            )

        self.universe_id = registry.register_universe(
            name="idea_universe",
            universe_type="pre_physical_idea_reality"
        )

        self.primordial_waters = (
            PrimordialWaters()
        )

        self.primordial_nebula = None

        self.starry_sky = []

        self.state = {
            "name": "idea_universe",
            "type": "pre_physical_idea_reality",
            "state": "created",
            "part_of_physics": False,
            "primordial_waters": (
                self.primordial_waters
            ),
            "primordial_nebula": None,
            "entities": self.entities,
            "events": self.events
        }

        self.universe.world["idea_universe"] = self.state

        print("IDEA UNIVERSE INITIALIZED")

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

        self.starry_sky.append(
            star
        )

        return star

    def run_primordial_stellar_epoch(
        self,
        star_count=1
    ):
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

            stars.append(
                star
            )

            remnants.append(
                remnant
            )

        self.primordial_nebula = (
            PrimordialNebula(
                source_remnants=remnants
            )
        )

        self.state[
            "primordial_nebula"
        ] = self.primordial_nebula

        return {
            "primordial_nebula": self.primordial_nebula,
            "stars": stars,
            "remnants": remnants
        }

    def add_entity(self, entity):
        entity["origin_layer"] = "idea_universe"
        entity["current_layer"] = "idea_universe"

        self.entities.append(entity)

        meeting_place = getattr(
            self.universe,
            "meeting_place",
            None
        )

        if meeting_place is not None:
            meeting_place.entities.append(
                entity
            )

        print(
            f"IDEA UNIVERSE ENTITY BORN: "
            f"{entity.get('name')}"
        )











