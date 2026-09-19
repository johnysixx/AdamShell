from dataclasses import dataclass


@dataclass(slots=True)
class CatMemeticSelectionState:
    group_id: str | None = None
    score: float = 0.0

    def record(
        self,
        group_id,
        score,
    ):
        self.group_id = group_id
        self.score = float(score)

        return self
