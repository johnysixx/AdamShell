from dataclasses import dataclass

from core.entity.components import (
    SpatialVector3,
)
from core.entity.quantum_box_cat_observation import (
    QuantumBoxCatObservation,
)


@dataclass(slots=True, frozen=True)
class CatQuantumBoxObservedMemoryDetails:

    box_id: str
    position: SpatialVector3 | None = None
    observation: QuantumBoxCatObservation | None = None

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "box_id",
            str(
                self.box_id
            ),
        )

        if (
            self.position is not None
            and not isinstance(
                self.position,
                SpatialVector3,
            )
        ):
            raise TypeError(
                "Quantum box observation memory "
                "position must be SpatialVector3 "
                "or None."
            )

        if (
            self.observation is not None
            and not isinstance(
                self.observation,
                QuantumBoxCatObservation,
            )
        ):
            raise TypeError(
                "Quantum box observation memory "
                "observation must be "
                "QuantumBoxCatObservation or None."
            )


@dataclass(slots=True, frozen=True)
class CatQuantumBoxTransferMemoryDetails:

    source_layer: str | None
    target_layer: str | None
    target_box_consumed: bool

    energy_j: float | None = None
    trail_id: str | None = None
    pair_id: str | None = None

    def __post_init__(
        self,
    ):
        for field_name in (
            "source_layer",
            "target_layer",
            "trail_id",
            "pair_id",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    str(
                        value
                    ),
                )

        object.__setattr__(
            self,
            "target_box_consumed",
            bool(
                self.target_box_consumed
            ),
        )

        if self.energy_j is not None:
            object.__setattr__(
                self,
                "energy_j",
                float(
                    self.energy_j
                ),
            )


@dataclass(slots=True, frozen=True)
class CatQuantumBoxTransferFailedMemoryDetails:

    reason: str
    source_layer: str | None = None
    target_layer: str | None = None
    cronenberg_id: str | None = None

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "reason",
            str(
                self.reason
            ),
        )

        for field_name in (
            "source_layer",
            "target_layer",
            "cronenberg_id",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    str(
                        value
                    ),
                )
