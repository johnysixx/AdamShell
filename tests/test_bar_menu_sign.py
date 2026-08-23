import unittest

from meeting_place.bar_menu_sign import (
    BarMenuSign
)


class BarMenuSignTests(unittest.TestCase):

    def test_sign_shows_regular_menu_and_new_drinks(
        self
    ):
        drink_menu = {
            "raspberry_rum": {
                "name": "raspberry_rum",
                "type": "bar_drink"
            }
        }

        new_drinks = {
            "singularity": {
                "name": "singularity",
                "status": "approved",
                "approved": True,
                "ingredients": [
                    "raspberry_rum",
                    "lemonade"
                ]
            }
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

        new_drinks["singularity"] = {
            "name": "singularity",
            "status": "approved"
        }

        self.assertIn(
            "singularity",
            sign.public_state["new_drinks"]
        )


    def test_sign_home_has_single_menu_section(
        self
    ):
        drink_menu = {
            "raspberry_rum": {
                "name": "raspberry_rum"
            }
        }

        new_drinks = {
            "singularity": {
                "name": "singularity",
                "status": "approved"
            }
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
            "raspberry_rum": {
                "name": "raspberry_rum",
                "type": "bar_drink"
            }
        }

        new_drinks = {
            "singularity": {
                "name": "singularity",
                "status": "approved",
                "ingredients": [
                    "raspberry_rum",
                    "lemonade"
                ]
            }
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
            "raspberry_rum": {
                "name": "raspberry_rum"
            }
        }

        new_drinks = {
            "singularity": {
                "name": "singularity",
                "status": "approved",
                "ingredients": [
                    "raspberry_rum",
                    "lemonade"
                ]
            }
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
                "raspberry_rum": {
                    "name": "raspberry_rum"
                }
            },
            new_drinks={
                "singularity": {
                    "name": "singularity"
                }
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
                "singularity": {
                    "name": "singularity"
                },
                "event_horizon": {
                    "name": "event_horizon"
                }
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
                "raspberry_rum": {
                    "name": "raspberry_rum"
                },
                "absinthe": {
                    "name": "absinthe"
                }
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
                "singularity": {
                    "name": "singularity",
                    "status": "approved",
                    "ingredients": [
                        "raspberry_rum",
                        "lemonade"
                    ]
                }
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
                "raspberry_rum": {
                    "name": "raspberry_rum"
                }
            },
            new_drinks={
                "singularity": {
                    "name": "singularity",
                    "status": "approved"
                }
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
                "raspberry_rum": {
                    "name": "raspberry_rum"
                },
                "absinthe": {
                    "name": "absinthe"
                }
            },
            new_drinks={
                "singularity": {
                    "name": "singularity",
                    "status": "approved"
                }
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


if __name__ == "__main__":
    unittest.main()














