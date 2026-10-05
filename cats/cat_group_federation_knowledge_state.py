from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatFederationKnowledgeDeniedResult:
    reason: str

    name: str = field(
        default="cat_federation_knowledge_denied",
        init=False,
    )

    shared: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatFederationKnowledgeSharedResult:
    federation_id: str
    source_group: str
    knowledge_id: str
    targets: tuple[str, ...]

    name: str = field(
        default="cat_federation_knowledge_shared",
        init=False,
    )

    shared: bool = field(
        default=True,
        init=False,
    )
