import unittest

from meeting_place.bar_hex_geometry import BarHexGeometry
from meeting_place.bar_service_protocol import (
    BarServiceProtocol,
)
from meeting_place.bartender import Bartender
from meeting_place.bartender_state import BartenderState


class BartenderStateObjectStateTests(
    unittest.TestCase
):

    def test_bartender_starts_present_as_enum(self):
        bartender = Bartender(
            story_book=object()
        )

        self.assertIs(
            bartender.state,
            BartenderState.PRESENT,
        )

    def test_service_protocol_moves_bartender_behind_bar(
        self
    ):
        bartender = Bartender(
            story_book=object()
        )
        protocol = BarServiceProtocol(
            BarHexGeometry()
        )

        result = protocol.place_bartender(
            bartender
        )

        self.assertTrue(result)
        self.assertIs(
            bartender.state,
            BartenderState.BEHIND_BAR,
        )

    def test_string_state_is_rejected(self):
        bartender = Bartender(
            story_book=object()
        )

        with self.assertRaises(TypeError):
            bartender.state = "behind_bar"

    def test_state_values_define_domain_names(self):
        self.assertEqual(
            {
                state.value
                for state in BartenderState
            },
            {
                "present",
                "behind_bar",
            },
        )


if __name__ == "__main__":
    unittest.main()
