from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType

from cats.genotype import CatGenotype


class _FrozenViabilityList(tuple):
    pass


class _FrozenViabilitySet(frozenset):
    pass


def _freeze_viability_payload(value):
    if isinstance(value, dict):
        return MappingProxyType({
            key: _freeze_viability_payload(item)
            for key, item in value.items()
        })

    if isinstance(value, list):
        return _FrozenViabilityList(
            _freeze_viability_payload(item)
            for item in value
        )

    if isinstance(value, tuple):
        return tuple(
            _freeze_viability_payload(item)
            for item in value
        )

    if isinstance(value, set):
        return _FrozenViabilitySet(
            _freeze_viability_payload(item)
            for item in value
        )

    if isinstance(value, frozenset):
        return frozenset(
            _freeze_viability_payload(item)
            for item in value
        )

    return deepcopy(value)


def _thaw_viability_payload(value):
    if isinstance(
        value,
        MappingProxyType,
    ):
        return {
            key: _thaw_viability_payload(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        _FrozenViabilityList,
    ):
        return [
            _thaw_viability_payload(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return tuple(
            _thaw_viability_payload(item)
            for item in value
        )

    if isinstance(
        value,
        _FrozenViabilitySet,
    ):
        return {
            _thaw_viability_payload(item)
            for item in value
        }

    if isinstance(value, frozenset):
        return frozenset(
            _thaw_viability_payload(item)
            for item in value
        )

    return deepcopy(value)


@dataclass(slots=True, frozen=True)
class KittenGeneticViabilityResult:

    status: str
    viable: bool
    rare: bool
    reason: str | None
    details: object
    special_traits: tuple[str, ...]
    genotype: object

    name: str = field(
        default=(
            "kitten_genetic_viability_resolved"
        ),
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "status",
            str(self.status),
        )

        object.__setattr__(
            self,
            "viable",
            bool(self.viable),
        )

        object.__setattr__(
            self,
            "rare",
            bool(self.rare),
        )

        if self.reason is not None:
            object.__setattr__(
                self,
                "reason",
                str(self.reason),
            )

        object.__setattr__(
            self,
            "details",
            _freeze_viability_payload(
                self.details
            ),
        )

        object.__setattr__(
            self,
            "special_traits",
            tuple(
                str(trait)
                for trait
                in self.special_traits
            ),
        )

        if (
            self.reason != "invalid_genotype"
            and not isinstance(
                self.genotype,
                CatGenotype,
            )
        ):
            raise TypeError(
                "Viability result requires "
                "a CatGenotype object."
            )

        if (
            self.viable
            and not isinstance(
                self.genotype,
                CatGenotype,
            )
        ):
            raise TypeError(
                "Viable result requires "
                "a CatGenotype object."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "viable": self.viable,
            "rare": self.rare,
            "reason": self.reason,
            "details": (
                _thaw_viability_payload(
                    self.details
                )
            ),
            "special_traits": list(
                self.special_traits
            ),
            "genotype": self.genotype,
        }


class KittenGeneticViabilityResolver:

    @classmethod
    def resolve(
        cls,
        genotype
    ):
        try:
            CatGenotype.validate(
                genotype
            )

        except (
            ValueError,
            TypeError,
            KeyError
        ) as error:
            return KittenGeneticViabilityResult(
                status="nonviable",
                viable=False,
                rare=False,
                reason="invalid_genotype",
                details=str(error),
                special_traits=(),
                genotype=genotype,
            )

        lethal_mutations = list(
            genotype.lethal_mutations
        )

        if lethal_mutations:
            return KittenGeneticViabilityResult(
                status="nonviable",
                viable=False,
                rare=False,
                reason=(
                    "lethal_genetic_combination"
                ),
                details={
                    "lethal_mutations": (
                        lethal_mutations
                    )
                },
                special_traits=(),
                genotype=genotype,
            )

        chromosomes = tuple(
            genotype.sex_chromosomes
        )

        if (
            genotype.sex == "male"
            and chromosomes
            == (
                "X",
                "X",
                "Y"
            )
        ):
            traits = [
                "rare_valid_genotype",
                "xxy_male"
            ]

            orange = tuple(
                genotype.orange_locus
            )

            if set(orange) == {
                "O",
                "o"
            }:
                traits.append(
                    "xxy_tortoiseshell_capable"
                )

            return KittenGeneticViabilityResult(
                status="rare_valid",
                viable=True,
                rare=True,
                reason="xxy_male",
                details={
                    "sex_chromosomes": (
                        chromosomes
                    )
                },
                special_traits=tuple(
                    traits
                ),
                genotype=genotype,
            )

        return KittenGeneticViabilityResult(
            status="standard",
            viable=True,
            rare=False,
            reason=None,
            details=None,
            special_traits=(),
            genotype=genotype,
        )
