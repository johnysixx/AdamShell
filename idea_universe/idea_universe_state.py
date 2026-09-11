from dataclasses import dataclass


@dataclass(slots=True)
class IdeaUniverseState:

    status: str = "created"
    part_of_physics: bool = False
    tick_count: int = 0
    stellar_epoch_started: bool = False
    heavenly_lights_created: bool = False
    heaven_ordered: bool = False
    celestial_stations_established: bool = False
    divine_order_established: bool = False
    aquatic_life_archetype: bool = False
    flying_life_archetype: bool = False
    land_life_archetype: bool = False

    def to_dict(self):
        return {
            "status": self.status,
            "part_of_physics": self.part_of_physics,
            "tick_count": self.tick_count,
            "stellar_epoch_started": (
                self.stellar_epoch_started
            ),
            "heavenly_lights_created": (
                self.heavenly_lights_created
            ),
            "heaven_ordered": self.heaven_ordered,
            "celestial_stations_established": (
                self.celestial_stations_established
            ),
            "divine_order_established": (
                self.divine_order_established
            ),
            "aquatic_life_archetype": (
                self.aquatic_life_archetype
            ),
            "flying_life_archetype": (
                self.flying_life_archetype
            ),
            "land_life_archetype": (
                self.land_life_archetype
            ),
        }
