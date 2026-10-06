from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupKnowledgeContributionDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_knowledge_contribution_denied",
        init=False,
    )

    contributed: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupKnowledgeContributedEvent:
    group_id: str
    cat: str
    knowledge_id: str
    category: str
    confidence: float
    verified: bool

    name: str = field(
        default="cat_group_knowledge_contributed",
        init=False,
    )

    contributed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "confidence",
            float(self.confidence),
        )

        object.__setattr__(
            self,
            "verified",
            bool(self.verified),
        )
