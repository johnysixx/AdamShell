from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupAllianceBreakDeniedResult:
    first_group: str
    second_group: str
    reason: str

    name: str = field(
        default="cat_group_alliance_break_denied",
        init=False,
    )

    broken: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupAllianceBrokenEvent:
    first_group: str
    second_group: str
    reason: str
    betrayal: bool

    name: str = field(
        default="cat_group_alliance_broken",
        init=False,
    )

    broken: bool = field(
        default=True,
        init=False,
    )
