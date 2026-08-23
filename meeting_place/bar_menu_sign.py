from universe.logger import UniverseLogger


class BarMenuSign:

    def __init__(
        self,
        drink_menu,
        new_drinks
    ):
        self.name = "bar_menu_sign"
        self.type = "bar_display"
        self.location = "inside_bar"

        self.drink_menu = drink_menu
        self.new_drinks = new_drinks

        self.current_screen = None
        self.screen_history = []

        self.idle_minutes = 0
        self.INACTIVITY_TIMEOUT_MINUTES = 5

        self.idle_minutes = 0
        self.INACTIVITY_TIMEOUT_MINUTES = 5

        self.idle_minutes = 0
        self.INACTIVITY_TIMEOUT_MINUTES = 5

        UniverseLogger.boot(
            "BAR MENU SIGN CREATED"
        )

    def _reset_idle(
        self
    ):
        self.idle_minutes = 0

    def _show_screen(
        self,
        screen
    ):
        self._reset_idle()

        if self.current_screen is not None:
            self.screen_history.append(
                self.current_screen
            )

        self.current_screen = screen

        return screen

    def open(
        self
    ):
        self._reset_idle()
        self.screen_history = []

        screen = {
            "screen": "home",
            "sections": [
                "menu"
            ]
        }

        self.current_screen = screen

        return screen

    def open_section(
        self,
        section
    ):
        if section == "new":
            screen = {
                "screen": "new",
                "drinks": self.new_drinks
            }

        elif section == "menu":
            screen = {
                "screen": "menu",
                "drinks": self.drink_menu,
                "new_drinks": self.new_drinks
            }

        else:
            raise ValueError(
                "Unknown bar menu section."
            )

        return self._show_screen(
            screen
        )

    def open_drink(
        self,
        drink_name
    ):
        if drink_name in self.new_drinks:
            drink = self.new_drinks[
                drink_name
            ]
            is_new = True

        elif drink_name in self.drink_menu:
            drink = self.drink_menu[
                drink_name
            ]
            is_new = False

        else:
            raise ValueError(
                "Unknown bar drink."
            )

        if isinstance(
            drink,
            dict
        ):
            ingredients = drink.get(
                "ingredients",
                []
            )
        else:
            ingredients = getattr(
                drink,
                "ingredients",
                []
            )

        screen = {
            "screen": "drink_detail",
            "drink": drink_name,
            "is_new": is_new,
            "ingredients": list(
                ingredients
            )
        }

        return self._show_screen(
            screen
        )

    def back(
        self
    ):
        self._reset_idle()

        if not self.screen_history:
            return self.current_screen

        self.current_screen = (
            self.screen_history.pop()
        )

        return self.current_screen
    def advance_minutes(
        self,
        minutes
    ):
        if minutes < 0:
            raise ValueError(
                "Minutes cannot be negative."
            )

        for _ in range(minutes):
            self.idle_minute()

        return self.current_screen

    def idle_minute(
        self
    ):
        if (
            self.current_screen is None
            or self.current_screen.get(
                "screen"
            ) == "home"
        ):
            self.idle_minutes = 0
            return self.current_screen

        self.idle_minutes += 1

        if (
            self.idle_minutes
            >= self.INACTIVITY_TIMEOUT_MINUTES
        ):
            self.open()

        return self.current_screen

    def render(
        self
    ):
        if self.current_screen is None:
            self.open()

        screen = self.current_screen.get(
            "screen"
        )

        if screen == "home":
            lines = [
                "=== BAR MENU ===",
                ""
            ]

            for drink_name in self.drink_menu:
                lines.append(
                    f"- {drink_name}"
                )

            for drink_name in self.new_drinks:
                if drink_name in self.drink_menu:
                    continue

                lines.append(
                    f"- {drink_name} [NOVINKA]"
                )

            return "\n".join(
                lines
            )

        if screen == "new":
            drinks = (
                self.current_screen.get(
                    "drinks",
                    {}
                )
            )

            lines = [
                "=== NOVINKY ===",
                ""
            ]

            for drink_name in drinks:
                lines.append(
                    f"- {drink_name}"
                )

            return "\n".join(
                lines
            )

        if screen == "menu":
            drinks = self.current_screen.get(
                "drinks",
                {}
            )

            new_drinks = self.current_screen.get(
                "new_drinks",
                {}
            )

            lines = [
                "=== BAR MENU ===",
                ""
            ]

            for drink_name in drinks:
                lines.append(
                    f"- {drink_name}"
                )

            for drink_name in new_drinks:
                if drink_name in drinks:
                    continue

                lines.append(
                    f"- {drink_name} [NOVINKA]"
                )

            return "\n".join(
                lines
            )
        if screen == "drink_detail":
            drink_name = (
                self.current_screen.get(
                    "drink",
                    ""
                )
            )

            is_new = (
                self.current_screen.get(
                    "is_new",
                    False
                )
            )

            ingredients = (
                self.current_screen.get(
                    "ingredients",
                    []
                )
            )

            lines = [
                f"=== {drink_name.upper()} ==="
            ]

            if is_new:
                lines.append(
                    "NOVINKA"
                )

            if ingredients:
                lines.extend(
                    [
                        "",
                        "Ingredience:"
                    ]
                )

                for ingredient in ingredients:
                    lines.append(
                        f"- {ingredient}"
                    )

            return "\n".join(
                lines
            )

        return ""

    @property
    def public_state(
        self
    ):
        return {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "drinks": self.drink_menu,
            "new_drinks": self.new_drinks
        }























