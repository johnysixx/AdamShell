from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupRitualDefinedResult:
    group_id: str
    ritual: str

    name: str = field(
        default="cat_group_ritual_defined",
        init=False,
    )

    defined: bool = field(
        default=True,
        init=False,
    )
