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


    def test_new_drink_can_be_promoted_to_regular_menu(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        recipe = {
            "name": "singularity",
            "status": "approved",
            "approved": True,
            "ingredients": [
                "raspberry_rum",
                "lemonade"
            ]
        }

        meeting_place.add_approved_cocktail(
            recipe
        )

        self.assertIn(
            "singularity",
            meeting_place.new_drinks
        )

        meeting_place.promote_new_drink(
            "singularity"
        )

        self.assertNotIn(
            "singularity",
            meeting_place.new_drinks
        )

        self.assertIs(
            meeting_place.drink_menu[
                "singularity"
            ],
            recipe
        )

        meeting_place.bar_menu_sign.open()

        rendered = (
            meeting_place
            .bar_menu_sign
            .render()
        )

        self.assertIn(
            "singularity",
            rendered
        )

        self.assertNotIn(
            "singularity [NOVINKA]",
            rendered
        )


    def test_unknown_new_drink_cannot_be_promoted(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        with self.assertRaises(
            ValueError
        ):
            meeting_place.promote_new_drink(
                "nonexistent"
            )


    def test_new_drink_is_promoted_after_quarter_bar_year(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        recipe = {
            "name": "singularity",
            "status": "approved",
            "approved": True,
            "ingredients": []
        }

        meeting_place.add_approved_cocktail(
            recipe
        )

        self.assertIn(
            "singularity",
            meeting_place.new_drinks
        )

        for _ in range(
            89 * 24
        ):
            meeting_place.tick()

        self.assertIn(
            "singularity",
            meeting_place.new_drinks
        )

        for _ in range(24):
            meeting_place.tick()

        self.assertNotIn(
            "singularity",
            meeting_place.new_drinks
        )

        self.assertIn(
            "singularity",
            meeting_place.drink_menu
        )


    def test_new_drink_age_counts_from_menu_added_day(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        for _ in range(
            50 * 24
        ):
            meeting_place.tick()

        recipe = {
            "name": "singularity",
            "status": "approved",
            "approved": True,
            "ingredients": []
        }

        meeting_place.add_approved_cocktail(
            recipe
        )

        self.assertEqual(
            recipe["menu_added_day"],
            50
        )

        for _ in range(
            89 * 24
        ):
            meeting_place.tick()

        self.assertIn(
            "singularity",
            meeting_place.new_drinks
        )

        for _ in range(24):
            meeting_place.tick()

        self.assertNotIn(
            "singularity",
            meeting_place.new_drinks
        )

        self.assertIn(
            "singularity",
            meeting_place.drink_menu
        )


if __name__ == "__main__":
    unittest.main()
