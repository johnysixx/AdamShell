from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatInstitutionMediationDeniedResult:
    reason: str

    name: str = field(
        default="cat_institution_mediation_denied",
        init=False,
    )

    mediated: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatInstitutionConflictMediatedEvent:
    group_id: str
    conflict_id: str
    mediator: str
    intensity: float
    resolved: bool

    name: str = field(
        default="cat_institution_conflict_mediated",
        init=False,
    )

    mediated: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "intensity",
            float(self.intensity),
        )

        object.__setattr__(
            self,
            "resolved",
            bool(self.resolved),
        )
