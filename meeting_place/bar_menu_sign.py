from universe.logger import UniverseLogger
from meeting_place.bar_objects import (
    BarMenuItem,
    DrinkRecipe,
)
from meeting_place.bar_menu_screen_state import (
    BAR_MENU_SCREEN_TYPES,
    BarMenuDrinkDetailScreen,
    BarMenuHomeScreen,
    BarMenuListScreen,
    BarMenuNewScreen,
)


class BarMenuSign:

    def __init__(
        self,
        drink_menu,
        new_drinks
    ):
        self.name = "bar_menu_sign"
        self.type = "bar_display"
        self.location = "inside_bar"

        if not isinstance(
            drink_menu,
            dict,
        ):
            raise TypeError(
                "Bar menu sign drink menu "
                "must be a registry dict."
            )

        if not isinstance(
            new_drinks,
            dict,
        ):
            raise TypeError(
                "Bar menu sign new drinks "
                "must be a registry dict."
            )

        self.drink_menu = drink_menu
        self.new_drinks = new_drinks

        self.current_screen = None
        self.screen_history = []

        self.idle_minutes = 0
        self.INACTIVITY_TIMEOUT_MINUTES = 5

        UniverseLogger.boot(
            "BAR MENU SIGN CREATED"
        )

    def _reset_idle(
        self
    ):
        self.idle_minutes = 0

    def _boundary(
        self,
        screen
    ):
        if screen is None:
            return None

        if not isinstance(
            screen,
            BAR_MENU_SCREEN_TYPES,
        ):
            raise TypeError(
                "Bar menu screen must use "
                "a typed screen state."
            )

        return screen.to_dict()

    def _show_screen(
        self,
        screen
    ):
        if not isinstance(
            screen,
            BAR_MENU_SCREEN_TYPES,
        ):
            raise TypeError(
                "Bar menu sign requires "
                "a typed screen state."
            )

        self._reset_idle()

        if self.current_screen is not None:
            self.screen_history.append(
                self.current_screen
            )

        self.current_screen = screen

        return self._boundary(
            screen
        )

    def open(
        self
    ):
        self._reset_idle()
        self.screen_history = []

        screen = BarMenuHomeScreen()

        self.current_screen = screen

        return self._boundary(
            screen
        )

    def open_section(
        self,
        section
    ):
        if section == "new":
            screen = BarMenuNewScreen(
                drinks=self.new_drinks,
            )

        elif section == "menu":
            screen = BarMenuListScreen(
                drinks=self.drink_menu,
                new_drinks=self.new_drinks,
            )

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

            if not isinstance(
                drink,
                DrinkRecipe,
            ):
                raise TypeError(
                    "New drink values must be "
                    "DrinkRecipe."
                )

            is_new = True

        elif drink_name in self.drink_menu:
            drink = self.drink_menu[
                drink_name
            ]

            if not isinstance(
                drink,
                BarMenuItem,
            ):
                raise TypeError(
                    "Bar menu values must be "
                    "BarMenuItem."
                )

            is_new = False

        else:
            raise ValueError(
                "Unknown bar drink."
            )

        screen = (
            BarMenuDrinkDetailScreen(
                drink=drink_name,
                is_new=is_new,
                ingredients=tuple(
                    drink.ingredients
                ),
            )
        )

        return self._show_screen(
            screen
        )

    def back(
        self
    ):
        self._reset_idle()

        if not self.screen_history:
            return self._boundary(
                self.current_screen
            )

        self.current_screen = (
            self.screen_history.pop()
        )

        return self._boundary(
            self.current_screen
        )

    def advance_minutes(
        self,
        minutes
    ):
        if minutes < 0:
            raise ValueError(
                "Minutes cannot be negative."
            )

        for _ in range(
            minutes
        ):
            self.idle_minute()

        return self._boundary(
            self.current_screen
        )

    def idle_minute(
        self
    ):
        if (
            self.current_screen is None
            or self.current_screen.screen
            == "home"
        ):
            self.idle_minutes = 0

            return self._boundary(
                self.current_screen
            )

        self.idle_minutes += 1

        if (
            self.idle_minutes
            >= self.INACTIVITY_TIMEOUT_MINUTES
        ):
            return self.open()

        return self._boundary(
            self.current_screen
        )

    def render(
        self
    ):
        if self.current_screen is None:
            self.open()

        screen = (
            self.current_screen.screen
        )

        if screen == "home":
            lines = [
                "=== BAR MENU ===",
                "",
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

        if isinstance(
            self.current_screen,
            BarMenuNewScreen,
        ):
            lines = [
                "=== NOVINKY ===",
                "",
            ]

            for drink_name in (
                self.current_screen
                .drinks
            ):
                lines.append(
                    f"- {drink_name}"
                )

            return "\n".join(
                lines
            )

        if isinstance(
            self.current_screen,
            BarMenuListScreen,
        ):
            drinks = (
                self.current_screen
                .drinks
            )

            new_drinks = (
                self.current_screen
                .new_drinks
            )

            lines = [
                "=== BAR MENU ===",
                "",
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

        if isinstance(
            self.current_screen,
            BarMenuDrinkDetailScreen,
        ):
            drink_name = (
                self.current_screen
                .drink
            )

            is_new = (
                self.current_screen
                .is_new
            )

            ingredients = (
                self.current_screen
                .ingredients
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
                        "Ingredience:",
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
            "new_drinks": self.new_drinks,
        }
