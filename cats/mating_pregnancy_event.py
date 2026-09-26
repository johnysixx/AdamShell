from dataclasses import dataclass, field

from cats.cat_birth_objects import (
    CatBirthProfile,
)

from cats.kitten_embryo_resolver import (
    KittenEmbryoCreatedEvent,
    KittenGeneticViabilitySnapshot,
    NonviableKittenEmbryoReplacedByCronenbergEvent,
)

from cats.mating_contact import (
    CatMatingHistoryEvent,
)

from cats.ovulation_resolver import (
    CatInducedOvulationResolvedEvent,
)

from cats.paternity_resolver import (
    KittenFatherSelectedEvent,
)


@dataclass(slots=True, frozen=True)
class CatPregnancyPhenotypeSnapshot:

    profile: CatBirthProfile
    base_color: str
    diluted: bool
    white_spotted: bool
    colorpoint: bool
    genotype: object

    name: str = field(
        default="cat_phenotype_resolved",
        init=False,
    )

    resolved: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.profile,
            CatBirthProfile,
        ):
            raise TypeError(
                "Pregnancy phenotype "
                "requires a CatBirthProfile."
            )

        object.__setattr__(
            self,
            "base_color",
            str(
                self.base_color
            ),
        )

        object.__setattr__(
            self,
            "diluted",
            bool(
                self.diluted
            ),
        )

        object.__setattr__(
            self,
            "white_spotted",
            bool(
                self.white_spotted
            ),
        )

        object.__setattr__(
            self,
            "colorpoint",
            bool(
                self.colorpoint
            ),
        )

    @classmethod
    def from_boundary(
        cls,
        payload,
        profile
    ):
        return cls(
            profile=profile,
            base_color=payload[
                "base_color"
            ],
            diluted=payload[
                "diluted"
            ],
            white_spotted=payload[
                "white_spotted"
            ],
            colorpoint=payload[
                "colorpoint"
            ],
            genotype=payload[
                "genotype"
            ],
        )

    def __deepcopy__(
        self,
        memo
    ):
        return self

    def to_dict(self):
        return {
            "name": self.name,
            "profile": (
                self.profile.to_dict()
            ),
            "base_color": (
                self.base_color
            ),
            "diluted": self.diluted,
            "white_spotted": (
                self.white_spotted
            ),
            "colorpoint": (
                self.colorpoint
            ),
            "genotype": self.genotype,
            "resolved": self.resolved,
        }


@dataclass(slots=True, frozen=True)
class CatPregnancyPaternityResult:

    embryo_id: str
    selection: KittenFatherSelectedEvent

    def __post_init__(self):
        if not isinstance(
            self.selection,
            KittenFatherSelectedEvent,
        ):
            raise TypeError(
                "Pregnancy paternity result "
                "requires a "
                "KittenFatherSelectedEvent."
            )

        object.__setattr__(
            self,
            "embryo_id",
            str(
                self.embryo_id
            ),
        )

    @property
    def father(self):
        return self.selection.father

    def __deepcopy__(
        self,
        memo
    ):
        return self

    def to_dict(self):
        return {
            "embryo_id": (
                self.embryo_id
            ),
            "father": self.father,
            "selection": (
                self.selection.to_dict()
            ),
        }


