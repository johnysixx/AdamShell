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


if __name__ == "__main__":
    unittest.main()
