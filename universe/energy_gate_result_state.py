from dataclasses import dataclass, field

from universe.energy_gate_process_state import (
    EnergyGateProcessState,
)
from universe.energy_gate_state import (
    EnergyGateCollectionEvent,
    EnergyGateState,
)


def _freeze_events(
    events,
):
    values = tuple(
        events
    )

    for event in values:
        if not isinstance(
            event,
            EnergyGateCollectionEvent,
        ):
            raise TypeError(
                "Energy gate result events must contain "
                "EnergyGateCollectionEvent objects."
            )

    return values


@dataclass(
    slots=True,
    frozen=True,
)
class EnergyGateCollectionResult:

    state: EnergyGateProcessState
    gate_state: EnergyGateState
    events: tuple[EnergyGateCollectionEvent, ...]

    name: str = field(
        default="energy_gate",
        init=False,
    )
    type: str = field(
        default="pre_physical_threshold",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            EnergyGateProcessState,
        ):
            raise TypeError(
                "Energy gate result state must use "
                "EnergyGateProcessState."
            )

        if not isinstance(
            self.gate_state,
            EnergyGateState,
        ):
            raise TypeError(
                "Energy gate result gate state must use "
                "EnergyGateState."
            )

        object.__setattr__(
            self,
            "events",
            _freeze_events(
                self.events
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "gate_state": self.gate_state.to_dict(),
            "events": [
                event.to_dict()
                for event in self.events
            ],
        }
