from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatInnovationTreeRegistrationDeniedResult:
    reason: str

    name: str = field(
        default="cat_innovation_tree_denied",
        init=False,
    )

    registered: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatInnovationTreeRegisteredResult:
    group_id: str
    innovation_id: str
    parent: str | None
    generation: int

    name: str = field(
        default="cat_innovation_tree_registered",
        init=False,
    )

    registered: bool = field(
        default=True,
        init=False,
    )
