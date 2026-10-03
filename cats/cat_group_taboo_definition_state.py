from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupTabooDefinedResult:
    group_id: str
    taboo_id: str
    taboo_name: str

    name: str = field(
        default="cat_group_taboo_defined",
        init=False,
    )

    defined: bool = field(
        default=True,
        init=False,
    )
