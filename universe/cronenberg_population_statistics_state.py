from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CronenbergPopulationSnapshot:

    total_count: int
    active_count: int
    inactive_count: int
    standalone_active_count: int
    active_quantum_pair_count: int
    merged_count: int
    recombined_count: int
    total_active_size: float
    total_active_energy: float
    population_pressure: float
    population_pressure_level: str

    name: str = field(
        default="cronenberg_population_statistics",
        init=False,
    )

    type: str = field(
        default="population_statistics",
        init=False,
    )

    def __post_init__(self):
        for field_name in (
            "total_count",
            "active_count",
            "inactive_count",
            "standalone_active_count",
            "active_quantum_pair_count",
            "merged_count",
            "recombined_count",
        ):
            object.__setattr__(
                self,
                field_name,
                int(
                    getattr(
                        self,
                        field_name,
                    )
                ),
            )

        for field_name in (
            "total_active_size",
            "total_active_energy",
            "population_pressure",
        ):
            object.__setattr__(
                self,
                field_name,
                float(
                    getattr(
                        self,
                        field_name,
                    )
                ),
            )

        object.__setattr__(
            self,
            "population_pressure_level",
            str(
                self.population_pressure_level
            ),
        )


@dataclass(slots=True, frozen=True)
class CronenbergPopulationDelta:

    total_count_delta: int
    active_count_delta: int
    inactive_count_delta: int
    merged_count_delta: int
    recombined_count_delta: int
    total_active_size_delta: float
    total_active_energy_delta: float
    population_pressure_delta: float


@dataclass(slots=True, frozen=True)
class CronenbergPopulationCriticalResponse:

    active: bool
    critical_pressure_streak: int
    existing_cat_count: int
    activate_existing_cats_first: bool
    overpopulation_reinforcement_allowed: bool
    reinforcement_is_last_resort: bool = True


@dataclass(slots=True, frozen=True)
class CronenbergPopulationPressureTransitionEvent:

    tick: int
    previous_level: str
    current_level: str
    previous_pressure: float
    current_pressure: float

    name: str = field(
        default=(
            "cronenberg_population_"
            "pressure_level_changed"
        ),
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CronenbergPopulationPressureWarningEvent:

    tick: int
    pressure: float
    pressure_level: str
    active_count: int
    active_quantum_pair_count: int
    existing_cats_activated: int
    activated_cat_names: tuple[str, ...]
    cat_reinforcements_suggested: bool
    cat_reinforcement_allowed: bool

    name: str = field(
        default=(
            "cronenberg_population_"
            "pressure_warning"
        ),
        init=False,
    )

    bar_assistance_requested: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "activated_cat_names",
            tuple(
                self.activated_cat_names
            ),
        )


@dataclass(slots=True, frozen=True)
class CronenbergPopulationRecord:

    tick: int
    critical_pressure_streak: int
    snapshot: CronenbergPopulationSnapshot
    delta: CronenbergPopulationDelta
    critical_response: CronenbergPopulationCriticalResponse
    pressure_transition: (
        CronenbergPopulationPressureTransitionEvent
        | None
    )
    pressure_warning: (
        CronenbergPopulationPressureWarningEvent
        | None
    )

    name: str = field(
        default="cronenberg_population_recorded",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.snapshot,
            CronenbergPopulationSnapshot,
        ):
            raise TypeError(
                "Population record requires "
                "CronenbergPopulationSnapshot."
            )

        if not isinstance(
            self.delta,
            CronenbergPopulationDelta,
        ):
            raise TypeError(
                "Population record requires "
                "CronenbergPopulationDelta."
            )

        if not isinstance(
            self.critical_response,
            CronenbergPopulationCriticalResponse,
        ):
            raise TypeError(
                "Population record requires "
                "CronenbergPopulationCriticalResponse."
            )

        if (
            self.pressure_transition is not None
            and not isinstance(
                self.pressure_transition,
                CronenbergPopulationPressureTransitionEvent,
            )
        ):
            raise TypeError(
                "Population pressure transition "
                "must be an object."
            )

        if (
            self.pressure_warning is not None
            and not isinstance(
                self.pressure_warning,
                CronenbergPopulationPressureWarningEvent,
            )
        ):
            raise TypeError(
                "Population pressure warning "
                "must be an object."
            )
