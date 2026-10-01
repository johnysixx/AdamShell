from dataclasses import dataclass, field

from cats.genotype import CatGenotype


@dataclass(slots=True, frozen=True)
class KittenInvalidGenotypeDetails:

    error: str

    def __post_init__(self):
        object.__setattr__(
            self,
            "error",
            str(self.error),
        )

        if not self.error:
            raise ValueError(
                "Invalid genotype details require "
                "an error message."
            )


@dataclass(slots=True, frozen=True)
class KittenLethalMutationDetails:

    lethal_mutations: tuple[str, ...]

    def __post_init__(self):
        mutations = tuple(
            str(mutation)
            for mutation
            in self.lethal_mutations
        )

        if not mutations:
            raise ValueError(
                "Lethal mutation details require "
                "at least one mutation."
            )

        object.__setattr__(
            self,
            "lethal_mutations",
            mutations,
        )


@dataclass(slots=True, frozen=True)
class KittenXXYGenotypeDetails:

    sex_chromosomes: tuple[str, ...]

    def __post_init__(self):
        chromosomes = tuple(
            str(chromosome)
            for chromosome
            in self.sex_chromosomes
        )

        if chromosomes != (
            "X",
            "X",
            "Y",
        ):
            raise ValueError(
                "XXY genotype details require "
                "XXY sex chromosomes."
            )

        object.__setattr__(
            self,
            "sex_chromosomes",
            chromosomes,
        )


@dataclass(slots=True, frozen=True)
class KittenGeneticViabilityResult:

    status: str
    viable: bool
    rare: bool
    reason: str | None

    details: (
        KittenInvalidGenotypeDetails
        | KittenLethalMutationDetails
        | KittenXXYGenotypeDetails
        | None
    )

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
            "special_traits",
            tuple(
                str(trait)
                for trait
                in self.special_traits
            ),
        )

        details_type_by_reason = {
            "invalid_genotype": (
                KittenInvalidGenotypeDetails
            ),
            "lethal_genetic_combination": (
                KittenLethalMutationDetails
            ),
            "xxy_male": (
                KittenXXYGenotypeDetails
            ),
        }

        if self.reason is None:
            if self.details is not None:
                raise TypeError(
                    "Standard viability result "
                    "cannot contain details."
                )

        elif self.reason in details_type_by_reason:
            expected_type = (
                details_type_by_reason[
                    self.reason
                ]
            )

            if not isinstance(
                self.details,
                expected_type,
            ):
                raise TypeError(
                    "Viability details do not match "
                    f"reason {self.reason!r}."
                )

        else:
            raise ValueError(
                "Unsupported kitten viability reason."
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
        if self.details is None:
            details = None

        elif isinstance(
            self.details,
            KittenInvalidGenotypeDetails,
        ):
            details = self.details.error

        elif isinstance(
            self.details,
            KittenLethalMutationDetails,
        ):
            details = {
                "lethal_mutations": list(
                    self.details.lethal_mutations
                )
            }

        elif isinstance(
            self.details,
            KittenXXYGenotypeDetails,
        ):
            details = {
                "sex_chromosomes": tuple(
                    self.details.sex_chromosomes
                )
            }

        else:
            raise TypeError(
                "Unsupported kitten viability details."
            )

        return {
            "name": self.name,
            "status": self.status,
            "viable": self.viable,
            "rare": self.rare,
            "reason": self.reason,
            "details": details,
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
                details=(
                    KittenInvalidGenotypeDetails(
                        error=str(error),
                    )
                ),
                special_traits=(),
                genotype=genotype,
            )

        lethal_mutations = tuple(
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
                details=(
                    KittenLethalMutationDetails(
                        lethal_mutations=(
                            lethal_mutations
                        ),
                    )
                ),
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
                details=(
                    KittenXXYGenotypeDetails(
                        sex_chromosomes=(
                            chromosomes
                        ),
                    )
                ),
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
