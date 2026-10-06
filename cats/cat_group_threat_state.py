from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupThreatState:
    name: str


@dataclass(slots=True, frozen=True)
class CatGroupThreatResponseEvent:
    group_id: str
    threat: str | None
    defenders: tuple[str, ...]
    withdrawers: tuple[str, ...]
    member_count: int

    name: str = field(
        default="cat_group_threat_response",
        init=False,
    )

    responded: bool = field(
        default=True,
        init=False,
    )
