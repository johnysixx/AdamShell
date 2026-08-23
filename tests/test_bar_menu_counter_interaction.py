import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from meeting_place.meeting_place import MeetingPlace


class BarMenuCounterInteractionTests(unittest.TestCase):

    def test_counter_tap_opens_drink_detail_on_menu_screen(
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
            "status": "approved",
            "ingredients": [
                "raspberry_rum",
                "lemonade"
            ]
        }

        meeting_place.bar_menu_sign.open()
        meeting_place.bar_menu_sign.open_section(
            "menu"
        )

        meeting_place.bar_counter.tap_menu_drink(
            "singularity"
        )

        self.assertEqual(
            meeting_place
            .bar_menu_sign
            .current_screen["screen"],
            "drink_detail"
        )

        self.assertEqual(
            meeting_place
            .bar_menu_sign
            .current_screen["drink"],
            "singularity"
        )


    def test_counter_back_tap_returns_menu_screen(
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
            "status": "approved",
            "ingredients": []
        }

        meeting_place.bar_menu_sign.open()
        meeting_place.bar_menu_sign.open_section(
            "menu"
        )
        meeting_place.bar_menu_sign.open_drink(
            "singularity"
        )

        meeting_place.bar_counter.tap_menu_back()

        self.assertEqual(
            meeting_place
            .bar_menu_sign
            .current_screen["screen"],
            "menu"
        )


    def test_counter_routes_generic_menu_taps(
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
            "status": "approved",
            "ingredients": []
        }

        meeting_place.bar_menu_sign.open()
        meeting_place.bar_menu_sign.open_section(
            "menu"
        )

        meeting_place.bar_counter.tap_menu(
            "singularity"
        )

        self.assertEqual(
            meeting_place
            .bar_menu_sign
            .current_screen["screen"],
            "drink_detail"
        )

        meeting_place.bar_counter.tap_menu(
            "back"
        )

        self.assertEqual(
            meeting_place
            .bar_menu_sign
            .current_screen["screen"],
            "menu"
        )


    def test_unknown_menu_tap_is_ignored(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.bar_menu_sign.open()
        meeting_place.bar_menu_sign.open_section(
            "menu"
        )

        before = (
            meeting_place
            .bar_menu_sign
            .current_screen
        )

        result = (
            meeting_place
            .bar_counter
            .tap_menu(
                "nonexistent"
            )
        )

        self.assertFalse(
            result
        )

        self.assertIs(
            meeting_place
            .bar_menu_sign
            .current_screen,
            before
        )


    def test_plain_counter_tap_opens_menu_home(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.bar_menu_sign.open()
        meeting_place.bar_menu_sign.open_section(
            "menu"
        )

        result = (
            meeting_place
            .bar_counter
            .tap_menu()
        )

        self.assertEqual(
            result["screen"],
            "home"
        )

        self.assertEqual(
            meeting_place
            .bar_menu_sign
            .current_screen["screen"],
            "home"
        )


if __name__ == "__main__":
    unittest.main()




