from dataclasses import dataclass


@dataclass(slots=True)
class CatExplorationGoal:
    layer: str | None = None
    position: object = None
