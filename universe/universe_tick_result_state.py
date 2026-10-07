from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class UniverseTickPhaseCompletedResult:

    phase: str
    source_component: str
    source_operation: str
    result: object

    name: str = field(
        default="universe_tick_phase_completed",
        init=False,
    )

    ok: bool = field(
        default=True,
        init=False,
    )

    skipped: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "phase",
            str(self.phase),
        )

        object.__setattr__(
            self,
            "source_component",
            str(self.source_component),
        )

        object.__setattr__(
            self,
            "source_operation",
            str(self.source_operation),
        )


@dataclass(slots=True, frozen=True)
class UniverseTickPhaseSkippedResult:

    phase: str
    source_component: str
    reason: str

    name: str = field(
        default="universe_tick_phase_skipped",
        init=False,
    )

    source_operation: str = field(
        default="tick",
        init=False,
    )

    ok: bool = field(
        default=True,
        init=False,
    )

    skipped: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "phase",
            str(self.phase),
        )

        object.__setattr__(
            self,
            "source_component",
            str(self.source_component),
        )

        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )


@dataclass(slots=True, frozen=True)
class UniverseTickPhaseErrorResult:

    phase: str
    source_component: str
    source_operation: str
    error_type: str
    error_message: str
    cronenberg_id: str | None

    name: str = field(
        default="universe_tick_phase_failed",
        init=False,
    )

    ok: bool = field(
        default=False,
        init=False,
    )

    skipped: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "phase",
            str(self.phase),
        )

        object.__setattr__(
            self,
            "source_component",
            str(self.source_component),
        )

        object.__setattr__(
            self,
            "source_operation",
            str(self.source_operation),
        )

        object.__setattr__(
            self,
            "error_type",
            str(self.error_type),
        )

        object.__setattr__(
            self,
            "error_message",
            str(self.error_message),
        )

        if self.cronenberg_id is not None:
            object.__setattr__(
                self,
                "cronenberg_id",
                str(self.cronenberg_id),
            )


UNIVERSE_TICK_PHASE_RESULT_TYPES = (
    UniverseTickPhaseCompletedResult,
    UniverseTickPhaseSkippedResult,
    UniverseTickPhaseErrorResult,
)


@dataclass(slots=True, frozen=True)
class UniverseTickReport:

    tick: int
    phases: tuple[object, ...]
    cronenberg_count: int

    name: str = field(
        default="universe_tick_completed",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "tick",
            int(self.tick),
        )

        object.__setattr__(
            self,
            "cronenberg_count",
            int(self.cronenberg_count),
        )

        phases = tuple(
            self.phases
        )

        if not all(
            isinstance(
                phase,
                UNIVERSE_TICK_PHASE_RESULT_TYPES,
            )
            for phase
            in phases
        ):
            raise TypeError(
                "Universe tick phases must contain "
                "universe tick phase result objects."
            )

        object.__setattr__(
            self,
            "phases",
            phases,
        )

    @property
    def errors(self):
        return tuple(
            phase
            for phase
            in self.phases
            if isinstance(
                phase,
                UniverseTickPhaseErrorResult,
            )
        )

    @property
    def cronenbergs_created(self):
        return tuple(
            error.cronenberg_id
            for error
            in self.errors
            if error.cronenberg_id is not None
        )

    @property
    def error_count(self):
        return len(
            self.errors
        )

    @property
    def ok(self):
        return (
            self.error_count == 0
        )
