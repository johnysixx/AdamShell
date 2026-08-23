import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from meeting_place.meeting_place import MeetingPlace
from meeting_place.bar_menu_sign import BarMenuSign


class BarMenuSignIntegrationTests(unittest.TestCase):

    def test_meeting_place_has_live_bar_menu_sign(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        self.assertIsInstance(
            meeting_place.bar_menu_sign,
            BarMenuSign
        )

        self.assertIs(
            meeting_place.bar_menu_sign.drink_menu,
            meeting_place.drink_menu
        )

        self.assertIs(
            meeting_place.bar_menu_sign.new_drinks,
            meeting_place.new_drinks
        )


    def test_new_bar_drink_appears_on_menu_sign(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        drink = {
            "name": "absinthe",
            "type": "bar_drink"
        }

        meeting_place.add_drink(
            drink=drink,
            source="new_bottle"
        )

        self.assertIn(
            "absinthe",
            meeting_place
            .bar_menu_sign
            .public_state["drinks"]
        )


    def test_bar_tick_advances_menu_inactivity(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.new_drinks[
            "singularity"
        ] = {
            "name": "singularity",
            "ingredients": []
        }

        meeting_place.bar_menu_sign.open()
        meeting_place.bar_menu_sign.open_drink(
            "singularity"
        )

        self.assertEqual(
            meeting_place
            .bar_menu_sign
            .current_screen["screen"],
            "drink_detail"
        )

        meeting_place.tick()

        self.assertEqual(
            meeting_place
            .bar_menu_sign
            .current_screen["screen"],
            "home"
        )


    def test_bar_tick_keeps_home_screen_idle_at_zero(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.bar_menu_sign.open()

        meeting_place.tick()

        self.assertEqual(
            meeting_place
            .bar_menu_sign
            .current_screen["screen"],
            "home"
        )

        self.assertEqual(
            meeting_place
            .bar_menu_sign
            .idle_minutes,
            0
        )


if __name__ == "__main__":
    unittest.main()


