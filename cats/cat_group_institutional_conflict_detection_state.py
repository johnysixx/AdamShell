from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatInstitutionConflictDetectionDeniedResult:
    reason: str

    name: str = field(
        default="cat_institution_conflict_detection_denied",
        init=False,
    )

    conflict: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatInstitutionConflictDetectedResult:
    group_id: str
    first_institution: str
    second_institution: str
    shared_roles: tuple[str, ...]
    shared_rituals: tuple[str, ...]
    different_purpose: bool
    score: float
    status: str
    conflict: bool

    name: str = field(
        default="cat_institution_conflict_detected",
        init=False,
    )
