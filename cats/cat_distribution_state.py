from dataclasses import dataclass


@dataclass(slots=True)
class CatDistributionState:
    recipient: str | None = None
    status: str | None = None
    suggested_layer: str | None = None
