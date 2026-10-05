from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupMythTellingDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_myth_telling_denied",
        init=False,
    )

    told: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupMythToldResult:
    group_id: str
    myth_id: str
    listeners: tuple[str, ...]

    name: str = field(
        default="cat_group_myth_told",
        init=False,
    )

    told: bool = field(
        default=True,
        init=False,
    )
