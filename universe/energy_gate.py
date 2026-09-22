from universe.energy_gate_state import (
    EnergyGateCollectionEvent,
    EnergyGateState,
)


HBAR_J_S = 1.054_571_817e-34
SPEED_OF_LIGHT_M_S = 299_792_458
GRAVITATIONAL_CONSTANT = 6.67430e-11

PLANCK_ENERGY_THRESHOLD_J = (
    HBAR_J_S * SPEED_OF_LIGHT_M_S ** 5 / GRAVITATIONAL_CONSTANT
) ** 0.5


class EnergyGate:

    def __init__(self, universe, threshold_j=None):
        self.universe = universe
        self.name = "energy_gate"
        self.type = "pre_physical_threshold"
        self.state = "closed"

        self.threshold_j = threshold_j or PLANCK_ENERGY_THRESHOLD_J
        self.idea_energy_j = 0.0

        self.events = []

        self.gate_state = EnergyGateState(
            threshold_j=self.threshold_j,
        )

        self.public_state = self._build_public_state()

        self.write_to_world()

    def _build_public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "gate_state": self.gate_state.to_dict(),
            "events": [
                event.to_dict()
                for event in self.events
            ],
        }

    def _refresh_public_state(self):
        self.public_state = self._build_public_state()

    def collect_energy(self, source, amount_j):
        if amount_j <= 0:
            raise ValueError("Energy amount must be positive")

        return (
            self.universe
            .quantum_error_boundary.execute(
                operation=lambda: (
                    self._collect_energy_unprotected(
                        source=source,
                        amount_j=amount_j,
                    )
                ),
                source_component="energy_gate",
                source_operation="collect_energy",
            )
        )

    def _collect_energy_unprotected(
        self,
        source,
        amount_j,
    ):
        self.idea_energy_j += amount_j

        self.events.append(
            EnergyGateCollectionEvent(
                source=source,
                amount_j=amount_j,
                total_idea_energy_j=self.idea_energy_j,
            )
        )

        self._update_state_unprotected()

        print(
            f"IDEA ENERGY COLLECTED: {amount_j:.3f} J "
            f"from {source}"
        )
        print(
            f"IDEA ENERGY TOTAL: "
            f"{self.idea_energy_j:.3f} J"
        )
        print(
            f"BIG BANG THRESHOLD: "
            f"{self.threshold_j:.3f} J"
        )

        return self.public_state

    def update_state(self):
        return (
            self.universe
            .quantum_error_boundary.execute(
                operation=self._update_state_unprotected,
                source_component="energy_gate",
                source_operation="update_state",
            )
        )

    def _update_state_unprotected(self):
        energy_ratio = self.idea_energy_j / self.threshold_j

        self.gate_state.idea_energy_j = self.idea_energy_j
        self.gate_state.energy_ratio = energy_ratio

        if self.idea_energy_j >= self.threshold_j:
            self.state = "open"
            self.gate_state.threshold_reached = True
            self.gate_state.physical_seed_created = True
            self.gate_state.big_bang_allowed = True
        else:
            self.state = "closed"
            self.gate_state.threshold_reached = False
            self.gate_state.physical_seed_created = False
            self.gate_state.big_bang_allowed = False

        self.write_to_world()

    def try_start_big_bang(self):
        return (
            self.universe
            .quantum_error_boundary.execute(
                operation=(
                    self._try_start_big_bang_unprotected
                ),
                source_component="energy_gate",
                source_operation="try_start_big_bang",
            )
        )

    def _try_start_big_bang_unprotected(self):
        self._update_state_unprotected()

        if not self.gate_state.big_bang_allowed:
            print("ENERGY GATE CLOSED")
            print("BIG BANG NOT ALLOWED YET")
            return False

        if self.universe.big_bang_started:
            print("BIG BANG ALREADY STARTED")
            self.gate_state.big_bang_started = True
            self.write_to_world()
            return True

        print("ENERGY GATE OPEN")
        print("PHYSICAL SEED CREATED")
        print("BIG BANG ALLOWED")

        self.universe.start_big_bang()

        self.gate_state.big_bang_started = True
        self.write_to_world()

        return True

    def write_to_world(self):
        self._refresh_public_state()

        self.universe.world["energy_gate"] = (
            self.public_state
        )
        self.universe.world["energy_gate_state"] = (
            self.gate_state
        )
