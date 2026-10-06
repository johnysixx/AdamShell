from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupScentNotMixedResult:
    group_id: str
    reason: str

    name: str = field(
        default="cat_group_scent_not_mixed",
        init=False,
    )

    mixed: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupScentMixedEvent:
    group_id: str
    members: tuple[str, ...]
    shared_scent_strength: float

    name: str = field(
        default="cat_group_scent_mixed",
        init=False,
    )

    mixed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "members",
            tuple(
                str(member)
                for member in self.members
            ),
        )

        object.__setattr__(
            self,
            "shared_scent_strength",
            float(
                self.shared_scent_strength
            ),
        )
