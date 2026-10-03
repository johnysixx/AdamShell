from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupNormViolationDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_norm_violation_denied",
        init=False,
    )

    violated: bool = field(
        default=False,
        init=False,
    )
