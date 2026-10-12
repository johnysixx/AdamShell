from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class BarMenuHomeScreen:
    sections: tuple[str, ...] = (
        "menu",
    )

    screen: str = field(
        default="home",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "sections",
            tuple(
                str(section)
                for section
                in self.sections
            ),
        )

    def to_dict(self):
        return {
            "screen": self.screen,
            "sections": list(
                self.sections
            ),
        }


@dataclass(slots=True, frozen=True)
class BarMenuNewScreen:
    drinks: dict

    screen: str = field(
        default="new",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.drinks,
            dict,
        ):
            raise TypeError(
                "Bar menu new-drinks screen "
                "requires a drink registry dict."
            )

    def to_dict(self):
        return {
            "screen": self.screen,
            "drinks": self.drinks,
        }


@dataclass(slots=True, frozen=True)
class BarMenuListScreen:
    drinks: dict
    new_drinks: dict

    screen: str = field(
        default="menu",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.drinks,
            dict,
        ):
            raise TypeError(
                "Bar menu screen requires "
                "a drink registry dict."
            )

        if not isinstance(
            self.new_drinks,
            dict,
        ):
            raise TypeError(
                "Bar menu screen requires "
                "a new-drink registry dict."
            )

    def to_dict(self):
        return {
            "screen": self.screen,
            "drinks": self.drinks,
            "new_drinks":
                self.new_drinks,
        }


@dataclass(slots=True, frozen=True)
class BarMenuDrinkDetailScreen:
    drink: str
    is_new: bool
    ingredients: tuple[str, ...]

    screen: str = field(
        default="drink_detail",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "drink",
            str(self.drink),
        )

        object.__setattr__(
            self,
            "is_new",
            bool(self.is_new),
        )

        object.__setattr__(
            self,
            "ingredients",
            tuple(
                str(ingredient)
                for ingredient
                in self.ingredients
            ),
        )

    def to_dict(self):
        return {
            "screen": self.screen,
            "drink": self.drink,
            "is_new": self.is_new,
            "ingredients": list(
                self.ingredients
            ),
        }


BAR_MENU_SCREEN_TYPES = (
    BarMenuHomeScreen,
    BarMenuNewScreen,
    BarMenuListScreen,
    BarMenuDrinkDetailScreen,
)
