from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatFederationLeaveDeniedResult:
    reason: str

    name: str = field(
        default="cat_federation_leave_denied",
        init=False,
    )

    left: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupLeftFederationResult:
    federation_id: str
    group_id: str

    name: str = field(
        default="cat_group_left_federation",
        init=False,
    )

    left: bool = field(
        default=True,
        init=False,
    )
