from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CronenbergManifestedEvent:
    cronenberg_id: str
    source_component: str
    source_operation: str
    error_type: str
    error_message: str
    quantum_tick: int

    name: str = field(
        default="cronenberg_manifested",
        init=False,
    )
    type: str = field(
        default="quantum_error_manifestation",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "cronenberg_id",
            str(self.cronenberg_id),
        )
        object.__setattr__(
            self,
            "source_component",
            str(self.source_component),
        )
        object.__setattr__(
            self,
            "source_operation",
            str(self.source_operation),
        )
        object.__setattr__(
            self,
            "error_type",
            str(self.error_type),
        )
        object.__setattr__(
            self,
            "error_message",
            str(self.error_message),
        )
        object.__setattr__(
            self,
            "quantum_tick",
            int(self.quantum_tick),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "cronenberg_id": self.cronenberg_id,
            "source_component": self.source_component,
            "source_operation": self.source_operation,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "quantum_tick": self.quantum_tick,
        }
