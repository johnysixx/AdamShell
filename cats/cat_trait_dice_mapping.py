from dataclasses import dataclass
from itertools import permutations


@dataclass(frozen=True, slots=True)
class CatTraitDieAssignment:
    die: str
    trait: str

    def __post_init__(self):
        if not isinstance(self.die, str) or not self.die:
            raise TypeError(
                "Trait assignment requires a die name."
            )

        if not isinstance(self.trait, str) or not self.trait:
            raise TypeError(
                "Trait assignment requires a trait name."
            )


@dataclass(frozen=True, slots=True)
class CatTraitDiceMappingResult:
    cat_d20_value: int
    permutation_index: int
    assignments: tuple[CatTraitDieAssignment, ...] = ()

    def __post_init__(self):
        if (
            not isinstance(self.assignments, tuple)
            or any(
                not isinstance(
                    assignment,
                    CatTraitDieAssignment,
                )
                for assignment in self.assignments
            )
        ):
            raise TypeError(
                "Trait dice mapping requires "
                "typed immutable assignments."
            )

        dice = tuple(
            assignment.die
            for assignment in self.assignments
        )

        traits = tuple(
            assignment.trait
            for assignment in self.assignments
        )

        if len(dice) != len(set(dice)):
            raise ValueError(
                "Trait dice mapping contains duplicate dice."
            )

        if len(traits) != len(set(traits)):
            raise ValueError(
                "Trait dice mapping contains duplicate traits."
            )

    @property
    def name(self):
        return "cat_trait_dice_mapping_resolved"

    @property
    def resolved(self):
        return True

    def trait_for_die(self, die_name):
        for assignment in self.assignments:
            if assignment.die == die_name:
                return assignment.trait

        return None

    def die_for_trait(self, trait):
        for assignment in self.assignments:
            if assignment.trait == trait:
                return assignment.die

        return None


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

        assignments = tuple(
            CatTraitDieAssignment(
                die=die_name,
                trait=trait,
            )
            for die_name, trait
            in zip(
                self.DICE,
                selected_traits,
            )
        )

        return CatTraitDiceMappingResult(
            cat_d20_value=value,
            permutation_index=permutation_index,
            assignments=assignments,
        )
