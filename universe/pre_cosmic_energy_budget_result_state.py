from dataclasses import dataclass


@dataclass(
    slots=True,
    frozen=True,
)
class PreCosmicEnergyBudgetResult:

    idea_dimensions: int
    threshold_j: float
    bar_energy_capture_ratio: float
    energy_serving_j: float
    reality_payment_ratio: float
    will_gain_per_energy_serving: float

    entropy_unit: float
    quantum_entropy_tick_max_units: float
    quantum_entropy_tick_expected_units: float
    expected_quantum_ticks_per_entropy_serving: float
    entropy_unit_energy_value_j: float

    entropy_drink_units: float
    entropy_drink_total_energy_gain_j: float
    entropy_drink_bar_share_ratio: float
    entropy_drink_entity_share_ratio: float
    entropy_drink_bar_energy_gain_j: float
    entropy_drink_entity_energy_gain_j: float
    entropy_drink_payment_ratio: float
    entropy_drink_entropy_increase_ratio: float

    reservoir_before_serving_j: float
    reservoir_before_serving_ratio: float
    first_energy_servings_total_j: float
    reservoir_after_first_energy_servings_j: float
    reservoir_after_first_energy_servings_ratio: float

    god_entropy_gain_ratio: float
    normal_entropy_gain_ratio: float

    def to_dict(self):
        return {
            "idea_dimensions": self.idea_dimensions,
            "threshold_j": self.threshold_j,
            "bar_energy_capture_ratio": (
                self.bar_energy_capture_ratio
            ),
            "energy_serving_j": self.energy_serving_j,
            "reality_payment_ratio": (
                self.reality_payment_ratio
            ),
            "will_gain_per_energy_serving": (
                self.will_gain_per_energy_serving
            ),
            "entropy_unit": self.entropy_unit,
            "quantum_entropy_tick_max_units": (
                self.quantum_entropy_tick_max_units
            ),
            "quantum_entropy_tick_expected_units": (
                self.quantum_entropy_tick_expected_units
            ),
            "expected_quantum_ticks_per_entropy_serving": (
                self.expected_quantum_ticks_per_entropy_serving
            ),
            "entropy_unit_energy_value_j": (
                self.entropy_unit_energy_value_j
            ),
            "entropy_drink_units": (
                self.entropy_drink_units
            ),
            "entropy_drink_total_energy_gain_j": (
                self.entropy_drink_total_energy_gain_j
            ),
            "entropy_drink_bar_share_ratio": (
                self.entropy_drink_bar_share_ratio
            ),
            "entropy_drink_entity_share_ratio": (
                self.entropy_drink_entity_share_ratio
            ),
            "entropy_drink_bar_energy_gain_j": (
                self.entropy_drink_bar_energy_gain_j
            ),
            "entropy_drink_entity_energy_gain_j": (
                self.entropy_drink_entity_energy_gain_j
            ),
            "entropy_drink_payment_ratio": (
                self.entropy_drink_payment_ratio
            ),
            "entropy_drink_entropy_increase_ratio": (
                self.entropy_drink_entropy_increase_ratio
            ),
            "reservoir_before_serving_j": (
                self.reservoir_before_serving_j
            ),
            "reservoir_before_serving_ratio": (
                self.reservoir_before_serving_ratio
            ),
            "first_energy_servings_total_j": (
                self.first_energy_servings_total_j
            ),
            "reservoir_after_first_energy_servings_j": (
                self.reservoir_after_first_energy_servings_j
            ),
            "reservoir_after_first_energy_servings_ratio": (
                self.reservoir_after_first_energy_servings_ratio
            ),
            "god_entropy_gain_ratio": (
                self.god_entropy_gain_ratio
            ),
            "normal_entropy_gain_ratio": (
                self.normal_entropy_gain_ratio
            ),
        }
