from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupInstitutionsInheritedResult:
    parent_group: str
    child_group: str
    institutions: tuple[str, ...]

    name: str = field(
        default="cat_group_institutions_inherited",
        init=False,
    )
