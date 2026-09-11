from copy import deepcopy
from dataclasses import dataclass, field


def _default_access():
    return {
        "god": "write",
        "serpent": "read",
        "adam": "read",
        "eve": "read",
        "pazuzu": "read",
        "classical_probe_debug_entity": "read",
    }


def _default_permissions():
    return {
        "can_modify": ["god"],
        "can_read": [
            "god",
            "serpent",
            "adam",
            "eve",
            "pazuzu",
            "classical_probe_debug_entity",
        ],
    }


def _default_eden():
    return {
        "role": "sandbox",
        "history_origin": True,
        "direct_parent": False,
    }


@dataclass(slots=True)
class RootUniverseState:

    status: str = "created"
    creator: str = "god"
    administrator: str = "god"
    part_of_physics: bool = True
    access: dict = field(default_factory=_default_access)
    permissions: dict = field(
        default_factory=_default_permissions
    )
    eden: dict = field(default_factory=_default_eden)
    eden_influence: list = field(default_factory=list)
    history_started: bool = False
    awaiting_adam_and_eve: bool = True
    history: list = field(default_factory=list)
    events: list = field(default_factory=list)
    tick_count: int = 0

    def to_dict(self):
        return {
            "status": self.status,
            "creator": self.creator,
            "administrator": self.administrator,
            "part_of_physics": self.part_of_physics,
            "access": deepcopy(self.access),
            "permissions": deepcopy(self.permissions),
            "eden": deepcopy(self.eden),
            "eden_influence": deepcopy(self.eden_influence),
            "history_started": self.history_started,
            "awaiting_adam_and_eve": (
                self.awaiting_adam_and_eve
            ),
            "history": deepcopy(self.history),
            "events": deepcopy(self.events),
            "tick_count": self.tick_count,
        }
