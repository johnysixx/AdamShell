from dataclasses import dataclass

from core.entity.quantum_box_occupancy_state import (
    QuantumBoxOccupancyState,
)


@dataclass(slots=True, frozen=True)
class QuantumBoxCatObservation:

    visible: bool
    recognized_as_quantum_box: bool
    occupied: bool | None
    occupancy_state: (
        QuantumBoxOccupancyState | None
    )
    occupant_identity_visible: bool = False

    def __post_init__(self):
        if (
            self.occupancy_state is not None
            and not isinstance(
                self.occupancy_state,
                QuantumBoxOccupancyState,
            )
        ):
            raise TypeError(
                "Quantum box occupancy state "
                "must use "
                "QuantumBoxOccupancyState "
                "or None."
            )

        if not self.visible:
            if self.occupied is not None:
                raise ValueError(
                    "Hidden quantum box observation "
                    "cannot expose occupancy."
                )

            if self.occupancy_state is not None:
                raise ValueError(
                    "Hidden quantum box observation "
                    "cannot expose occupancy state."
                )

            return

        if self.occupied is None:
            raise ValueError(
                "Visible quantum box observation "
                "requires occupancy."
            )

        if self.occupancy_state is None:
            raise ValueError(
                "Visible quantum box observation "
                "requires occupancy state."
            )

        if self.occupied is True:
            if (
                self.occupancy_state
                is not (
                    QuantumBoxOccupancyState
                    .CAT_TRANSFER_OCCUPIED
                )
            ):
                raise ValueError(
                    "Occupied quantum box observation "
                    "requires "
                    "CAT_TRANSFER_OCCUPIED state."
                )

            return

        if (
            self.occupancy_state
            is not (
                QuantumBoxOccupancyState
                .UNOCCUPIED
            )
        ):
            raise ValueError(
                "Unoccupied quantum box observation "
                "requires UNOCCUPIED state."
            )
