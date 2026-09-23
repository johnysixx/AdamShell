from universe.energy_gate import (
    PLANCK_ENERGY_THRESHOLD_J,
    SPEED_OF_LIGHT_M_S,
)
from universe.pre_cosmic_rules import IDEA_DIMENSIONS
from universe.dark_sector_state import (
    DarkMatterCondensationEvent,
    DarkSectorEnergyReceivedEvent,
    DarkSectorState,
)


QUANTUM_BOX_ENERGY_COST_J = (
    PLANCK_ENERGY_THRESHOLD_J / IDEA_DIMENSIONS
)

DARK_ENERGY_QUANTUM_THRESHOLD_J = (
    PLANCK_ENERGY_THRESHOLD_J
)


class DarkSector:

    def __init__(self, universe=None):
        self.universe = universe
        self.name = "dark_sector"
        self.type = "cosmic_dark_sector"

        self.dark_sector_state = DarkSectorState(
            quantum_threshold_j=(
                DARK_ENERGY_QUANTUM_THRESHOLD_J
            ),
        )

        self.events = []

    @property
    def dark_energy_j(self):
        return self.dark_sector_state.dark_energy_j

    @dark_energy_j.setter
    def dark_energy_j(self, value):
        self.dark_sector_state.dark_energy_j = value

    @property
    def dark_matter_kg(self):
        return self.dark_sector_state.dark_matter_kg

    @dark_matter_kg.setter
    def dark_matter_kg(self, value):
        self.dark_sector_state.dark_matter_kg = value

    @property
    def quantum_threshold_j(self):
        return self.dark_sector_state.quantum_threshold_j

    @quantum_threshold_j.setter
    def quantum_threshold_j(self, value):
        self.dark_sector_state.quantum_threshold_j = value

    def receive_empty_box_energy(
            self,
            box_id,
            energy_j=QUANTUM_BOX_ENERGY_COST_J
    ):
        if energy_j <= 0:
            raise ValueError(
                "Received energy must be positive"
            )

        if self.universe is None:
            return self._receive_empty_box_energy_unprotected(
                box_id=box_id,
                energy_j=energy_j,
            )

        return (
            self.universe
            .quantum_error_boundary.execute(
                operation=lambda: (
                    self._receive_empty_box_energy_unprotected(
                        box_id=box_id,
                        energy_j=energy_j,
                    )
                ),
                source_component="dark_sector",
                source_operation=(
                    "receive_empty_box_energy"
                ),
            )
        )

    def _receive_empty_box_energy_unprotected(
        self,
        box_id,
        energy_j,
    ):
        self.dark_energy_j += energy_j

        event = DarkSectorEnergyReceivedEvent(
            box_id=box_id,
            energy_j=energy_j,
            dark_energy_total_j=self.dark_energy_j,
            threshold_progress=self.threshold_progress,
        )

        self.events.append(event)

        print(
            f"DARK ENERGY RECEIVED FROM EMPTY BOX: "
            f"{box_id} "
            f"ENERGY={energy_j:.3f} J "
            f"TOTAL={self.dark_energy_j:.3f} J"
        )

        return event

    def _condense_dark_matter(self):
        if not self.threshold_reached:
            return None

        consumed_energy_j = (
            self.quantum_threshold_j
        )

        produced_dark_matter_kg = (
            self.energy_mass_equivalent_kg(
                consumed_energy_j
            )
        )

        self.dark_energy_j -= consumed_energy_j
        self.dark_matter_kg += produced_dark_matter_kg

        event = DarkMatterCondensationEvent(
            consumed_energy_j=consumed_energy_j,
            produced_dark_matter_kg=(
                produced_dark_matter_kg
            ),
            dark_energy_remaining_j=(
                self.dark_energy_j
            ),
            dark_matter_total_kg=(
                self.dark_matter_kg
            ),
        )

        self.events.append(event)

        return event

    @staticmethod
    def energy_mass_equivalent_kg(energy_j):
        if energy_j < 0:
            raise ValueError(
                "Energy cannot be negative"
            )

        return energy_j / SPEED_OF_LIGHT_M_S ** 2

    @property
    def threshold_progress(self):
        if self.quantum_threshold_j <= 0:
            return 0.0

        return min(
            self.dark_energy_j / self.quantum_threshold_j,
            1.0
        )

    @property
    def energy_remaining_to_threshold_j(self):
        return max(
            self.quantum_threshold_j - self.dark_energy_j,
            0.0
        )

    @property
    def empty_boxes_remaining_estimate(self):
        remaining_energy = (
            self.energy_remaining_to_threshold_j
        )

        if remaining_energy <= 0:
            return 0.0

        return (
            remaining_energy
            / QUANTUM_BOX_ENERGY_COST_J
        )

    @property
    def threshold_reached(self):
        return (
            self.dark_energy_j
            >= self.quantum_threshold_j
        )

    @property
    def state(self):
        if self.threshold_reached:
            return "threshold_reached"

        return "accumulating"

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "dark_energy_j": self.dark_energy_j,
            "dark_matter_kg": self.dark_matter_kg,
            "dark_sector_state": (
                self.dark_sector_state.to_dict()
            ),
            "quantum_box_energy_cost_j": (
                QUANTUM_BOX_ENERGY_COST_J
            ),
            "quantum_threshold_j": (
                self.quantum_threshold_j
            ),
            "threshold_progress": (
                self.threshold_progress
            ),
            "threshold_reached": (
                self.threshold_reached
            ),
            "energy_remaining_to_threshold_j": (
                self.energy_remaining_to_threshold_j
            ),
            "empty_boxes_remaining_estimate": (
                self.empty_boxes_remaining_estimate
            ),
            "state": self.state,
            "dark_energy_mass_equivalent_kg": (
                self.energy_mass_equivalent_kg(
                    self.dark_energy_j
                )
            ),
            "event_count": len(self.events)
        }
