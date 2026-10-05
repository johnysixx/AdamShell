from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupInnovationCreationDeniedResult:
    reason: str
    missing: str | None = None

    name: str = field(
        default="cat_group_innovation_denied",
        init=False,
    )

    created: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupInnovationCreatedEvent:
    group_id: str
    innovation_id: str
    innovation_name: str
    sources: tuple[str, ...]
    confidence: float

    name: str = field(
        default="cat_group_innovation_created",
        init=False,
    )

    created: bool = field(
        default=True,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "group_id": self.group_id,
            "innovation_id": self.innovation_id,
            "innovation_name": self.innovation_name,
            "sources": list(
                self.sources
            ),
            "confidence": self.confidence,
            "created": self.created,
        }
