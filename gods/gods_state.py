from copy import deepcopy
from dataclasses import dataclass, field


def _default_permissions():
    return {
        "can_create": True,
        "can_administer": True,
        "can_modify": True,
    }


@dataclass(slots=True)
class GodsState:

    layer_type: str = "entity_layer"
    status: str = "created"
    gods: list = field(default_factory=list)
    events: list = field(default_factory=list)
    tick_count: int = 0
    permissions: dict = field(
        default_factory=_default_permissions
    )

    def to_dict(self):
        return {
            "type": self.layer_type,
            "state": self.status,
            "gods": list(self.gods),
            "events": deepcopy(self.events),
            "tick_count": self.tick_count,
            "permissions": dict(self.permissions),
        }
