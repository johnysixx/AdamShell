from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatInstitutionConflictEscalationDeniedResult:
    reason: str

    name: str = field(
        default="cat_institution_conflict_denied",
        init=False,
    )

    escalated: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupInstitutionalConflictEvent:
    group_id: str
    conflict_id: str
    first_institution: str
    second_institution: str
    issue: str
    intensity: float

    name: str = field(
        default="cat_group_institutional_conflict",
        init=False,
    )

    escalated: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "intensity",
            float(self.intensity),
        )
