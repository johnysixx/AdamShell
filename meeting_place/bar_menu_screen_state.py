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
    drinks: tuple[str, ...]

    screen: str = field(
        default="new",
        init=False,
    )

    def __post_init__(self):
        if (
            not isinstance(self.drinks, tuple)
            or any(
                not isinstance(name, str)
                for name in self.drinks
            )
        ):
            raise TypeError(
                "New-drinks screen requires "
                "an immutable tuple of drink names."
            )

    def to_dict(self):
        return {
            "screen": self.screen,
            "drinks": list(self.drinks),
        }


@dataclass(slots=True, frozen=True)
class BarMenuListScreen:
    drinks: tuple[str, ...]
    new_drinks: tuple[str, ...]

    screen: str = field(
        default="menu",
        init=False,
    )

    def __post_init__(self):
        for field_name in (
            "drinks",
            "new_drinks",
        ):
            names = getattr(
                self,
                field_name,
            )

            if (
                not isinstance(names, tuple)
                or any(
                    not isinstance(name, str)
                    for name in names
                )
            ):
                raise TypeError(
                    "Menu screens require "
                    "immutable tuples of drink names."
                )

    def to_dict(self):
        return {
            "screen": self.screen,
            "drinks": list(self.drinks),
            "new_drinks": list(self.new_drinks),
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
