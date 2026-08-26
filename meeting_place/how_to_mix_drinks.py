from universe.logger import UniverseLogger


class HowToMixDrinks:

    def __init__(self):
        self.name = "how_to_mix_drinks"
        self.type = "bartender_recipe_book"
        self.hidden_recipes = {
            "raspberry_rum": {
                "name": "raspberry_rum",
                "origin": "god_secret_recipe",
                "hidden": True,
                "learned": False,
                "teacher": None,
                "ingredients": {
                    "rum": {
                        "shots": 1,
                        "consumed": False
                    },
                    "liquid_hydrocarbons": {
                        "shots": 1,
                        "consumed": True
                    }
                }
            }
        }

        self.recipes = {}
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

        recipe = self.hidden_recipes.get(
            name
        )

        if recipe is None:
            raise ValueError(
                "Unknown hidden cocktail recipe."
            )

        revealed = {
            key: value
            for key, value
            in recipe.items()
        }

        revealed[
            "ingredients"
        ] = {
            ingredient_name: dict(
                requirement
            )
            for (
                ingredient_name,
                requirement
            )
            in recipe[
                "ingredients"
            ].items()
        }

        revealed[
            "hidden"
        ] = False

        revealed[
            "learned"
        ] = True

        revealed[
            "teacher"
        ] = teacher

        revealed[
            "origin"
        ] = "taught_by_god"

        self.recipes[
            name
        ] = revealed

        del self.hidden_recipes[
            name
        ]

        UniverseLogger.event(
            "HOW TO MIX DRINKS SECRET RECIPE "
            f"REVEALED: {name} BY {teacher}"
        )

        return revealed


    def add_created_recipe(
        self,
        name,
        ingredients
    ):
        recipe = {
            "name": name,
            "origin": "created_by_bartender",
            "status": "testing",
            "ingredients": list(
                ingredients
            ),
            "tastings": [],
            "votes_for": 0,
            "votes_against": 0,
            "approved": False
        }

        self.recipes[
            name
        ] = recipe

        UniverseLogger.event(
            "HOW TO MIX DRINKS RECIPE ADDED: "
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

        for existing in recipe["tastings"]:
            if existing.get("guest") == guest:
                raise ValueError(
                    "Guest already tasted this cocktail."
                )

        tasting = {
            "guest": guest,
            "liked": bool(
                liked
            ),
            "comment": comment
        }

        recipe[
            "tastings"
        ].append(
            tasting
        )

        if tasting["liked"]:
            recipe[
                "votes_for"
            ] += 1
        else:
            recipe[
                "votes_against"
            ] += 1

        if len(recipe["tastings"]) == 5:
            if recipe["votes_for"] >= 4:
                recipe["approved"] = True
                recipe["status"] = "approved"
            else:
                recipe["approved"] = False
                recipe["status"] = "rejected"

        UniverseLogger.event(
            "HOW TO MIX DRINKS TASTING RECORDED: "
            f"{drink} BY {guest}"
        )

        return tasting





