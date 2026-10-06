from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupLeaveDeniedResult:
    group_id: str
    cat: str
    reason: str

    name: str = field(
        default="cat_group_leave_denied",
        init=False,
    )

    left: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatLeftGroupEvent:
    group_id: str
    cat: str
    member_count: int

    name: str = field(
        default="cat_left_group",
        init=False,
    )

    left: bool = field(
        default=True,
        init=False,
    )
