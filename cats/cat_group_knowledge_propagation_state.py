from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupKnowledgePropagationDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_knowledge_propagation_denied",
        init=False,
    )

    propagated: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupKnowledgePropagatedResult:
    group_id: str
    knowledge_id: str
    receivers: tuple[str, ...]

    name: str = field(
        default="cat_group_knowledge_propagated",
        init=False,
    )

    propagated: bool = field(
        default=True,
        init=False,
    )
