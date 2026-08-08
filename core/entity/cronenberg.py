import uuid

from core.entity.entity import Entity
from core.entity.cronenberg_system.metabolism import (
    CronenbergMetabolism
)
from core.entity.cronenberg_system.hunger import (
    CronenbergHunger
)
from core.entity.cronenberg_system.travel import (
    CronenbergTravel
)
from core.entity.cronenberg_system.growth import (
    CronenbergGrowth
)
from core.entity.cronenberg_system.traits import CronenbergTraits
from core.entity.cronenberg_system.quantum_links import CronenbergQuantumLinks
from universe.aroma_profile import AromaProfile


class Cronenberg(Entity):

    def __init__(
        self,
        error,
        source_component,
        source_operation,
        quantum_tick=None
    ):
        super().__init__("cronenberg")

        self.id = (
            f"cronenberg_"
            f"{uuid.uuid4().hex[:8]}"
        )

        self.name = self.id
        self.type = "cronenberg"

        self.state = "born_from_quantum_error"
        self.location = "quantum_layer"

        self.size = 1.0
        self.juice_value = self.size

        self.aroma = AromaProfile.create(
            identity="cronenberg",
            components={
                "ozone": 1.0,
                "ionized_air": 0.85,
                "electrical": 0.75,
                "metallic": 0.20
            },
            intensity=1.0
        )

        self.aroma_chemical_marker = {
            "molecule": "ozone",
            "formula": "O3"
        }

        self.metabolism = (
            CronenbergMetabolism()
        )

        self.hunger = (
            CronenbergHunger()
        )

        self.travel = (
            CronenbergTravel()
        )

        self.growth = (
            CronenbergGrowth()
        )

        self.consumed_cronenbergs = []

        self.traits = CronenbergTraits(
            error=error,
            source_component=source_component,
            source_operation=source_operation,
            quantum_tick=quantum_tick
        )

        self.quantum_link_system = CronenbergQuantumLinks(
            owner_id=self.id
        )

        self.quantum_state = {
            "spin": 0.5,
            "entangled": False,
            "pair_id": None,
            "counterpart_id": None,
            "counterpart_potential": True,
            "counterpart_manifested": False
        }

        self.profile = None
        self.bar_policy = None

        self.origin = {
            "layer": "quantum_layer",
            "source_component": source_component,
            "source_operation": source_operation,
            "quantum_tick": quantum_tick,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }

    @property
    def quantum_links(self):
        return (
            self.quantum_link_system
            .snapshot()
        )

    @property
    def required_daily_energy(self):
        return (
            self.metabolism
            .required_daily_energy(
                self.size
            )
        )

    @property
    def daily_energy_received(self):
        return (
            self.metabolism
            .daily_energy_received
        )

    @property
    def pending_dark_energy(self):
        return (
            self.metabolism
            .pending_dark_energy
        )

    @property
    def total_dark_energy_produced(self):
        return (
            self.metabolism
            .total_dark_energy_produced
        )

    @property
    def is_satiated(self):
        return self.hunger.is_satiated

    @property
    def is_fed_enough(self):
        return (
            self.metabolism
            .is_fed_enough(
                self.size
            )
        )

    @property
    def can_hunt(self):
        return self.hunger.can_hunt

    @property
    def strength(self):
        return (
            self.size,
            self.energy
        )

    def tick(self, universe):
        super().tick(universe)

        if self.location not in {
            "quantum_layer",
            "between_layers"
        }:
            return

        travel_event = (
            self.travel.travel_step(
                size=self.size,
                available_energy=max(
                    0.0,
                    self.energy
                )
            )
        )

        self.energy -= (
            travel_event["energy_spent"]
        )

        travel_dark_energy = (
            travel_event[
                "dark_energy_produced"
            ]
        )

        self.metabolism.pending_dark_energy += (
            travel_dark_energy
        )

        self.metabolism.total_dark_energy_produced += (
            travel_dark_energy
        )

        layer_event = (
            self.growth.grow_from_layer(
                self.size
            )
        )

        self.size = (
            layer_event["new_size"]
        )

        self.juice_value = self.size
        self.travel.layers_crossed += 1

        print(
            f"{self.name} travels -> "
            f"energy spent "
            f"{travel_event['energy_spent']:.2f}, "
            f"dark energy "
            f"{travel_dark_energy:.3f}, "
            f"size {self.size:.2f}"
        )

        if self.location == "quantum_layer":
            self.location = "between_layers"
            self.state = (
                "moving_toward_meeting_place"
            )

            print(
                f"{self.name} -> "
                f"location {self.location}, "
                f"state {self.state}"
            )

            return

        self.location = (
            "meeting_place_entrance"
        )

        self.state = (
            "waiting_at_bar_entrance"
        )

        print(
            f"{self.name} -> "
            f"location {self.location}, "
            f"state {self.state}"
        )

        meeting_place = getattr(
            universe,
            "meeting_place",
            None
        )

        if meeting_place is not None:
            meeting_place.add_entity(
                self
            )

    def receive_energy(self, amount):
        event = (
            self.metabolism.receive_energy(
                amount=amount,
                size=self.size
            )
        )

        self.energy += (
            event["energy_received"]
        )

        print(
            f"{self.name} receives "
            f"{event['energy_received']:.2f} "
            f"energy; needs "
            f"{event['required_energy']:.2f}; "
            f"produces "
            f"{event['dark_energy_produced']:.3f} "
            f"dark energy"
        )

        return event[
            "dark_energy_produced"
        ]

    def collect_dark_energy(self):
        return (
            self.metabolism
            .collect_dark_energy()
        )

    def _is_quantum_counterpart_of(self, other):
        if getattr(other, "type", None) != "cronenberg":
            return False

        own_state = getattr(
            self,
            "quantum_state",
            {}
        )

        other_state = getattr(
            other,
            "quantum_state",
            {}
        )

        pair_id = own_state.get(
            "pair_id"
        )

        return (
            pair_id is not None
            and pair_id == other_state.get("pair_id")
            and own_state.get("counterpart_id")
            == other.id
            and other_state.get("counterpart_id")
            == self.id
        )

    def consume(self, other):
        if other is self:
            raise ValueError(
                "Cronenberg cannot consume itself."
            )

        if self._is_quantum_counterpart_of(other):
            universe = getattr(
                self,
                "universe",
                None
            )

            if universe is None:
                raise RuntimeError(
                    "Quantum pair consumption requires "
                    "a registered Universe."
                )

            return universe.resolve_quantum_pair_consumption(
                first=self,
                second=other
            )

        consumed_mass = float(
            other.size
        )

        consumed_energy = max(
            0.0,
            float(other.energy)
        )

        growth_event = (
            self.growth.absorb_mass(
                size=self.size,
                consumed_mass=consumed_mass
            )
        )

        self.size = (
            growth_event["new_size"]
        )

        self.energy += consumed_energy
        self.juice_value = self.size

        digestion_event = (
            self.hunger.start_digestion(
                consumed_mass=consumed_mass
            )
        )

        self.consumed_cronenbergs.append({
            "name": other.name,
            "mass": consumed_mass,
            "energy": consumed_energy,
            "digestion_days": (
                digestion_event[
                    "digestion_days"
                ]
            )
        })

        other.state = (
            "consumed_by_cronenberg"
        )

        other.location = (
            "inside_cronenberg"
        )

        other.energy = 0.0

        print(
            f"{self.name} consumes "
            f"{other.name}; "
            f"gains mass "
            f"{consumed_mass:.2f}; "
            f"new size "
            f"{self.size:.2f}; "
            f"digestion "
            f"{digestion_event['digestion_days']} "
            f"days"
        )

        return {
            "predator": self.name,
            "prey": other.name,
            "mass_gained": consumed_mass,
            "energy_gained": consumed_energy,
            "new_size": self.size,
            "digestion_days": (
                digestion_event[
                    "digestion_days"
                ]
            )
        }

    def tick_in_pen(self, universe):
        self.age += 1

        fed_enough = (
            self.metabolism
            .is_fed_enough(
                self.size
            )
        )

        was_satiated = (
            self.hunger.is_satiated
        )

        hunger_event = (
            self.hunger.finish_day(
                fed_enough=fed_enough
            )
        )

        growth_allowed = (
            fed_enough
            or was_satiated
        )

        if growth_allowed:
            growth_event = (
                self.growth
                .grow_from_feeding(
                    self.size
                )
            )

            self.size = (
                growth_event["new_size"]
            )

            self.juice_value = self.size

            if was_satiated:
                self.state = (
                    "growing_while_digesting"
                )
            else:
                self.state = (
                    "growing_in_pen"
                )

            print(
                f"{self.name} grows in pen -> "
                f"age {self.age}, "
                f"size {self.size:.2f}, "
                f"required food "
                f"{self.required_daily_energy:.2f}, "
                f"digestion remaining "
                f"{self.hunger.satiety_days_remaining}"
            )

        else:
            starvation_event = (
                self.growth.apply_starvation(
                    size=self.size,
                    hungry_days=(
                        self.hunger.hungry_days
                    )
                )
            )

            self.size = (
                starvation_event[
                    "new_size"
                ]
            )

            self.juice_value = self.size
            self.state = "hungry_in_pen"

            print(
                f"{self.name} is hungry -> "
                f"received "
                f"{self.daily_energy_received:.2f}, "
                f"required "
                f"{self.required_daily_energy:.2f}, "
                f"hungry days "
                f"{self.hunger.hungry_days}, "
                f"size {self.size:.2f}"
            )

        self.metabolism.finish_day()

        return growth_allowed

    def cat_response(self):
        return (
            self.travel.cat_response(
                self.size
            )
        )

    @property
    def is_alive(self):
        return self.state not in {
            "destroyed",
            "consumed_by_cronenberg",
            "processed_into_lemonade"
        }

    @property
    def public_state(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "active": self.active,
            "location": self.location,
            "origin": dict(self.origin),
            "quantum_state": dict(self.quantum_state),
            "alive": self.is_alive,
            "age": self.age,
            "energy": self.energy,
            "size": self.size,
            "juice_value": self.juice_value,
            "required_daily_energy": (
                self.required_daily_energy
            ),
            "daily_energy_received": (
                self.daily_energy_received
            ),
            "cat_response": (
                self.cat_response()
            ),
            "metabolism": (
                self.metabolism.public_state
            ),
            "hunger": (
                self.hunger.public_state
            ),
            "travel": (
                self.travel.public_state
            ),
            "growth": (
                self.growth.public_state
            ),
            "traits": self.traits.public_state,
            "quantum_links": self.quantum_links,
            "consumed_cronenbergs": list(
                self.consumed_cronenbergs
            )
        }
