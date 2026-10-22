from dataclasses import dataclass


@dataclass(slots=True)
class CatCulturalTraditionEvaluationState:
    tradition: str
    group_id: str
    score: float
    category: str

    def __post_init__(
        self,
    ):
        self.tradition = str(
            self.tradition
        )

        if not self.tradition:
            raise ValueError(
                "Cultural tradition evaluation "
                "requires tradition."
            )
