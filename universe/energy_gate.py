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

        self.gate_state = {
            "threshold_j": self.threshold_j,
            "idea_energy_j": self.idea_energy_j,
            "energy_ratio": 0.0,
            "threshold_reached": False,
            "physical_seed_created": False,
            "big_bang_allowed": False,
            "big_bang_started": False
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "gate_state": self.gate_state,
            "events": self.events
        }

        self.write_to_world()

    def collect_energy(self, source, amount_j):
        if amount_j <= 0:
            raise ValueError("Energy amount must be positive")

        self.idea_energy_j += amount_j

        self.events.append({
            "name": "idea_energy_collected",
            "source": source,
            "amount_j": amount_j,
            "total_idea_energy_j": self.idea_energy_j
        })

        self.update_state()

        print(f"IDEA ENERGY COLLECTED: {amount_j:.3f} J from {source}")
        print(f"IDEA ENERGY TOTAL: {self.idea_energy_j:.3f} J")
        print(f"BIG BANG THRESHOLD: {self.threshold_j:.3f} J")

        return self.public_state

    def update_state(self):
        energy_ratio = self.idea_energy_j / self.threshold_j

        self.gate_state["idea_energy_j"] = self.idea_energy_j
        self.gate_state["energy_ratio"] = energy_ratio

        if self.idea_energy_j >= self.threshold_j:
            self.state = "open"
            self.public_state["state"] = self.state
            self.gate_state["threshold_reached"] = True
            self.gate_state["physical_seed_created"] = True
            self.gate_state["big_bang_allowed"] = True
        else:
            self.state = "closed"
            self.public_state["state"] = self.state
            self.gate_state["threshold_reached"] = False
            self.gate_state["physical_seed_created"] = False
            self.gate_state["big_bang_allowed"] = False

        self.write_to_world()

    def try_start_big_bang(self):
        self.update_state()

        if not self.gate_state["big_bang_allowed"]:
            print("ENERGY GATE CLOSED")
            print("BIG BANG NOT ALLOWED YET")
            return False

        if self.universe.big_bang_started:
            print("BIG BANG ALREADY STARTED")
            self.gate_state["big_bang_started"] = True
            self.write_to_world()
            return True

        print("ENERGY GATE OPEN")
        print("PHYSICAL SEED CREATED")
        print("BIG BANG ALLOWED")

        self.universe.start_big_bang()

        self.gate_state["big_bang_started"] = True
        self.write_to_world()

        return True

    def write_to_world(self):
        self.universe.world["energy_gate"] = self.public_state
        self.universe.world["energy_gate_state"] = self.gate_state
