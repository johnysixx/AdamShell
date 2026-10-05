from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupInnovationTrialDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_innovation_trial_denied",
        init=False,
    )

    tested: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupInnovationTrialResult:
    group_id: str
    innovation_id: str
    success: bool
    confidence: float
    verified: bool

    name: str = field(
        default="cat_group_innovation_trial",
        init=False,
    )

    tested: bool = field(
        default=True,
        init=False,
    )
