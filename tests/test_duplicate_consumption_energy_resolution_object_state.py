import unittest

from cats.duplicate_consumption_energy_resolution import (
    DuplicateConsumptionEnergyResolution,
)


class DuplicateConsumptionEnergyResolutionObjectStateTests(
    unittest.TestCase
):

    def test_resolution_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                resolution.value
                for resolution
                in DuplicateConsumptionEnergyResolution
            },
            {
                "cronenberg_manifested",
                "cronenberg_quantum_counterpart_created",
            },
        )


if __name__ == "__main__":
    unittest.main()
