import unittest

from meeting_place.bar_menu_sign import (
    BarMenuSign
)
from meeting_place.bar_objects import BarMenuItem, DrinkRecipe


class BarMenuSignTests(unittest.TestCase):

    def _menu_item(self, name):
        return BarMenuItem(
            name=name,
            type="bar_drink",
            menu_source="test",
        )

    def _new_drink(
        self,
        name="singularity",
        ingredients=(),
        status=None,
    ):
        return DrinkRecipe(
            name=name,
            origin="test_recipe",
            ingredients=list(ingredients),
            status=status,
            approved=status == "approved",
        )

    def test_sign_shows_regular_menu_and_new_drinks(
        self
    ):
        drink_menu = {
            "raspberry_rum": self._menu_item("raspberry_rum")
        }

        new_drinks = {
            "singularity": self._new_drink(
                ingredients=("raspberry_rum", "lemonade"),
                status="approved",
            )
        }

        sign = BarMenuSign(
            drink_menu=drink_menu,
            new_drinks=new_drinks
        )

        state = sign.public_state

        self.assertEqual(
            state["name"],
            "bar_menu_sign"
        )

        self.assertEqual(
            state["type"],
            "bar_display"
        )

        self.assertEqual(
            state["location"],
            "inside_bar"
        )

        self.assertIn(
            "raspberry_rum",
            state["drinks"]
        )

        self.assertIn(
            "singularity",
            state["new_drinks"]
        )


    def test_sign_updates_when_bar_menu_changes(
        self
    ):
        drink_menu = {}
        new_drinks = {}

        sign = BarMenuSign(
            drink_menu=drink_menu,
            new_drinks=new_drinks
        )

        self.assertEqual(
            sign.public_state["new_drinks"],
            {}
        )

        new_drinks["singularity"] = self._new_drink(
            status="approved"
        )

        self.assertIn(
            "singularity",
            sign.public_state["new_drinks"]
        )


    def test_sign_home_has_single_menu_section(
        self
    ):
        drink_menu = {
            "raspberry_rum": self._menu_item("raspberry_rum")
        }

        new_drinks = {
            "singularity": self._new_drink(
                status="approved"
            )
        }

        sign = BarMenuSign(
            drink_menu=drink_menu,
            new_drinks=new_drinks
        )

        home = sign.open()

        self.assertEqual(
            home["screen"],
            "home"
        )

        self.assertEqual(
            home["sections"],
            [
                "menu"
            ]
        )

    def test_sign_can_open_drink_detail(
        self
    ):
        drink_menu = {
            "raspberry_rum": self._menu_item("raspberry_rum")
        }

        new_drinks = {
            "singularity": self._new_drink(
                ingredients=(
                    "raspberry_rum",
                    "lemonade",
                ),
                status="approved",
            )
        }

        sign = BarMenuSign(
            drink_menu=drink_menu,
            new_drinks=new_drinks
        )

        detail = sign.open_drink(
            "singularity"
        )

        self.assertEqual(
            detail["screen"],
            "drink_detail"
        )

        self.assertEqual(
            detail["drink"],
            "singularity"
        )

        self.assertTrue(
            detail["is_new"]
        )

        self.assertEqual(
            detail["ingredients"],
            [
                "raspberry_rum",
                "lemonade"
            ]
        )


    def test_sign_can_navigate_back_through_history(
        self
    ):
        drink_menu = {
            "raspberry_rum": self._menu_item("raspberry_rum")
        }

        new_drinks = {
            "singularity": self._new_drink(
                ingredients=(
                    "raspberry_rum",
                    "lemonade",
                ),
                status="approved",
            )
        }

        sign = BarMenuSign(
            drink_menu=drink_menu,
            new_drinks=new_drinks
        )

        sign.open()

        sign.open_section(
            "new"
        )

        sign.open_drink(
            "singularity"
        )

        self.assertEqual(
            sign.current_screen["screen"],
            "drink_detail"
        )

        screen = sign.back()

        self.assertEqual(
            screen["screen"],
            "new"
        )

        self.assertEqual(
            sign.current_screen["screen"],
            "new"
        )

        screen = sign.back()

        self.assertEqual(
            screen["screen"],
            "home"
        )

        self.assertEqual(
            sign.current_screen["screen"],
            "home"
        )


    def test_sign_renders_home_screen_as_text(
        self
    ):
        sign = BarMenuSign(
            drink_menu={
                "raspberry_rum": self._menu_item("raspberry_rum")
            },
            new_drinks={
                "singularity": self._new_drink()
            }
        )

        sign.open()

        rendered = sign.render()

        self.assertIn(
            "BAR MENU",
            rendered
        )

        self.assertIn(
            "singularity",
            rendered
        )

        self.assertIn(
            "[NOVINKA]",
            rendered
        )

        self.assertIn(
            "BAR MENU",
            rendered
        )


    def test_sign_renders_new_drinks_section_as_text(
        self
    ):
        sign = BarMenuSign(
            drink_menu={},
            new_drinks={
                "singularity": self._new_drink(),
                "event_horizon": self._new_drink(
                    name="event_horizon"
                )
            }
        )

        sign.open()
        sign.open_section(
            "new"
        )

        rendered = sign.render()

        self.assertIn(
            "NOVINKY",
            rendered
        )

        self.assertIn(
            "singularity",
            rendered
        )

        self.assertIn(
            "event_horizon",
            rendered
        )

    def test_sign_renders_regular_menu_as_text(
        self
    ):
        sign = BarMenuSign(
            drink_menu={
                "raspberry_rum": self._menu_item("raspberry_rum"),
                "absinthe": self._menu_item("absinthe"),
            },
            new_drinks={}
        )

        sign.open()
        sign.open_section(
            "menu"
        )

        rendered = sign.render()

        self.assertIn(
            "BAR MENU",
            rendered
        )

        self.assertIn(
            "raspberry_rum",
            rendered
        )

        self.assertIn(
            "absinthe",
            rendered
        )


    def test_sign_renders_drink_detail_as_text(
        self
    ):
        sign = BarMenuSign(
            drink_menu={},
            new_drinks={
                "singularity": self._new_drink(
                    ingredients=(
                        "raspberry_rum",
                        "lemonade",
                    ),
                    status="approved",
                )
            }
        )

        sign.open()
        sign.open_section(
            "new"
        )
        sign.open_drink(
            "singularity"
        )

        rendered = sign.render()

        self.assertIn(
            "SINGULARITY",
            rendered
        )

        self.assertIn(
            "NOVINKA",
            rendered
        )

        self.assertIn(
            "Ingredience",
            rendered
        )

        self.assertIn(
            "raspberry_rum",
            rendered
        )

        self.assertIn(
            "lemonade",
            rendered
        )


    def test_menu_merges_new_drinks_with_new_label(
        self
    ):
        sign = BarMenuSign(
            drink_menu={
                "raspberry_rum": self._menu_item("raspberry_rum")
            },
            new_drinks={
                "singularity": self._new_drink(
                    status="approved"
                )
            }
        )

        home = sign.open()

        self.assertEqual(
            home["sections"],
            [
                "menu"
            ]
        )

        sign.open_section(
            "menu"
        )

        rendered = sign.render()

        self.assertIn(
            "raspberry_rum",
            rendered
        )

        self.assertIn(
            "singularity",
            rendered
        )

        self.assertIn(
            "NOVINKA",
            rendered
        )


    def test_bar_menu_sign_is_display_not_terminal(
        self
    ):
        sign = BarMenuSign(
            drink_menu={},
            new_drinks={}
        )

        self.assertEqual(
            sign.type,
            "bar_display"
        )

        self.assertEqual(
            sign.public_state["type"],
            "bar_display"
        )


    def test_home_render_shows_full_menu_with_new_labels(
        self
    ):
        sign = BarMenuSign(
            drink_menu={
                "raspberry_rum": self._menu_item("raspberry_rum"),
                "absinthe": self._menu_item("absinthe"),
            },
            new_drinks={
                "singularity": self._new_drink(
                    status="approved"
                )
            }
        )

        sign.open()

        rendered = sign.render()

        self.assertIn(
            "BAR MENU",
            rendered
        )

        self.assertIn(
            "raspberry_rum",
            rendered
        )

        self.assertIn(
            "absinthe",
            rendered
        )

        self.assertIn(
            "singularity",
            rendered
        )

        self.assertIn(
            "[NOVINKA]",
            rendered
        )


    def test_drink_detail_returns_home_after_inactivity_timeout(
        self
    ):
        sign = BarMenuSign(
            drink_menu={},
            new_drinks={
                "singularity": self._new_drink()
            }
        )

        sign.open()
        sign.open_drink(
            "singularity"
        )

        self.assertEqual(
            sign.current_screen["screen"],
            "drink_detail"
        )

        for _ in range(5):
            sign.idle_minute()

        self.assertEqual(
            sign.current_screen["screen"],
            "home"
        )


    def test_interaction_resets_inactivity_timeout(
        self
    ):
        sign = BarMenuSign(
            drink_menu={},
            new_drinks={
                "singularity": self._new_drink()
            }
        )

        sign.open()
        sign.open_drink(
            "singularity"
        )

        for _ in range(4):
            sign.idle_minute()

        self.assertEqual(
            sign.idle_minutes,
            4
        )

        sign.open_drink(
            "singularity"
        )

        self.assertEqual(
            sign.idle_minutes,
            0
        )

        sign.idle_minute()

        self.assertEqual(
            sign.current_screen["screen"],
            "drink_detail"
        )


    def test_interaction_resets_inactivity_timeout(
        self
    ):
        sign = BarMenuSign(
            drink_menu={},
            new_drinks={
                "singularity": self._new_drink()
            }
        )

        sign.open()
        sign.open_drink(
            "singularity"
        )

        for _ in range(4):
            sign.idle_minute()

        self.assertEqual(
            sign.idle_minutes,
            4
        )

        sign.open_drink(
            "singularity"
        )

        self.assertEqual(
            sign.idle_minutes,
            0
        )

        sign.idle_minute()

        self.assertEqual(
            sign.current_screen["screen"],
            "drink_detail"
        )


if __name__ == "__main__":
    unittest.main()

















