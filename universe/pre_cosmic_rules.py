from universe.energy_gate import PLANCK_ENERGY_THRESHOLD_J


IDEA_DIMENSIONS = 20

BAR_ENERGY_CAPTURE_RATIO = 1 / IDEA_DIMENSIONS

ENERGY_SERVING_RATIO = 1 / 1000
ENERGY_SERVING_J = PLANCK_ENERGY_THRESHOLD_J * ENERGY_SERVING_RATIO

REALITY_PAYMENT_RATIO = 0.01
WILL_GAIN_PER_ENERGY_SERVING = 0.2

ENTROPY_UNIT = 1.0
QUANTUM_ENTROPY_TICK_MAX_UNITS = 1 / IDEA_DIMENSIONS
QUANTUM_ENTROPY_TICK_EXPECTED_UNITS = QUANTUM_ENTROPY_TICK_MAX_UNITS / 2
EXPECTED_QUANTUM_TICKS_PER_ENTROPY_SERVING = (
    ENTROPY_UNIT / QUANTUM_ENTROPY_TICK_EXPECTED_UNITS
)

ENTROPY_UNIT_ENERGY_VALUE_J = ENERGY_SERVING_J / IDEA_DIMENSIONS
SERPENT_ENTROPY_DRINK_UNITS = ENTROPY_UNIT
SERPENT_ENTROPY_DRINK_ENERGY_GAIN_J = (
    SERPENT_ENTROPY_DRINK_UNITS * ENTROPY_UNIT_ENERGY_VALUE_J
)
SERPENT_ENTROPY_PAYMENT_RATIO = 0.0
SERPENT_ENTROPY_INCREASE_RATIO = 0.0

IDEA_UNIVERSE_BIRTH_ENERGY_J = PLANCK_ENERGY_THRESHOLD_J * 1.0
PRINCIPLE_BIRTH_ENERGY_J = PLANCK_ENERGY_THRESHOLD_J * 0.5
GOD_EMERGENCE_ENERGY_J = PLANCK_ENERGY_THRESHOLD_J * 0.75

NORMAL_ENTROPY_GAIN_RATIO = 0.01
GOD_ENTROPY_GAIN_RATIO = 0.004


def captured_by_bar(generated_energy_j):
    return generated_energy_j * BAR_ENERGY_CAPTURE_RATIO


def describe_pre_cosmic_energy_budget():
    serpent_entropy_energy_gain = SERPENT_ENTROPY_DRINK_ENERGY_GAIN_J

    idea_universe_capture = captured_by_bar(IDEA_UNIVERSE_BIRTH_ENERGY_J)
    lilith_capture = captured_by_bar(PRINCIPLE_BIRTH_ENERGY_J)
    pazuzu_male_principle_capture = captured_by_bar(PRINCIPLE_BIRTH_ENERGY_J)
    god_capture = captured_by_bar(GOD_EMERGENCE_ENERGY_J)

    reservoir_before_serving = (
        serpent_entropy_energy_gain
        + idea_universe_capture
        + lilith_capture
        + pazuzu_male_principle_capture
        + god_capture
    )

    first_energy_servings_total = ENERGY_SERVING_J * 3
    reservoir_after_first_energy_servings = (
        reservoir_before_serving - first_energy_servings_total
    )

    return {
        "idea_dimensions": IDEA_DIMENSIONS,
        "threshold_j": PLANCK_ENERGY_THRESHOLD_J,
        "bar_energy_capture_ratio": BAR_ENERGY_CAPTURE_RATIO,
        "energy_serving_j": ENERGY_SERVING_J,
        "reality_payment_ratio": REALITY_PAYMENT_RATIO,
        "will_gain_per_energy_serving": WILL_GAIN_PER_ENERGY_SERVING,

        "entropy_unit": ENTROPY_UNIT,
        "quantum_entropy_tick_max_units": QUANTUM_ENTROPY_TICK_MAX_UNITS,
        "quantum_entropy_tick_expected_units": QUANTUM_ENTROPY_TICK_EXPECTED_UNITS,
        "expected_quantum_ticks_per_entropy_serving": EXPECTED_QUANTUM_TICKS_PER_ENTROPY_SERVING,
        "entropy_unit_energy_value_j": ENTROPY_UNIT_ENERGY_VALUE_J,

        "serpent_entropy_drink_units": SERPENT_ENTROPY_DRINK_UNITS,
        "serpent_entropy_drink_energy_gain_j": serpent_entropy_energy_gain,
        "serpent_entropy_payment_ratio": SERPENT_ENTROPY_PAYMENT_RATIO,
        "serpent_entropy_increase_ratio": SERPENT_ENTROPY_INCREASE_RATIO,

        "reservoir_before_serving_j": reservoir_before_serving,
        "reservoir_before_serving_ratio": reservoir_before_serving / PLANCK_ENERGY_THRESHOLD_J,
        "first_energy_servings_total_j": first_energy_servings_total,
        "reservoir_after_first_energy_servings_j": reservoir_after_first_energy_servings,
        "reservoir_after_first_energy_servings_ratio": reservoir_after_first_energy_servings / PLANCK_ENERGY_THRESHOLD_J,

        "god_entropy_gain_ratio": GOD_ENTROPY_GAIN_RATIO,
        "normal_entropy_gain_ratio": NORMAL_ENTROPY_GAIN_RATIO,
    }
