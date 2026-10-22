from dataclasses import dataclass


@dataclass(slots=True)
class CatMemeticSelectionState:
    meme_id: str
    group_id: str | None = None
    score: float = 0.0

    def __post_init__(
        self,
    ):
        self.meme_id = str(
            self.meme_id
        )

        if not self.meme_id:
            raise ValueError(
                "Memetic selection requires meme_id."
            )

    def record(
        self,
        group_id,
        score,
    ):
        self.group_id = group_id
        self.score = float(score)

        return self
