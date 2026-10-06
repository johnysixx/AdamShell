from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupMythCreationDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_myth_creation_denied",
        init=False,
    )

    created: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupMythCreatedEvent:
    group_id: str
    myth_id: str
    source_knowledge: str

    name: str = field(
        default="cat_group_myth_created",
        init=False,
    )

    created: bool = field(
        default=True,
        init=False,
    )
