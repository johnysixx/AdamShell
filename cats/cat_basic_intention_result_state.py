from dataclasses import dataclass, field

from core.entity.components import SpatialVector3


@dataclass(slots=True, frozen=True)
class CatWanderFailedResult:

    cat: str
    reason: str

    name: str = field(
        default="cat_wander_failed",
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatWanderedEvent:

    cat: str
    from_position: SpatialVector3
    position: SpatialVector3
    axis: str
    step: float

    name: str = field(
        default="cat_wandered",
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    executed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.from_position,
            SpatialVector3,
        ):
            raise TypeError(
                "Cat wander source position must "
                "be SpatialVector3."
            )

        if not isinstance(
            self.position,
            SpatialVector3,
        ):
            raise TypeError(
                "Cat wander destination position "
                "must be SpatialVector3."
            )

        if self.axis not in {
            "x",
            "y",
        }:
            raise ValueError(
                "Cat wander axis must be x or y."
            )

        object.__setattr__(
            self,
            "step",
            float(self.step),
        )


@dataclass(slots=True, frozen=True)
class CatRestStartedEvent:

    cat: str
    previous_state: object
    state: str

    name: str = field(
        default="cat_intention_rest_started",
        init=False,
    )

    intention: str = field(
        default="rest",
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    executed: bool = field(
        default=True,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatIntentionBodyActionDeferredEvent:

    cat: str
    intention: str
    target: object
    required_system: str

    name: str = field(
        default="cat_intention_body_action_deferred",
        init=False,
    )

    decision_preserved: bool = field(
        default=True,
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )

    deferred: bool = field(
        default=True,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatIntentionExecutionFailedResult:

    reason: str
    cat: str | None = None
    intention: str | None = None

    name: str = field(
        default="cat_intention_execution_failed",
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatIntentionExecutionSkippedResult:

    cat: str
    reason: str

    name: str = field(
        default="cat_intention_execution_skipped",
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatApproachFailedResult:

    cat: str
    reason: str

    target: str | None = None
    cat_layer: str | None = None
    target_layer: str | None = None

    name: str = field(
        default="cat_approach_failed",
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatApproachStartedEvent:

    cat: str
    target: str
    route_id: object
    destination: SpatialVector3

    name: str = field(
        default="cat_approach_started",
        init=False,
    )

    arrived: bool = field(
        default=False,
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    executed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(
        self,
    ):
        if not isinstance(
            self.destination,
            SpatialVector3,
        ):
            raise TypeError(
                "Cat approach destination must be "
                "SpatialVector3."
            )


@dataclass(
    slots=True,
    frozen=True,
)
class CatApproachCompletedEvent:

    cat: str
    target: str
    position: SpatialVector3
    social: object

    name: str = field(
        default="cat_approach_completed",
        init=False,
    )

    arrived: bool = field(
        default=True,
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    executed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(
        self,
    ):
        if not isinstance(
            self.position,
            SpatialVector3,
        ):
            raise TypeError(
                "Completed cat approach position "
                "must be SpatialVector3."
            )
