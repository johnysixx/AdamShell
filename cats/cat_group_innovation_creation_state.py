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

    def __post_init__(self):
        object.__setattr__(
            self,
            "sources",
            tuple(self.sources),
        )

        object.__setattr__(
            self,
            "confidence",
            float(self.confidence),
        )
