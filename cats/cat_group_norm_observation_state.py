from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupNormObservationDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_norm_observation_denied",
        init=False,
    )

    observed: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupNormObservedResult:
    group_id: str
    cat: str
    norm_id: str

    name: str = field(
        default="cat_group_norm_observed",
        init=False,
    )

    observed: bool = field(
        default=True,
        init=False,
    )
