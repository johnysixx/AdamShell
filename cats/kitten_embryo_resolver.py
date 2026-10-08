from dataclasses import dataclass, field

from cats.genotype import CatGenotype
from cats.phenotype_resolver import CatPhenotypeResolver
from cats.kitten_viability_resolver import (
    KittenGeneticViabilityResolver,
    KittenGeneticViabilityResult,
)
from cats.cat_birth_objects import (
    CatBirthProfile,
    CatPhenotypeResult,
    KittenEmbryo,
    cat_phenotype_snapshot,
    kitten_genetic_viability_snapshot,
)


@dataclass(slots=True, frozen=True)
class NonviableKittenEmbryoReplacedByCronenbergEvent:

    embryo_id: str
    mother: str
    father: str
    genotype: CatGenotype
    viability: (
        KittenGeneticViabilityResult
    )
    cronenberg_id: str
    name: str = field(
        default=(
            "nonviable_kitten_embryo_"
            "replaced_by_cronenberg"
        ),
        init=False,
    )
    kitten_created: bool = field(
        default=False,
        init=False,
    )
    cronenberg_created: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.genotype,
            CatGenotype,
        ):
            raise TypeError(
                "Nonviable embryo event "
                "requires a CatGenotype object."
            )

        if not isinstance(
            self.viability,
            KittenGeneticViabilityResult,
        ):
            raise TypeError(
                "Nonviable embryo event "
                "requires a viability object."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "embryo_id": self.embryo_id,
            "mother": self.mother,
            "father": self.father,
            "genotype": self.genotype,
            "viability": (
                kitten_genetic_viability_snapshot(
                    self.viability
                )
            ),
            "kitten_created": (
                self.kitten_created
            ),
            "cronenberg_created": (
                self.cronenberg_created
            ),
            "cronenberg_id": (
                self.cronenberg_id
            ),
        }


@dataclass(slots=True, frozen=True)
class KittenEmbryoCreatedEvent:

    embryo_id: str
    mother: str
    father: str
    genetic_status: str
    rare: bool
    profile: CatBirthProfile
    name: str = field(
        default="kitten_embryo_created",
        init=False,
    )
    kitten_created: bool = field(
        default=False,
        init=False,
    )
    cronenberg_created: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.profile,
            CatBirthProfile,
        ):
            raise TypeError(
                "Embryo event profile requires "
                "a CatBirthProfile object."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "embryo_id": self.embryo_id,
            "mother": self.mother,
            "father": self.father,
            "genetic_status": (
                self.genetic_status
            ),
            "rare": self.rare,
            "profile": (
                self.profile.to_dict()
            ),
            "kitten_created": (
                self.kitten_created
            ),
            "cronenberg_created": (
                self.cronenberg_created
            ),
        }


@dataclass(slots=True, frozen=True)
class KittenEmbryoResult:

    embryo: KittenEmbryo | None
    viability: KittenGeneticViabilityResult

    phenotype: (
        CatPhenotypeResult
        | None
    )

    cronenberg: object | None

    event: (
        KittenEmbryoCreatedEvent
        | NonviableKittenEmbryoReplacedByCronenbergEvent
    )

    def __post_init__(self):
        if not isinstance(
            self.viability,
            KittenGeneticViabilityResult,
        ):
            raise TypeError(
                "Kitten embryo result requires "
                "a viability result object."
            )

        if self.viable:
            if not isinstance(
                self.event,
                KittenEmbryoCreatedEvent,
            ):
                raise TypeError(
                    "Viable kitten embryo result "
                    "requires a created event."
                )

            if not isinstance(
                self.embryo,
                KittenEmbryo,
            ):
                raise TypeError(
                    "Viable kitten embryo result "
                    "requires a KittenEmbryo."
                )

            if not isinstance(
                self.phenotype,
                CatPhenotypeResult,
            ):
                raise TypeError(
                    "Viable kitten embryo result "
                    "requires a phenotype result."
                )

            if self.cronenberg is not None:
                raise ValueError(
                    "Viable kitten embryo result "
                    "cannot contain a Cronenberg."
                )

            if (
                self.embryo.viability
                is not self.viability
            ):
                raise ValueError(
                    "Kitten embryo result must "
                    "reuse embryo viability."
                )

            if (
                self.embryo.phenotype
                is not self.phenotype
            ):
                raise ValueError(
                    "Kitten embryo result must "
                    "reuse embryo phenotype."
                )

            if (
                self.embryo.profile
                is not self.event.profile
            ):
                raise ValueError(
                    "Kitten embryo result must "
                    "reuse event profile."
                )

        else:
            if not isinstance(
                self.event,
                NonviableKittenEmbryoReplacedByCronenbergEvent,
            ):
                raise TypeError(
                    "Nonviable kitten embryo result "
                    "requires replacement event."
                )

            if self.embryo is not None:
                raise ValueError(
                    "Nonviable kitten embryo result "
                    "cannot contain an embryo."
                )

            if self.phenotype is not None:
                raise ValueError(
                    "Nonviable kitten embryo result "
                    "cannot contain a phenotype."
                )

            if self.cronenberg is None:
                raise ValueError(
                    "Nonviable kitten embryo result "
                    "requires a Cronenberg."
                )

            if (
                self.event.viability
                is not self.viability
            ):
                raise ValueError(
                    "Nonviable kitten embryo result "
                    "must reuse event viability."
                )

    @property
    def viable(self):
        return self.viability.viable

    @property
    def embryo_id(self):
        return self.event.embryo_id

    def to_dict(self):
        result = {
            "embryo": self.embryo,
            "viability": (
                kitten_genetic_viability_snapshot(
                    self.viability
                )
            ),
        }

        if self.phenotype is not None:
            result[
                "phenotype"
            ] = (
                cat_phenotype_snapshot(
                    self.phenotype
                )
            )

        result.update(
            {
                "cronenberg": (
                    self.cronenberg
                ),
                "event": (
                    self.event.to_dict()
                ),
                "viable": self.viable,
            }
        )

        return result


