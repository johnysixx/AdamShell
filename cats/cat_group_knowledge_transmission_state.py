from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupKnowledgeTransmissionDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_knowledge_transmission_denied",
        init=False,
    )

    transmitted: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupKnowledgeTransmittedEvent:
    source_group: str
    target_group: str
    knowledge_id: str
    confidence: float
    transmission: str

    name: str = field(
        default="cat_group_knowledge_transmitted",
        init=False,
    )

    transmitted: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "confidence",
            float(self.confidence),
        )
