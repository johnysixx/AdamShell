from universe.energy_gate import (
    PLANCK_ENERGY_THRESHOLD_J
)


def existence_pct_to_energy_j(
    existence_pct
):
    existence_pct = float(
        existence_pct
    )

    if existence_pct < 0.0:
        raise ValueError(
            "Existence percentage cannot be negative."
        )

    return (
        PLANCK_ENERGY_THRESHOLD_J
        * (
            existence_pct
            / 100.0
        )
    )
