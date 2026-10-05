from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupMythRetellingDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_myth_retelling_denied",
        init=False,
    )

    retold: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupMythRetoldResult:
    source_group: str
    target_group: str
    myth_id: str
    parent_myth_id: str
    root_myth_id: str
    credibility: float
    transformed: bool

    name: str = field(
        default="cat_group_myth_retold",
        init=False,
    )

    retold: bool = field(
        default=True,
        init=False,
    )
