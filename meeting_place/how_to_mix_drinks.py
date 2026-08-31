from universe.logger import UniverseLogger

from meeting_place.bar_objects import (
    DrinkRecipe,
    RecipeIngredientRequirement,
)


class HowToMixDrinks:

    def __init__(self):

        self.name = (
            "how_to_mix_drinks"
        )

        self.type = (
            "bartender_recipe_book"
        )

        self.hidden_recipes = {
            "raspberry_rum":
                DrinkRecipe(
                    name=
                        "raspberry_rum",
                    origin=
                        "god_secret_recipe",
                    hidden=True,
                    learned=False,
                    teacher=None,
                    ingredients={
                        "rum":
                            RecipeIngredientRequirement(
                                shots=1,
                                consumed=False,
                            ),
                        "liquid_hydrocarbons":
                            RecipeIngredientRequirement(
                                shots=1,
                                consumed=True,
                            ),
                    },
                )
        }

        self.recipes = {
            "vodka_with_lemon":
                DrinkRecipe(
                    name=
                        "vodka_with_lemon",
                    origin=
                        "basic_bar_recipe",
                    hidden=False,
                    learned=True,
                    teacher=None,
                    category=
                        "basic_drink",
                    effects={},
                    price_basis=
                        "vodka",
                    ingredients={
                        "vodka":
                            RecipeIngredientRequirement(
                                shots=1,
                                consumed=False,
                            ),
                        "lemon":
                            RecipeIngredientRequirement(
                                shots=1,
                                consumed=False,
                                use="drop",
                            ),
                    },
                )
        }

        UniverseLogger.boot(
            "HOW TO MIX DRINKS CREATED"
        )

    def reveal_hidden_recipe(
        self,
        name,
        teacher
    ):

        if name in self.recipes:
            return self.recipes[
                name
            ]

        recipe = (
            self.hidden_recipes
            .get(name)
        )

        if recipe is None:
            raise ValueError(
                "Unknown hidden cocktail "
                "recipe."
            )

        recipe.reveal(
            teacher
        )

        self.recipes[
            name
        ] = recipe

        del self.hidden_recipes[
            name
        ]

        UniverseLogger.event(
            "HOW TO MIX DRINKS "
            "SECRET RECIPE REVEALED: "
            f"{name} BY {teacher}"
        )

        return recipe

    def add_created_recipe(
        self,
        name,
        ingredients
    ):

        recipe = DrinkRecipe(
            name=name,
            origin=
                "created_by_bartender",
            status="testing",
            ingredients=list(
                ingredients
            ),
            tastings=[],
            votes_for=0,
            votes_against=0,
            approved=False,
        )

        self.recipes[
            name
        ] = recipe

        UniverseLogger.event(
            "HOW TO MIX DRINKS "
            "RECIPE ADDED: "
            f"{name}"
        )

        return recipe

    def record_tasting(
        self,
        drink,
        guest,
        liked,
        comment=None
    ):

        if drink not in self.recipes:
            raise ValueError(
                "Unknown cocktail recipe."
            )

        recipe = self.recipes[
            drink
        ]

        tasting = (
            recipe.record_tasting(
                guest=guest,
                liked=liked,
                comment=comment,
            )
        )

        UniverseLogger.event(
            "HOW TO MIX DRINKS "
            "TASTING RECORDED: "
            f"{drink} BY {guest}"
        )

        return tasting
