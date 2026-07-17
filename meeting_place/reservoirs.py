import random

from universe.pre_cosmic_rules import (
    QUANTUM_ENTROPY_TICK_MAX_UNITS,
    SERPENT_ENTROPY_DRINK_BAR_ENERGY_GAIN_J,
    SERPENT_ENTROPY_DRINK_SERPENT_ENERGY_GAIN_J,
    SERPENT_ENTROPY_DRINK_UNITS,
)


class BarEnergyReservoir:

    def __init__(self):
        self.name = "bar_energy_reservoir"
        self.type = "pre_physical_energy_reservoir"
        self.energy_j = 0.0
        self.events = []

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "energy_j": self.energy_j,
            "events": self.events
        }

    def add_energy(self, source, amount_j):
        if amount_j <= 0:
            raise ValueError("Energy amount must be positive")

        self.energy_j += amount_j

        event = {
            "name": "bar_energy_added",
            "source": source,
            "amount_j": amount_j,
            "total_energy_j": self.energy_j
        }

        self.events.append(event)

        print(f"BAR ENERGY ADDED: {amount_j:.3f} J from {source}")
        print(f"BAR ENERGY TOTAL: {self.energy_j:.3f} J")

        return event

    def spend_energy(self, purpose, amount_j):
        if amount_j <= 0:
            raise ValueError("Energy amount must be positive")

        if amount_j > self.energy_j:
            raise ValueError("Not enough bar energy")

        self.energy_j -= amount_j

        event = {
            "name": "bar_energy_spent",
            "purpose": purpose,
            "amount_j": amount_j,
            "total_energy_j": self.energy_j
        }

        self.events.append(event)

        print(f"BAR ENERGY SPENT: {amount_j:.3f} J for {purpose}")
        print(f"BAR ENERGY TOTAL: {self.energy_j:.3f} J")

        return event


class BarEntropyReservoir:

    def __init__(self):
        self.name = "bar_entropy_reservoir"
        self.type = "pre_physical_entropy_reservoir"
        self.entropy_units = 0.0
        self.events = []

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "entropy_units": self.entropy_units,
            "events": self.events
        }

    def quantum_tick(self, rng=None):
        rng = rng or random
        amount_units = rng.uniform(0.0, QUANTUM_ENTROPY_TICK_MAX_UNITS)

        self.entropy_units += amount_units

        event = {
            "name": "quantum_entropy_tick",
            "amount_units": amount_units,
            "total_entropy_units": self.entropy_units
        }

        self.events.append(event)

        print(f"BAR ENTROPY TICK: +{amount_units:.6f} units")
        print(f"BAR ENTROPY TOTAL: {self.entropy_units:.6f} units")

        return event

    def add_entropy(self, source, amount_units):
        if amount_units <= 0:
            raise ValueError("Entropy amount must be positive")

        self.entropy_units += amount_units

        event = {
            "name": "bar_entropy_added",
            "source": source,
            "amount_units": amount_units,
            "total_entropy_units": self.entropy_units
        }

        self.events.append(event)

        print(f"BAR ENTROPY ADDED: {amount_units:.6f} units from {source}")
        print(f"BAR ENTROPY TOTAL: {self.entropy_units:.6f} units")

        return event

    def serve_entropy_to_serpent(self, energy_reservoir, serpent=None):
        if self.entropy_units < SERPENT_ENTROPY_DRINK_UNITS:
            print("NOT ENOUGH BAR ENTROPY FOR SERPENT")
            return None

        self.entropy_units -= SERPENT_ENTROPY_DRINK_UNITS

        bar_energy_gain_j = SERPENT_ENTROPY_DRINK_BAR_ENERGY_GAIN_J
        serpent_energy_gain_j = SERPENT_ENTROPY_DRINK_SERPENT_ENERGY_GAIN_J

        energy_reservoir.add_energy("serpent_entropy_drink", bar_energy_gain_j)

        if serpent is not None:
            if isinstance(serpent, dict):
                serpent["energy_j"] = serpent.get("energy_j", 0.0) + serpent_energy_gain_j
            else:
                serpent.energy_j = getattr(serpent, "energy_j", 0.0) + serpent_energy_gain_j

        event = {
            "name": "serpent_entropy_served",
            "entropy_units_spent": SERPENT_ENTROPY_DRINK_UNITS,
            "bar_energy_gain_j": bar_energy_gain_j,
            "serpent_energy_gain_j": serpent_energy_gain_j,
            "total_entropy_units": self.entropy_units
        }

        self.events.append(event)

        print("SERPENT WAS SERVED ENTROPY")
        print(f"SERPENT ENERGY GAIN: {serpent_energy_gain_j:.3f} J")
        print(f"BAR ENTROPY TOTAL: {self.entropy_units:.6f} units")

        return event
