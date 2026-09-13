from copy import deepcopy
from dataclasses import dataclass, field


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
            "history": deepcopy(self.history),
        }
