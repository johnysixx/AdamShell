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

    def __post_init__(self):
        object.__setattr__(
            self,
            "confidence",
            float(self.confidence),
        )
