from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupSplitDeniedResult:
    group_id: str
    reason: str

    name: str = field(
        default="cat_group_split_denied",
        init=False,
    )

    split: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupSplitEvent:
    parent_group: str
    daughter_group: str
    departing_members: tuple[str, ...]
    remaining_members: tuple[str, ...]
    reason: str

    name: str = field(
        default="cat_group_split",
        init=False,
    )

    split: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "departing_members",
            tuple(
                self.departing_members
            ),
        )

        object.__setattr__(
            self,
            "remaining_members",
            tuple(
                self.remaining_members
            ),
        )
