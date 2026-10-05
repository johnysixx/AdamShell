from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupKnowledgeShareDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_knowledge_share_denied",
        init=False,
    )

    shared: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupKnowledgeSharedResult:
    group_id: str
    knowledge_id: str
    receivers: tuple[str, ...]

    name: str = field(
        default="cat_group_knowledge_shared",
        init=False,
    )

    shared: bool = field(
        default=True,
        init=False,
    )
