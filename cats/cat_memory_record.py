from copy import deepcopy
from dataclasses import (
    dataclass,
    field,
    fields,
    is_dataclass,
)

from core.entity.components import (
    SpatialVector3,
)


def _memory_snapshot_value(
    value,
):
    if isinstance(
        value,
        SpatialVector3,
    ):
        return value.to_dict()

    if is_dataclass(
        value
    ):
        return {
            item.name:
                _memory_snapshot_value(
                    getattr(
                        value,
                        item.name,
                    )
                )
            for item
            in fields(value)
        }

    if isinstance(
        value,
        dict,
    ):
        return {
            key:
                _memory_snapshot_value(
                    item
                )
            for key, item
            in value.items()
        }

    if isinstance(
        value,
        list,
    ):
        return [
            _memory_snapshot_value(
                item
            )
            for item
            in value
        ]

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _memory_snapshot_value(
                item
            )
            for item
            in value
        )

    return deepcopy(
        value
    )


@dataclass(slots=True)
class CatMemoryRecord:
    memory_id: str
    sequence: int
    event_type: str
    universe_tick: object = None
    location: object = None
    participants: list = field(
        default_factory=list
    )
    details: object = field(
        default_factory=dict
    )

    def to_dict(self):
        return {
            "memory_id":
                self.memory_id,
            "sequence":
                self.sequence,
            "event_type":
                self.event_type,
            "universe_tick":
                self.universe_tick,
            "location":
                _memory_snapshot_value(
                    self.location
                ),
            "participants":
                deepcopy(
                    self.participants
                ),
            "details":
                _memory_snapshot_value(
                    self.details
                ),
        }
