from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupKnowledgeVerificationDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_knowledge_verification_denied",
        init=False,
    )

    verified: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupKnowledgeVerifiedEvent:
    group_id: str
    cat: str
    knowledge_id: str
    outcome: str
    confidence: float

    name: str = field(
        default="cat_group_knowledge_verified",
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
            "outcome":
                self.outcome,
            "confidence":
                self.confidence,
        }
