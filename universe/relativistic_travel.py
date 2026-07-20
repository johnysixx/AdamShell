from math import sqrt

from universe.energy_gate import SPEED_OF_LIGHT_M_S


CAT_SPEED_RATIO = 0.99
CAT_MAX_SPEED_M_S = SPEED_OF_LIGHT_M_S * CAT_SPEED_RATIO


def lorentz_factor(speed_m_s):
    if speed_m_s < 0:
        raise ValueError("Speed cannot be negative")

    if speed_m_s >= SPEED_OF_LIGHT_M_S:
        raise ValueError("Massive entities cannot reach or exceed light speed")

    beta = speed_m_s / SPEED_OF_LIGHT_M_S

    return 1.0 / sqrt(1.0 - beta ** 2)


def calculate_relativistic_travel(
    distance_m,
    speed_m_s=CAT_MAX_SPEED_M_S
):
    if distance_m < 0:
        raise ValueError("Distance cannot be negative")

    if speed_m_s <= 0:
        raise ValueError("Speed must be positive")

    gamma = lorentz_factor(speed_m_s)
    coordinate_time_s = distance_m / speed_m_s
    proper_time_s = coordinate_time_s / gamma

    return {
        "distance_m": distance_m,
        "speed_m_s": speed_m_s,
        "speed_ratio_c": speed_m_s / SPEED_OF_LIGHT_M_S,
        "lorentz_factor": gamma,
        "coordinate_time_s": coordinate_time_s,
        "proper_time_s": proper_time_s
    }
