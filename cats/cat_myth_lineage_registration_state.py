from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatMythLineageRegistrationDeniedResult:
    reason: str

    name: str = field(
        default="cat_myth_lineage_denied",
        init=False,
    )

    registered: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatMythLineageRegisteredResult:
    group_id: str
    myth_id: str

    name: str = field(
        default="cat_myth_lineage_registered",
        init=False,
    )

    registered: bool = field(
        default=True,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatMythDescendantRegisteredResult:
    group_id: str
    root_myth_id: str
    parent_myth_id: str
    child_myth_id: str

    name: str = field(
        default="cat_myth_descendant_registered",
        init=False,
    )

    registered: bool = field(
        default=True,
        init=False,
    )
