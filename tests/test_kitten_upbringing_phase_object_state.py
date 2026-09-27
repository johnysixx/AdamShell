import unittest

from cats.kitten_upbringing_phase import (
    KittenUpbringingPhase,
)
from cats.kitten_upbringing_state import (
    KittenUpbringingState,
)


class KittenUpbringingPhaseObjectStateTests(
    unittest.TestCase
):

    def test_default_phase_is_domain_object(
        self
    ):
        state = KittenUpbringingState()

        self.assertIs(
            state.phase,
            KittenUpbringingPhase
            .COMPLETE_MATERNAL_CARE,
        )

    def test_phase_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                phase.value
                for phase
                in KittenUpbringingPhase
            },
            {
                "complete_maternal_care",
                "early_socialization",
                "live_prey_training",
                "first_training_kill",
                "family_hunting",
            },
        )


if __name__ == "__main__":
    unittest.main()
