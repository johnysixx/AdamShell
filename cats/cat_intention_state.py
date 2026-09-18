from dataclasses import dataclass, field


@dataclass(slots=True)
class CatIntentionCandidate:
    type: str
    target: object = None
    score: float = 0.0
    reasons: list = field(
        default_factory=list
    )

    def __post_init__(self):
        self.score = min(
            1.0,
            max(
                0.0,
                float(self.score),
            ),
        )

        self.reasons = list(
            self.reasons
        )
