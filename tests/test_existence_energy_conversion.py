import unittest

from universe.energy_gate import (
    PLANCK_ENERGY_THRESHOLD_J
)

from core.entity.existence_energy import (
    existence_pct_to_energy_j
)


class ExistenceEnergyConversionTests(
    unittest.TestCase
):

    def test_full_existence_equals_planck_energy(
        self
    ):
        self.assertEqual(
            existence_pct_to_energy_j(
                100.0
            ),
            PLANCK_ENERGY_THRESHOLD_J
        )

    def test_half_existence_equals_half_planck_energy(
        self
    ):
        self.assertEqual(
            existence_pct_to_energy_j(
                50.0
            ),
            PLANCK_ENERGY_THRESHOLD_J
            * 0.5
        )

    def test_zero_existence_produces_no_energy(
        self
    ):
        self.assertEqual(
            existence_pct_to_energy_j(
                0.0
            ),
            0.0
        )


if __name__ == "__main__":
    unittest.main()
