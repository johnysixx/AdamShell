from dataclasses import dataclass


@dataclass(slots=True)
class CatQuantumReturnState:
    active: bool = False
    arrived_at_box: bool = False
    pair_id: str | None = None
    route_id: str | None = None
    remote_box_id: object = None
    anchor_box_id: object = None
    destination: object = None
    stabilized_path: object = None
