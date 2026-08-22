from universe.logger import UniverseLogger


class HowToMixDrinks:

    def __init__(self):
        self.name = "how_to_mix_drinks"
        self.type = "bartender_recipe_book"
        self.recipes = {}

        UniverseLogger.boot(
            "HOW TO MIX DRINKS CREATED"
        )

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



