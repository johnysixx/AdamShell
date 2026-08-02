from itertools import permutations


class CatTraitDiceMapping:

    DICE = (
        "d4",
        "d6",
        "d8",
        "d10",
        "d12"
    )

    TRAITS = (
        "color",
        "fur_length",
        "pattern",
        "eye_color",
        "sex"
    )

    def __init__(self):
        self._permutations = list(
            permutations(
                self.TRAITS
            )
        )

    def resolve(
        self,
        cat_d20_value
    ):
        value = int(
            cat_d20_value
        )

        if value < 1 or value > 20:
            raise ValueError(
                "CatD20 value must be between 1 and 20."
            )

        permutation_index = (
            (value - 1) * 37
        ) % len(
            self._permutations
        )

        selected_traits = (
            self._permutations[
                permutation_index
            ]
        )

        die_to_trait = dict(
            zip(
                self.DICE,
                selected_traits
            )
        )

        trait_to_die = {
            trait: die
            for die, trait
            in die_to_trait.items()
        }

        return {
            "name": "cat_trait_dice_mapping_resolved",
            "cat_d20_value": value,
            "permutation_index": (
                permutation_index
            ),
            "die_to_trait": die_to_trait,
            "trait_to_die": trait_to_die,
            "resolved": True
        }