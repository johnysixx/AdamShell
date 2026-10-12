from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    BarDrink,
    DrinkRecipe,
)
from meeting_place.bar_receipt_state import (
    BarReceiptState,
)
from meeting_place.bartender_chronicle_state import (
    BartenderLearnedGuestDrinkEntry,
)


@dataclass(slots=True, frozen=True)
class LilithRequestedRecipeState:
    vodka: int = 1
    lemon: str = "whole"
    sugar: int = 1

    def to_dict(self):
        return {
            "vodka": self.vodka,
            "lemon": self.lemon,
            "sugar": self.sugar,
        }


@dataclass(slots=True, frozen=True)
class BartenderMakesVodkaWithLemonEvent:
    name: str = field(
        default="bartender_makes_vodka_with_lemon",
        init=False,
    )
    guest: str = field(
        default="lilith",
        init=False,
    )
    drink: str = field(
        default="vodka_with_lemon",
        init=False,
    )
    price_basis: str = field(
        default="vodka",
        init=False,
    )
    effects_present: bool = field(
        default=False,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "price_basis": self.price_basis,
            "effects": {},
        }


@dataclass(slots=True, frozen=True)
class LilithCorrectsVodkaWithLemonEvent:
    requested_recipe: LilithRequestedRecipeState

    name: str = field(
        default="lilith_corrects_vodka_with_lemon",
        init=False,
    )
    guest: str = field(
        default="lilith",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.requested_recipe,
            LilithRequestedRecipeState,
        ):
            raise TypeError(
                "Lilith drink correction requires "
                "LilithRequestedRecipeState."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "requested_recipe":
                self.requested_recipe.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class LilithDrinkRecipeSnapshot:
    drink: str
    teacher: str
    price_basis: str
    vodka_shots: int
    lemon_shots: int
    lemon_use: str
    sugar_shots: int
    energy_j: float
    creative_will: float

    @classmethod
    def from_recipe(
        cls,
        recipe,
    ):
        if not isinstance(
            recipe,
            DrinkRecipe,
        ):
            raise TypeError(
                "Lilith recipe snapshot requires "
                "a DrinkRecipe object."
            )

        return cls(
            drink=recipe.name,
            teacher=recipe.teacher,
            price_basis=recipe.price_basis,
            vodka_shots=(
                recipe.ingredients[
                    "vodka"
                ].shots
            ),
            lemon_shots=(
                recipe.ingredients[
                    "lemon"
                ].shots
            ),
            lemon_use=(
                recipe.ingredients[
                    "lemon"
                ].use
            ),
            sugar_shots=(
                recipe.ingredients[
                    "sugar"
                ].shots
            ),
            energy_j=float(
                recipe.effects[
                    "energy_j"
                ]
            ),
            creative_will=float(
                recipe.effects[
                    "creative_will"
                ]
            ),
        )

    def to_dict(self):
        return {
            "name": self.drink,
            "teacher": self.teacher,
            "price_basis":
                self.price_basis,
            "ingredients": {
                "vodka": {
                    "shots":
                        self.vodka_shots,
                },
                "lemon": {
                    "shots":
                        self.lemon_shots,
                    "use":
                        self.lemon_use,
                },
                "sugar": {
                    "shots":
                        self.sugar_shots,
                },
            },
            "effects": {
                "energy_j":
                    self.energy_j,
                "creative_will":
                    self.creative_will,
            },
        }


@dataclass(slots=True, frozen=True)
class BartenderLearnsLilithDrinkEvent:
    recipe: LilithDrinkRecipeSnapshot

    name: str = field(
        default="bartender_learns_lilith",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.recipe,
            LilithDrinkRecipeSnapshot,
        ):
            raise TypeError(
                "Bartender learned Lilith event "
                "requires a typed recipe snapshot."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "recipe":
                self.recipe.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class BartenderLearnsLilithDrinkResult:
    recipe: DrinkRecipe
    learned: BartenderLearnedGuestDrinkEntry

    def __post_init__(self):
        if not isinstance(
            self.recipe,
            DrinkRecipe,
        ):
            raise TypeError(
                "Learned Lilith drink result "
                "requires DrinkRecipe."
            )

        if not isinstance(
            self.learned,
            BartenderLearnedGuestDrinkEntry,
        ):
            raise TypeError(
                "Learned Lilith drink result "
                "requires typed bartender memory."
            )

    def to_dict(self):
        return {
            "recipe":
                self.recipe.to_dict(),
            "learned":
                self.learned.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class LilithDrinkEffectAppliedResult:
    energy_j: float
    creative_will: float

    name: str = field(
        default="lilith_drink_effect_applied",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "energy_j",
            float(self.energy_j),
        )
        object.__setattr__(
            self,
            "creative_will",
            float(self.creative_will),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "energy_j": self.energy_j,
            "creative_will":
                self.creative_will,
        }


@dataclass(slots=True, frozen=True)
class BartenderMixesFinalLilithEvent:
    name: str = field(
        default="bartender_mixes_final_lilith",
        init=False,
    )
    guest: str = field(
        default="lilith",
        init=False,
    )
    drink: str = field(
        default="lilith",
        init=False,
    )
    sugar_cubes: int = field(
        default=1,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "sugar_cubes":
                self.sugar_cubes,
        }


@dataclass(slots=True, frozen=True)
class BartenderHandsLilithDrinkEvent:
    receipt_number: int | str

    name: str = field(
        default=(
            "bartender_hands_lilith_"
            "drink_and_receipt"
        ),
        init=False,
    )
    guest: str = field(
        default="lilith",
        init=False,
    )
    drink: str = field(
        default="lilith",
        init=False,
    )
    paid: bool = field(
        default=False,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "receipt_number":
                self.receipt_number,
            "paid": self.paid,
        }


@dataclass(slots=True, frozen=True)
class LilithDrinkServiceResult:
    drink: BarDrink
    receipt: BarReceiptState

    def __post_init__(self):
        if not isinstance(
            self.drink,
            BarDrink,
        ):
            raise TypeError(
                "Lilith service result requires "
                "a BarDrink object."
            )

        if not isinstance(
            self.receipt,
            BarReceiptState,
        ):
            raise TypeError(
                "Lilith service result requires "
                "a BarReceiptState object."
            )

    def to_dict(self):
        return {
            "drink":
                self.drink.to_dict(),
            "receipt":
                self.receipt.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class DrinkIngredientRequestState:
    ingredient: str
    amount: int
    unit: str

    def __post_init__(self):
        object.__setattr__(
            self,
            "ingredient",
            str(self.ingredient),
        )
        object.__setattr__(
            self,
            "amount",
            int(self.amount),
        )
        object.__setattr__(
            self,
            "unit",
            str(self.unit),
        )

    def to_dict(self):
        return {
            "ingredient":
                self.ingredient,
            "amount":
                self.amount,
            "unit":
                self.unit,
        }


@dataclass(slots=True, frozen=True)
class LilithRequestsSecondSugarCubeEvent:
    request: DrinkIngredientRequestState

    name: str = field(
        default=(
            "lilith_tastes_and_requests_"
            "second_sugar_cube"
        ),
        init=False,
    )
    guest: str = field(
        default="lilith",
        init=False,
    )
    drink: str = field(
        default="lilith",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.request,
            DrinkIngredientRequestState,
        ):
            raise TypeError(
                "Lilith sugar request requires "
                "DrinkIngredientRequestState."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "request":
                self.request.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class BartenderAddsSecondSugarCubeEvent:
    name: str = field(
        default="bartender_adds_second_sugar_cube",
        init=False,
    )
    guest: str = field(
        default="lilith",
        init=False,
    )
    drink: str = field(
        default="lilith",
        init=False,
    )
    final_sugar_cubes: int = field(
        default=2,
        init=False,
    )
    recipe_updated: bool = field(
        default=True,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "final_sugar_cubes":
                self.final_sugar_cubes,
            "recipe_updated":
                self.recipe_updated,
        }


@dataclass(slots=True, frozen=True)
class LilithDrinkRevisionResult:
    drink: BarDrink
    recipe: DrinkRecipe

    def __post_init__(self):
        if not isinstance(
            self.drink,
            BarDrink,
        ):
            raise TypeError(
                "Lilith revision result requires "
                "a BarDrink object."
            )

        if not isinstance(
            self.recipe,
            DrinkRecipe,
        ):
            raise TypeError(
                "Lilith revision result requires "
                "a DrinkRecipe object."
            )

    def to_dict(self):
        return {
            "drink":
                self.drink.to_dict(),
            "recipe":
                self.recipe.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class LilithJoinsSerpentAtTableEvent:
    name: str = field(
        default="lilith_joins_serpent_at_table",
        init=False,
    )
    guest: str = field(
        default="lilith",
        init=False,
    )
    companion: str = field(
        default="serpent",
        init=False,
    )
    drink_in_hand: str = field(
        default="lilith",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "with": self.companion,
            "drink_in_hand":
                self.drink_in_hand,
        }
