import unittest

from meeting_place.dark_matter_door_sign import (
    DarkMatterDoorSign,
)
from meeting_place.dark_matter_door_sign_state import (
    DarkMatterDoorSignState,
)
from meeting_place.dark_matter_sign import (
    DarkMatterSign,
)
from meeting_place.dark_matter_sign_state import (
    DarkMatterSignState,
)
from meeting_place.dark_matter_tank import (
    DarkMatterTank,
)


class DarkMatterSignStateObjectStateTests(
    unittest.TestCase
):

    def test_main_sign_starts_coming_soon_as_enum(self):
        sign = DarkMatterSign()

        self.assertIs(
            sign.state,
            DarkMatterSignState.COMING_SOON,
        )

        self.assertEqual(
            sign.public_state["state"],
            "coming_soon",
        )

    def test_main_sign_becomes_available_from_tank_state(self):
        sign = DarkMatterSign()
        tank = DarkMatterTank()

        self.assertTrue(
            sign.attach_tank(tank)
        )

        self.assertIs(
            sign.state,
            DarkMatterSignState.COMING_SOON,
        )

        tank.dark_matter_kg = 1.0

        self.assertIs(
            sign.state,
            DarkMatterSignState.AVAILABLE,
        )

        self.assertEqual(
            sign.public_state["state"],
            "available",
        )

    def test_door_sign_starts_inside_as_enum(self):
        sign = DarkMatterDoorSign()

        self.assertIs(
            sign.state,
            DarkMatterDoorSignState.COMING_SOON_INSIDE,
        )

        self.assertEqual(
            sign.public_state["state"],
            "coming_soon_inside",
        )

    def test_door_sign_moves_outside_when_available(self):
        sign = DarkMatterDoorSign()
        tank = DarkMatterTank()

        sign.attach_tank(
            tank
        )

        tank.dark_matter_kg = 1.0

        self.assertIs(
            sign.state,
            DarkMatterDoorSignState.AVAILABLE_OUTSIDE,
        )

        self.assertEqual(
            sign.public_state["state"],
            "available_outside",
        )

    def test_sign_state_domains_remain_separate(self):
        self.assertEqual(
            {
                state.value
                for state
                in DarkMatterSignState
            },
            {
                "coming_soon",
                "available",
            },
        )

        self.assertEqual(
            {
                state.value
                for state
                in DarkMatterDoorSignState
            },
            {
                "coming_soon_inside",
                "available_outside",
            },
        )


if __name__ == "__main__":
    unittest.main()
