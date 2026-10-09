from dataclasses import dataclass, field

from cats.kitten_embryo_resolver import (
    KittenEmbryoCreatedEvent,
    KittenEmbryoResult,
    NonviableKittenEmbryoReplacedByCronenbergEvent,
)

from cats.cat_birth_objects import (
    cat_birth_profile_snapshot,
    cat_phenotype_snapshot,
    kitten_genetic_viability_snapshot,
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


def _induced_ovulation_snapshot(
    event,
):
    if not isinstance(
        event,
        CatInducedOvulationResolvedEvent,
    ):
        raise TypeError(
            "Pregnancy ovulation snapshot requires "
            "CatInducedOvulationResolvedEvent."
        )

    return {
        "name": event.name,
        "female": event.female,
        "day": event.day,
        "stimulation": event.stimulation,
        "threshold": event.threshold,
        "ovulation_induced": (
            event.ovulation_induced
        ),
        "reason": event.reason,
    }


def _kitten_embryo_event_snapshot(
    event,
):
    if isinstance(
        event,
        KittenEmbryoCreatedEvent,
    ):
        return {
            "name": event.name,
            "embryo_id": event.embryo_id,
            "mother": event.mother,
            "father": event.father,
            "genetic_status": (
                event.genetic_status
            ),
            "rare": event.rare,
            "profile": (
                cat_birth_profile_snapshot(
                    event.profile
                )
            ),
            "kitten_created": (
                event.kitten_created
            ),
            "cronenberg_created": (
                event.cronenberg_created
            ),
        }

    if isinstance(
        event,
        NonviableKittenEmbryoReplacedByCronenbergEvent,
    ):
        return event.to_dict()

    raise TypeError(
        "Pregnancy embryo event snapshot "
        "requires a typed embryo event."
    )


def _kitten_embryo_result_snapshot(
    result,
):
    if not isinstance(
        result,
        KittenEmbryoResult,
    ):
        raise TypeError(
            "Pregnancy embryo snapshot requires "
            "KittenEmbryoResult."
        )

    snapshot = {
        "embryo": result.embryo,
        "viability": (
            kitten_genetic_viability_snapshot(
                result.viability
            )
        ),
    }

    if result.phenotype is not None:
        snapshot[
            "phenotype"
        ] = (
            cat_phenotype_snapshot(
                result.phenotype
            )
        )

    snapshot.update(
        {
            "cronenberg": (
                result.cronenberg
            ),
            "event": (
                _kitten_embryo_event_snapshot(
                    result.event
                )
            ),
            "viable": result.viable,
        }
    )

    return snapshot


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


def _pregnancy_paternity_snapshot(
    result,
):
    if not isinstance(
        result,
        CatPregnancyPaternityResult,
    ):
        raise TypeError(
            "Pregnancy paternity snapshot requires "
            "CatPregnancyPaternityResult."
        )

    return {
        "embryo_id": result.embryo_id,
        "father": result.father,
        "selection": {
            "name": result.selection.name,
            "father": result.selection.father,
            "successful_contact_count": (
                result.selection
                .successful_contact_count
            ),
            "total_successful_contacts": (
                result.selection
                .total_successful_contacts
            ),
            "weighted_candidate_names": list(
                result.selection
                .weighted_candidate_names
            ),
        },
    }


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
        KittenEmbryoResult,
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
                KittenEmbryoResult,
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
                _induced_ovulation_snapshot(
                    self.ovulation
                )
            ),
            "ovulation_induced": (
                self.ovulation_induced
            ),
            "mating_contact_count": (
                self.mating_contact_count
            ),
            "paternity_results": [
                _pregnancy_paternity_snapshot(
                    result
                )
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
                _kitten_embryo_result_snapshot(
                    result
                )
                for result
                in self.embryo_results
            ],
            "started": self.started,
        }

@dataclass(slots=True, frozen=True)
class CatPregnancyAdvanceDeniedResult:

    mother: str
    reason: str

    name: str = field(
        default="cat_pregnancy_advance_failed",
        init=False,
    )

    advanced: bool = field(
        default=False,
        init=False,
    )

    ready_for_birth: bool = field(
        default=False,
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
            "reason",
            str(
                self.reason
            ),
        )

    def __deepcopy__(
        self,
        memo
    ):
        return self

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
