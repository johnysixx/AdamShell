from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupNormDefinedEvent:
    group_id: str
    norm_id: str
    norm_name: str
    category: str

    name: str = field(
        default="cat_group_norm_defined",
        init=False,
    )

    defined: bool = field(
        default=True,
        init=False,
    )
