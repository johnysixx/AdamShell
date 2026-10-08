from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class QuantumBoxesPairedEvent:
    box_a: object
    box_b: object
    layer_a: str
    layer_b: str

    name: str = field(
        default="quantum_boxes_paired",
        init=False,
    )

    paired: bool = field(
        default=True,
        init=False,
    )
