from dataclasses import dataclass
from itertools import permutations
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class CatTraitDiceMappingResult:
    cat_d20_value: int
    permutation_index: int
    die_to_trait: Mapping[str, str]
    trait_to_die: Mapping[str, str]

    def __post_init__(self):
        if not isinstance(self.die_to_trait, dict):
            raise TypeError(
                "die_to_trait must be a dict registry."
            )

        if not isinstance(self.trait_to_die, dict):
            raise TypeError(
                "trait_to_die must be a dict registry."
            )

        object.__setattr__(
            self,
            "die_to_trait",
            MappingProxyType(dict(self.die_to_trait)),
        )
        object.__setattr__(
            self,
            "trait_to_die",
            MappingProxyType(dict(self.trait_to_die)),
        )

    @property
    def name(self):
        return "cat_trait_dice_mapping_resolved"

    @property
    def resolved(self):
        return True

    def trait_for_die(self, die_name):
        return self.die_to_trait.get(die_name)

    def die_for_trait(self, trait):
        return self.trait_to_die.get(trait)

    def to_dict(self):
        return {
            "name": self.name,
            "cat_d20_value": self.cat_d20_value,
            "permutation_index": self.permutation_index,
            "die_to_trait": dict(self.die_to_trait),
            "trait_to_die": dict(self.trait_to_die),
            "resolved": self.resolved,
        }


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

        return CatTraitDiceMappingResult(
            cat_d20_value=value,
            permutation_index=permutation_index,
            die_to_trait=die_to_trait,
            trait_to_die=trait_to_die,
        )
