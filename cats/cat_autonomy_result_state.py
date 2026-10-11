from dataclasses import (
    dataclass,
    field,
)


@dataclass(
    slots=True,
    frozen=True,
)
class CatThoughtCycleFailedResult:

    cat: str | None
    observation: object
    decision: object = None

    name: str = field(
        default="cat_thought_cycle_failed",
        init=False,
    )

    completed: bool = field(
        default=False,
        init=False,
    )

    @property
    def observations(
        self,
    ):
        return self.observation


@dataclass(
    slots=True,
    frozen=True,
)
class CatThoughtCycleCompletedEvent:

    cat: str
    observations: object
    decision: object
    execution: object

    name: str = field(
        default="cat_thought_cycle_completed",
        init=False,
    )

    completed: bool = field(
        default=True,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatAutonomousTickSkippedResult:

    cat: str
    reason: str

    name: str = field(
        default="cat_autonomous_tick_skipped",
        init=False,
    )

    completed: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatAutonomousTickCompletedEvent:

    cat: str
    mode: str

    result: object = None
    needs: object = None
    needs_after_action: object = None
    thought: object = None
    completed: bool = True

    name: str = field(
        default="cat_autonomous_tick_completed",
        init=False,
    )

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "completed",
            bool(
                self.completed
            ),
        )


@dataclass(
    slots=True,
    frozen=True,
)
class CatTickOperationResult:

    cat: str
    result: object

    name: str = field(
        default="cat_tick_operation_completed",
        init=False,
    )

    ok: bool = field(
        default=True,
        init=False,
    )

    cronenberg_id: str | None = field(
        default=None,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatGroupTickOperationResult:

    group_id: str
    result: object

    name: str = field(
        default="cat_group_tick_operation_completed",
        init=False,
    )

    ok: bool = field(
        default=True,
        init=False,
    )

    cronenberg_id: str | None = field(
        default=None,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatTickErrorResult:

    source_component: str
    source_operation: str
    error_type: str
    error_message: str

    cat_name: str | None = None
    group_id: str | None = None
    cronenberg_id: str | None = None

    name: str = field(
        default="cat_tick_operation_failed",
        init=False,
    )

    ok: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatsTickCompletedEvent:

    tick: int
    cats: tuple[object, ...]
    groups: tuple[object, ...]
    errors: tuple[CatTickErrorResult, ...]
    cronenbergs_created: tuple[str, ...]

    name: str = field(
        default="cats_tick_completed",
        init=False,
    )

    ok: bool = field(
        init=False,
    )

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "tick",
            int(
                self.tick
            ),
        )

        for field_name in (
            "cats",
            "groups",
            "errors",
            "cronenbergs_created",
        ):
            object.__setattr__(
                self,
                field_name,
                tuple(
                    getattr(
                        self,
                        field_name,
                    )
                ),
            )

        object.__setattr__(
            self,
            "ok",
            not bool(
                self.errors
            ),
        )

    @property
    def error_count(
        self,
    ):
        return len(
            self.errors
        )

    @property
    def cats_processed(
        self,
    ):
        return len(
            self.cats
        )

    @property
    def groups_processed(
        self,
    ):
        return len(
            self.groups
        )
