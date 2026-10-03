from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupTabooViolationDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_taboo_violation_denied",
        init=False,
    )

    violated: bool = field(
        default=False,
        init=False,
    )
