from dataclasses import dataclass


@dataclass(slots=True)
class CatQuantumExplorationState:
    active: bool = False
    arrived: bool = False
    pair_id: str | None = None
    route_id: str | None = None
    destination: object = None
    stabilized_path: object = None
    stage: int = 1
    continuation: bool = False
