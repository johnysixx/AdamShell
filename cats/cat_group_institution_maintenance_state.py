from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupInstitutionMaintenanceDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_institution_maintenance_denied",
        init=False,
    )

    maintained: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupInstitutionMaintainedResult:
    group_id: str
    institution: str
    status: str
    continuity: float
    active: bool

    name: str = field(
        default="cat_group_institution_maintained",
        init=False,
    )

    maintained: bool = field(
        default=True,
        init=False,
    )