class KittenEmbryoResolver:

    def __init__(self, universe):
        self.universe = universe
        self.history = []
        self.embryo_count = 0

    def create_embryo(self, mother, father, rng, genotype_override=None):
        self._validate_parents(mother, father)
        self.embryo_count += 1
        embryo_id = f'embryo_{self.embryo_count:04d}'
        genotype = genotype_override if genotype_override is not None else CatGenotype.inherit(mother_genotype=mother.genotype, father_genotype=father.genotype, rng=rng)
        viability = KittenGeneticViabilityResolver.resolve(genotype)
        if not viability.viable:
            cronenberg = self.universe.create_cronenberg_from_quantum_error(error=RuntimeError(f'Nonviable kitten genotype replaced embryo {embryo_id}.'), source_component='kitten_embryo_resolver', source_operation='nonviable_embryo')
            event = (
                NonviableKittenEmbryoReplacedByCronenbergEvent(
                    embryo_id=embryo_id,
                    mother=mother.name,
                    father=father.name,
                    genotype=genotype,
                    viability=viability,
                    cronenberg_id=cronenberg.id,
                )
            )

            self.record_event(
                event
            )

            self.universe.quantum_events.append(
                event.to_dict()
            )

            return KittenEmbryoResult(
                embryo=None,
                viability=viability,
                phenotype=None,
                cronenberg=cronenberg,
                event=event,
            )
        phenotype = CatPhenotypeResolver.resolve(
            genotype
        )

        profile = phenotype.profile

        embryo = KittenEmbryo(
            id=embryo_id,
            mother_name=mother.name,
            father_name=father.name,
            genotype=genotype,
            phenotype=phenotype,
            profile=profile,
            viability=(
                viability
            ),
            genetic_status=(
                viability.status
            ),
            rare=(
                viability.rare
            ),
            special_traits=(
                viability
                .special_traits
            ),
        )

        event = KittenEmbryoCreatedEvent(
            embryo_id=embryo_id,
            mother=mother.name,
            father=father.name,
            genetic_status=(
                viability.status
            ),
            rare=(
                viability.rare
            ),
            profile=profile,
        )

        self.record_event(
            event
        )

        return KittenEmbryoResult(
            embryo=embryo,
            viability=viability,
            phenotype=phenotype,
            cronenberg=None,
            event=event,
        )

    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            (
                NonviableKittenEmbryoReplacedByCronenbergEvent,
                KittenEmbryoCreatedEvent,
            ),
        ):
            raise TypeError(
                "Kitten embryo history requires "
                "a kitten embryo event object."
            )

        self.history.append(
            event
        )

        return event

    @staticmethod
    def _validate_parents(mother, father):
        if getattr(mother, 'sex', None) != 'female':
            raise ValueError('Embryo mother must be female.')
        if getattr(father, 'sex', None) != 'male':
            raise ValueError('Embryo father must be male.')
        if not hasattr(mother, 'genotype'):
            raise ValueError('Mother has no genotype.')
        if not hasattr(father, 'genotype'):
            raise ValueError('Father has no genotype.')