@dataclass(slots=True, frozen=True)
class CatPregnancyEmbryoResult:

    embryo: object | None

    viability: (
        KittenGeneticViabilitySnapshot
    )

    phenotype: (
        CatPregnancyPhenotypeSnapshot
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
            KittenGeneticViabilitySnapshot,
        ):
            raise TypeError(
                "Pregnancy embryo result "
                "requires a typed viability "
                "snapshot."
            )

        if not isinstance(
            self.event,
            (
                KittenEmbryoCreatedEvent,
                NonviableKittenEmbryoReplacedByCronenbergEvent,
            ),
        ):
            raise TypeError(
                "Pregnancy embryo result "
                "requires a typed embryo event."
            )

        if self.viable:
            if self.embryo is None:
                raise ValueError(
                    "Viable pregnancy embryo "
                    "requires an embryo object."
                )

            if not isinstance(
                self.phenotype,
                CatPregnancyPhenotypeSnapshot,
            ):
                raise TypeError(
                    "Viable pregnancy embryo "
                    "requires a typed phenotype."
                )

            if self.cronenberg is not None:
                raise ValueError(
                    "Viable pregnancy embryo "
                    "cannot contain a Cronenberg."
                )

        else:
            if self.embryo is not None:
                raise ValueError(
                    "Nonviable pregnancy embryo "
                    "cannot contain an embryo."
                )

            if self.phenotype is not None:
                raise ValueError(
                    "Nonviable pregnancy embryo "
                    "cannot contain a phenotype."
                )

            if self.cronenberg is None:
                raise ValueError(
                    "Nonviable pregnancy embryo "
                    "requires a Cronenberg."
                )

    @property
    def viable(self):
        return isinstance(
            self.event,
            KittenEmbryoCreatedEvent,
        )

    @property
    def embryo_id(self):
        return self.event.embryo_id

    @classmethod
    def from_boundary(
        cls,
        payload,
        event
    ):
        if isinstance(
            event,
            KittenEmbryoCreatedEvent,
        ):
            if not payload[
                "viable"
            ]:
                raise ValueError(
                    "Viable embryo event has "
                    "nonviable boundary state."
                )

            viability = (
                KittenGeneticViabilitySnapshot
                .from_boundary(
                    payload[
                        "viability"
                    ]
                )
            )

            phenotype = (
                CatPregnancyPhenotypeSnapshot
                .from_boundary(
                    payload[
                        "phenotype"
                    ],
                    profile=(
                        event.profile
                    ),
                )
            )

        elif isinstance(
            event,
            NonviableKittenEmbryoReplacedByCronenbergEvent,
        ):
            if payload[
                "viable"
            ]:
                raise ValueError(
                    "Nonviable embryo event has "
                    "viable boundary state."
                )

            viability = (
                event.viability
            )

            phenotype = None

        else:
            raise TypeError(
                "Unsupported embryo event."
            )

        return cls(
            embryo=payload[
                "embryo"
            ],
            viability=viability,
            phenotype=phenotype,
            cronenberg=payload[
                "cronenberg"
            ],
            event=event,
        )

    def __deepcopy__(
        self,
        memo
    ):
        return self

    def to_dict(self):
        result = {
            "embryo": self.embryo,
            "viability": (
                self.viability.to_dict()
            ),
        }

        if self.phenotype is not None:
            result[
                "phenotype"
            ] = (
                self.phenotype.to_dict()
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


@dataclass(slots=True, frozen=True)
class CatPregnancyStartedEvent(
    CatMatingHistoryEvent
):

    mother: str

    ovulation: (
        CatInducedOvulationResolvedEvent
    )

    mating_contact_count: int

    paternity_results: tuple[
        CatPregnancyPaternityResult,
        ...,
    ]

    gestation_days: int
    started_on_day: int

    embryo_results: tuple[
        CatPregnancyEmbryoResult,
        ...,
    ]

    name: str = field(
        default="cat_pregnancy_started",
        init=False,
    )

    ovulation_induced: bool = field(
        default=True,
        init=False,
    )

    pregnancy_day: int = field(
        default=0,
        init=False,
    )

    started: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.ovulation,
            CatInducedOvulationResolvedEvent,
        ):
            raise TypeError(
                "Pregnancy start requires "
                "a typed ovulation event."
            )

        if not (
            self.ovulation
            .ovulation_induced
        ):
            raise ValueError(
                "Pregnancy cannot start "
                "without induced ovulation."
            )

        if not all(
            isinstance(
                result,
                CatPregnancyPaternityResult,
            )
            for result
            in self.paternity_results
        ):
            raise TypeError(
                "Pregnancy paternity results "
                "must be typed objects."
            )

        if not all(
            isinstance(
                result,
                CatPregnancyEmbryoResult,
            )
            for result
            in self.embryo_results
        ):
            raise TypeError(
                "Pregnancy embryo results "
                "must be typed objects."
            )

        object.__setattr__(
            self,
            "mother",
            str(
                self.mother
            ),
        )

        object.__setattr__(
            self,
            "mating_contact_count",
            int(
                self.mating_contact_count
            ),
        )

        object.__setattr__(
            self,
            "paternity_results",
            tuple(
                self.paternity_results
            ),
        )

        object.__setattr__(
            self,
            "gestation_days",
            int(
                self.gestation_days
            ),
        )

        object.__setattr__(
            self,
            "started_on_day",
            int(
                self.started_on_day
            ),
        )

        object.__setattr__(
            self,
            "embryo_results",
            tuple(
                self.embryo_results
            ),
        )

        if (
            len(
                self.paternity_results
            )
            != len(
                self.embryo_results
            )
        ):
            raise ValueError(
                "Pregnancy requires one "
                "paternity result per embryo."
            )

        for (
            paternity,
            embryo,
        ) in zip(
            self.paternity_results,
            self.embryo_results,
        ):
            if (
                paternity.embryo_id
                != embryo.embryo_id
            ):
                raise ValueError(
                    "Pregnancy paternity and "
                    "embryo ids must match."
                )

            if (
                paternity.father
                != embryo.event.father
            ):
                raise ValueError(
                    "Pregnancy paternity father "
                    "must match embryo father."
                )

    @property
    def father_names(self):
        names = []

        for result in (
            self.paternity_results
        ):
            if (
                result.father
                not in names
            ):
                names.append(
                    result.father
                )

        return tuple(
            names
        )

    @property
    def multiple_sires(self):
        return (
            len(
                self.father_names
            )
            > 1
        )

    @property
    def expected_birth_day(self):
        return (
            self.started_on_day
            + self.gestation_days
        )

    @property
    def embryos_attempted(self):
        return len(
            self.embryo_results
        )

    @property
    def viable_embryo_count(self):
        return sum(
            1
            for result
            in self.embryo_results
            if result.viable
        )

    @property
    def nonviable_embryo_count(self):
        return (
            self.embryos_attempted
            - self.viable_embryo_count
        )

    def to_dict(self):
        return {
            "name": self.name,
            "mother": self.mother,
            "father_names": list(
                self.father_names
            ),
            "multiple_sires": (
                self.multiple_sires
            ),
            "ovulation": (
                self.ovulation.to_dict()
            ),
            "ovulation_induced": (
                self.ovulation_induced
            ),
            "mating_contact_count": (
                self.mating_contact_count
            ),
            "paternity_results": [
                result.to_dict()
                for result
                in self.paternity_results
            ],
            "gestation_days": (
                self.gestation_days
            ),
            "pregnancy_day": (
                self.pregnancy_day
            ),
            "started_on_day": (
                self.started_on_day
            ),
            "expected_birth_day": (
                self.expected_birth_day
            ),
            "embryos_attempted": (
                self.embryos_attempted
            ),
            "viable_embryo_count": (
                self.viable_embryo_count
            ),
            "nonviable_embryo_count": (
                self.nonviable_embryo_count
            ),
            "embryo_results": [
                result.to_dict()
                for result
                in self.embryo_results
            ],
            "started": self.started,
        }

@dataclass(slots=True, frozen=True)
class CatPregnancyAdvancedEvent(
    CatMatingHistoryEvent
):

    mother: str
    days_advanced: int
    pregnancy_day: int
    gestation_days: int

    name: str = field(
        default="cat_pregnancy_advanced",
        init=False,
    )

    advanced: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "mother",
            str(
                self.mother
            ),
        )

        object.__setattr__(
            self,
            "days_advanced",
            int(
                self.days_advanced
            ),
        )

        object.__setattr__(
            self,
            "pregnancy_day",
            int(
                self.pregnancy_day
            ),
        )

        object.__setattr__(
            self,
            "gestation_days",
            int(
                self.gestation_days
            ),
        )

    @property
    def ready_for_birth(self):
        return (
            self.pregnancy_day
            >= self.gestation_days
        )

    def __deepcopy__(
        self,
        memo
    ):
        return self

    def to_dict(self):
        return {
            "name": self.name,
            "mother": self.mother,
            "days_advanced": (
                self.days_advanced
            ),
            "pregnancy_day": (
                self.pregnancy_day
            ),
            "gestation_days": (
                self.gestation_days
            ),
            "ready_for_birth": (
                self.ready_for_birth
            ),
            "advanced": self.advanced,
        }
