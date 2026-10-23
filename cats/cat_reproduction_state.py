from cats.cat_development_stage import CatDevelopmentStage
from dataclasses import dataclass, field

from cats.cat_birth_objects import (
    CatBirthProfile,
    CatLitter,
    KittenEmbryo,
)
from cats.cat_estrous_phase import CatEstrousPhase

from cats.mating_contact import CatMatingContact




@dataclass(slots=True)
class CatReproductionState:

    sex: str
    neutered: bool = False
    fertile: bool = field(init=False)

    developmental_stage: CatDevelopmentStage | None = None
    reproductive_maturity: bool = False

    estrous_phase: CatEstrousPhase = CatEstrousPhase.INACTIVE
    estrus_active: bool = False
    estrous_cycle_day: int = 0
    estrus_duration_days: int = 7
    interestrus_duration_days: int = 8
    estrous_cycles_completed: int = 0

    mating_window_open: bool = False
    mating_window_started_day: int | None = None
    mating_contacts: list[CatMatingContact] = field(default_factory=list)
    potential_fathers: list[str] = field(default_factory=list)

    ovulation_stimulation: int = 0
    ovulation_threshold: int = 4
    ovulation_induced: bool = False
    last_ovulation_day: int | None = None

    pregnant: bool = False
    pregnancy_day: int | None = None
    gestation_days: int | None = None
    expected_birth_day: int | None = None

    mother_name: str | None = None

    embryos: list[KittenEmbryo] = field(default_factory=list)
    litters: list[CatLitter] = field(default_factory=list)
    last_litter: CatLitter | None = None
    litters_born: int = 0

    def __post_init__(self):
        if self.sex not in {"female", "male"}:
            raise ValueError(
                "Cat reproductive sex must be female or male."
            )

        self.neutered = bool(self.neutered)
        self.fertile = not self.neutered

    def to_dict(self):

        def profile_snapshot(
            profile,
        ):
            if not isinstance(
                profile,
                CatBirthProfile,
            ):
                raise TypeError(
                    "Reproduction birth profile "
                    "boundary requires "
                    "CatBirthProfile."
                )

            return {
                "color": profile.color,
                "fur_length": (
                    profile.fur_length
                ),
                "pattern": profile.pattern,
                "eye_color": (
                    profile.eye_color
                ),
                "sex": profile.sex,
            }

        def contact_snapshot(
            contact,
        ):
            if not isinstance(
                contact,
                CatMatingContact,
            ):
                raise TypeError(
                    "Reproduction mating contact "
                    "boundary requires "
                    "CatMatingContact."
                )

            return {
                "name": contact.name,
                "contact_number": (
                    contact.contact_number
                ),
                "female": contact.female,
                "male": contact.male,
                "male_name": (
                    contact.male_name
                ),
                "successful": (
                    contact.successful
                ),
                "day": contact.day,
                "_male_ref": (
                    contact.male_ref
                ),
            }

        def viability_snapshot(
            viability,
        ):
            details = (
                viability.details
            )

            if details is None:
                boundary_details = None

            elif hasattr(
                details,
                "error",
            ):
                boundary_details = (
                    details.error
                )

            elif hasattr(
                details,
                "lethal_mutations",
            ):
                boundary_details = {
                    "lethal_mutations": list(
                        details.lethal_mutations
                    ),
                }

            elif hasattr(
                details,
                "sex_chromosomes",
            ):
                boundary_details = {
                    "sex_chromosomes": tuple(
                        details.sex_chromosomes
                    ),
                }

            else:
                raise TypeError(
                    "Unsupported kitten "
                    "viability details."
                )

            return {
                "name": viability.name,
                "status": viability.status,
                "viable": viability.viable,
                "rare": viability.rare,
                "reason": viability.reason,
                "details": boundary_details,
                "special_traits": list(
                    viability.special_traits
                ),
                "genotype": (
                    viability.genotype
                ),
            }

        def phenotype_snapshot(
            phenotype,
        ):
            return {
                "name": phenotype.name,
                "profile": (
                    profile_snapshot(
                        phenotype.profile
                    )
                ),
                "base_color": (
                    phenotype.base_color
                ),
                "diluted": (
                    phenotype.diluted
                ),
                "white_spotted": (
                    phenotype.white_spotted
                ),
                "colorpoint": (
                    phenotype.colorpoint
                ),
                "genotype": (
                    phenotype.genotype
                ),
                "resolved": (
                    phenotype.resolved
                ),
            }

        def embryo_snapshot(
            embryo,
        ):
            if not isinstance(
                embryo,
                KittenEmbryo,
            ):
                raise TypeError(
                    "Reproduction embryo boundary "
                    "requires KittenEmbryo."
                )

            return {
                "id": embryo.id,
                "type": embryo.type,
                "state": embryo.state,
                "mother_name": (
                    embryo.mother_name
                ),
                "father_name": (
                    embryo.father_name
                ),
                "genotype": (
                    embryo.genotype
                ),
                "phenotype": (
                    phenotype_snapshot(
                        embryo.phenotype
                    )
                ),
                "profile": (
                    profile_snapshot(
                        embryo.profile
                    )
                ),
                "viability": (
                    viability_snapshot(
                        embryo.viability
                    )
                ),
                "genetic_status": (
                    embryo.genetic_status
                ),
                "rare": embryo.rare,
                "special_traits": list(
                    embryo.special_traits
                ),
            }

        def birth_result_snapshot(
            result,
        ):
            if not result.born:
                return {
                    "embryo_id": (
                        result.embryo_id
                    ),
                    "kitten": None,
                    "born": False,
                    "reason": (
                        result.reason
                    ),
                }

            return {
                "embryo_id": (
                    result.embryo_id
                ),
                "kitten": result.kitten,
                "father": result.father,
                "genetic_status": (
                    result.genetic_status
                ),
                "rare": result.rare,
                "born": True,
            }

        def litter_snapshot(
            litter,
        ):
            if not isinstance(
                litter,
                CatLitter,
            ):
                raise TypeError(
                    "Reproduction litter boundary "
                    "requires CatLitter."
                )

            return {
                "name": litter.name,
                "litter_number": (
                    litter.litter_number
                ),
                "mother": litter.mother,
                "father_names": list(
                    litter.father_names
                ),
                "multiple_sires": (
                    litter.multiple_sires
                ),
                "embryos_present": (
                    litter.embryos_present
                ),
                "kittens_born": (
                    litter.kittens_born
                ),
                "kitten_names": list(
                    litter.kitten_names
                ),
                "birth_results": [
                    birth_result_snapshot(
                        result
                    )
                    for result
                    in litter.birth_results
                ],
                "pregnancy_day": (
                    litter.pregnancy_day
                ),
                "gestation_days": (
                    litter.gestation_days
                ),
                "birth_day": (
                    litter.birth_day
                ),
                "born": litter.born,
            }

        return {
            "sex": self.sex,
            "neutered": self.neutered,
            "fertile": self.fertile,

            "developmental_stage": (
                self.developmental_stage.value
                if (
                    self.developmental_stage
                    is not None
                )
                else None
            ),

            "reproductive_maturity": (
                self.reproductive_maturity
            ),

            "estrous_phase": (
                self.estrous_phase.value
            ),

            "estrus_active":
                self.estrus_active,

            "estrous_cycle_day":
                self.estrous_cycle_day,

            "estrus_duration_days":
                self.estrus_duration_days,

            "interestrus_duration_days":
                self.interestrus_duration_days,

            "estrous_cycles_completed":
                self.estrous_cycles_completed,

            "mating_window_open":
                self.mating_window_open,

            "mating_window_started_day": (
                self.mating_window_started_day
            ),

            "mating_contacts": [
                contact_snapshot(
                    contact
                )
                for contact
                in self.mating_contacts
            ],

            "potential_fathers": list(
                self.potential_fathers
            ),

            "ovulation_stimulation":
                self.ovulation_stimulation,

            "ovulation_threshold":
                self.ovulation_threshold,

            "ovulation_induced":
                self.ovulation_induced,

            "last_ovulation_day":
                self.last_ovulation_day,

            "pregnant": self.pregnant,

            "pregnancy_day":
                self.pregnancy_day,

            "gestation_days":
                self.gestation_days,

            "expected_birth_day":
                self.expected_birth_day,

            "mother_name":
                self.mother_name,

            "embryos": [
                embryo_snapshot(
                    embryo
                )
                for embryo
                in self.embryos
            ],

            "litters": [
                litter_snapshot(
                    litter
                )
                for litter
                in self.litters
            ],

            "last_litter": (
                litter_snapshot(
                    self.last_litter
                )
                if (
                    self.last_litter
                    is not None
                )
                else None
            ),

            "litters_born":
                self.litters_born,
        }
