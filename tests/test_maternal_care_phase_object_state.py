import unittest

from cats.maternal_care_phase import (
    MaternalCarePhase,
)
from cats.cat_maternal_care_system import (
    CatMaternalCareSystem,
)


class MaternalCarePhaseObjectStateTests(
    unittest.TestCase
):

    def test_age_resolves_to_domain_phase(
        self
    ):
        system = CatMaternalCareSystem()

        self.assertIs(
            system.care_phase(5),
            MaternalCarePhase.NEONATAL,
        )
        self.assertIs(
            system.care_phase(20),
            MaternalCarePhase.COMPLETE,
        )
        self.assertIs(
            system.care_phase(40),
            MaternalCarePhase.REDUCED,
        )
        self.assertIs(
            system.care_phase(70),
            MaternalCarePhase.INDEPENDENCE,
        )

    def test_phase_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                phase.value
                for phase
                in MaternalCarePhase
            },
            {
                "neonatal_maternal_care",
                "complete_maternal_care",
                "reduced_maternal_care",
                "maternal_independence",
            },
        )


if __name__ == "__main__":
    unittest.main()
