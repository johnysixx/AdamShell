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

    def to_dict(self):
        return {
            "name":
                self.name,
            "group_id":
                self.group_id,
            "cat":
                self.cat,
            "knowledge_id":
                self.knowledge_id,
            "category":
                self.category,
            "confidence":
                self.confidence,
            "verified":
                self.verified,
            "contributed":
                self.contributed,
        }
