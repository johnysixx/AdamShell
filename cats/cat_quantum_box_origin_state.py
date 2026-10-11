from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatQuantumBoxOriginState:
    source: str
    manifested_from_box: bool = field(default=True, init=False)
    born_in_quantum_layer: bool = field(default=True, init=False)

    def __post_init__(self):
        object.__setattr__(self, "source", str(self.source))

