from dataclasses import dataclass, field

from core.transitions.root_transition_status import (
    RootTransitionStatus,
)


@dataclass(slots=True)
class RootTransitionState:

    target: str = "root_universe"
    _status: RootTransitionStatus = field(
        default=RootTransitionStatus.CREATED,
        init=False,
        repr=False,
    )
    creator: str | None = None
    existence_cost_pct: float = 25.0
    energy_cost_j: float = 1000.0
    can_enter: bool = False

    @property
    def status(self):
        return self._status

    @status.setter
    def status(
        self,
        status
    ):
        if not isinstance(
            status,
            RootTransitionStatus,
        ):
            raise TypeError(
                "Root transition status must use "
                "RootTransitionStatus."
            )

        self._status = status

    def to_dict(self):
        return {
            "target": self.target,
            "state": self.status.value,
            "creator": self.creator,
            "existence_cost_pct": self.existence_cost_pct,
            "energy_cost_j": self.energy_cost_j,
            "can_enter": self.can_enter,
        }
