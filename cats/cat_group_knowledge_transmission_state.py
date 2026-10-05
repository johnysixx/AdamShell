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

    def to_dict(self):
        return {
            "name":
                self.name,
            "source_group":
                self.source_group,
            "target_group":
                self.target_group,
            "knowledge_id":
                self.knowledge_id,
            "confidence":
                self.confidence,
            "transmission":
                self.transmission,
            "transmitted":
                self.transmitted,
        }
