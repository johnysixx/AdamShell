from copy import deepcopy
from dataclasses import dataclass, field


def _serialize_day0_history_value(
    value,
):
    to_dict = getattr(
        value,
        "to_dict",
        None,
    )

    if callable(to_dict):
        return deepcopy(
            to_dict()
        )

    return deepcopy(
        value
    )


@dataclass(slots=True)
class GenesisDay0State:

    name: str = "genesis_day0"
    status: str = "principles_required"
    physical_time_exists: bool = False
    physical_space_exists: bool = False
    history: list = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "physical_time_exists": self.physical_time_exists,
            "physical_space_exists": self.physical_space_exists,
            "history": [
                _serialize_day0_history_value(
                    item
                )
                for item in self.history
            ],
        }
