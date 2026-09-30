import unittest

from meeting_place.bar_blacklist import BarBlacklist
from meeting_place.bouncer import Bouncer
from meeting_place.bouncer_state import (
    BouncerState,
)


class BouncerStateObjectStateTests(
    unittest.TestCase
):

    def _bouncer(self):
        return Bouncer(
            blacklist=BarBlacklist()
        )

    def test_bouncer_starts_outside_as_enum(self):
        bouncer = self._bouncer()

        self.assertIs(
            bouncer.state,
            BouncerState.STANDING_OUTSIDE_BAR,
        )

    def test_string_state_is_rejected(self):
        bouncer = self._bouncer()

        with self.assertRaises(TypeError):
            bouncer.state = "responding_inside_bar"

    def test_state_values_define_domain_names(self):
        self.assertEqual(
            {
                state.value
                for state in BouncerState
            },
            {
                "standing_outside_bar",
                "responding_inside_bar",
                "inside_and_outside_bar",
            },
        )


if __name__ == "__main__":
    unittest.main()
