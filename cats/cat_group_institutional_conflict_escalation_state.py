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

    def to_dict(self):
        return {
            "name": self.name,
            "group_id": self.group_id,
            "conflict_id": self.conflict_id,
            "first_institution": self.first_institution,
            "second_institution": self.second_institution,
            "issue": self.issue,
            "intensity": self.intensity,
            "escalated": self.escalated,
        }
