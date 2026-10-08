from dataclasses import dataclass, field

from core.entity.cat_quantum_transfer_phase import (
    CatQuantumTransferPhase,
)


@dataclass(slots=True, frozen=True)
class QuantumBoxCounterpartClearedEvent:
    previous_box_id: object
    previous_layer: str | None
    was_paired: bool

    name: str = field(
        default="quantum_box_counterpart_cleared",
        init=False,
    )

    cleared: bool = field(
        default=True,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class QuantumBoxCatTransferStartedEvent:
    cat_name: str | None
    source_box_id: object
    target_box_id: object
    source_layer: str | None
    target_layer: str | None
    started_tick: int | None

    name: str = field(
        default="quantum_box_cat_transfer_started",
        init=False,
    )

    active: bool = field(
        default=True,
        init=False,
    )

    state: CatQuantumTransferPhase = field(
        default=CatQuantumTransferPhase.SUPERPOSITION,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class QuantumBoxCatTransferEnergyConsumedEvent:
    purpose: str

    name: str = field(
        default=(
            "quantum_box_cat_transfer_"
            "energy_consumed"
        ),
        init=False,
    )

    available: bool = field(
        default=False,
        init=False,
    )

    consumed: bool = field(
        default=True,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class QuantumBoxAlreadyCollapsedResult:
    quantum_box_id: object
    result: str | None

    name: str = field(
        default="quantum_box_already_collapsed",
        init=False,
    )

    collapsed: bool = field(
        default=True,
        init=False,
    )

    changed: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class QuantumBoxCollapsedEvent:
    quantum_box_id: object
    result: str
    cause: str
    observer: str | None
    tick: int | None

    name: str = field(
        default="quantum_box_collapsed",
        init=False,
    )

    collapsed: bool = field(
        default=True,
        init=False,
    )

    changed: bool = field(
        default=True,
        init=False,
    )


QUANTUM_BOX_COLLAPSE_RESULT_TYPES = (
    QuantumBoxAlreadyCollapsedResult,
    QuantumBoxCollapsedEvent,
)
