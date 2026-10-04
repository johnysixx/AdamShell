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

    def to_dict(self):
        return {
            "name": self.name,
            "group_id": self.group_id,
            "conflict_id": self.conflict_id,
            "mediator": self.mediator,
            "intensity": self.intensity,
            "resolved": self.resolved,
            "mediated": self.mediated,
        }
