from dataclasses import dataclass

from core.entity.quantum_die import QuantumDieRollEvent
from quantum.quantum_die_resolver import (
    QuantumDieResolutionEvent,
)


@dataclass(slots=True, frozen=True)
class QuantumDieRollResult:
    roll_event: QuantumDieRollEvent
    resolution_event: QuantumDieResolutionEvent | None = None

    def __post_init__(self):
        if not isinstance(
            self.roll_event,
            QuantumDieRollEvent,
        ):
            raise TypeError(
                "Quantum die roll requires "
                "QuantumDieRollEvent."
            )

        resolution = self.resolution_event

        if resolution is None:
            return

        if not isinstance(
            resolution,
            QuantumDieResolutionEvent,
        ):
            raise TypeError(
                "Quantum die resolution requires "
                "QuantumDieResolutionEvent."
            )

        if (
            resolution.die != self.roll_event.die
            or resolution.value != self.roll_event.value
            or resolution.roll_number
            != self.roll_event.roll_number
        ):
            raise ValueError(
                "Quantum die resolution does not "
                "match the roll event."
            )

    def to_dict(self):
        snapshot = self.roll_event.to_dict()

        if self.resolution_event is not None:
            snapshot["resolution"] = (
                self.resolution_event.to_dict()
            )

        return snapshot
