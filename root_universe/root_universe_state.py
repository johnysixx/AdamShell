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


@dataclass(slots=True, frozen=True)
class RootUniversePermissions:
    """Immutable root universe permission rules."""

    can_modify: tuple[str, ...] = ("god",)
    can_read: tuple[str, ...] = (
        "god",
        "serpent",
        "adam",
        "eve",
        "pazuzu",
        "classical_probe_debug_entity",
    )

    def to_dict(self):
        return {
            "can_modify": list(self.can_modify),
            "can_read": list(self.can_read),
        }


@dataclass(slots=True, frozen=True)
class RootUniverseEden:
    role: str = "sandbox"
    history_origin: bool = True
    direct_parent: bool = False

    def to_dict(self):
        return {
            "role": self.role,
            "history_origin": self.history_origin,
            "direct_parent": self.direct_parent,
        }


@dataclass(slots=True)
class RootUniverseState:

    status: str = "created"
    creator: str = "god"
    administrator: str = "god"
    part_of_physics: bool = True
    access: dict = field(default_factory=_default_access)
    permissions: RootUniversePermissions = field(
        default_factory=RootUniversePermissions
    )
    eden: RootUniverseEden = field(default_factory=RootUniverseEden)
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
            "permissions": self.permissions.to_dict(),
            "eden": self.eden.to_dict(),
            "eden_influence": deepcopy(self.eden_influence),
            "history_started": self.history_started,
            "awaiting_adam_and_eve": (
                self.awaiting_adam_and_eve
            ),
            "history": deepcopy(self.history),
            "events": deepcopy(self.events),
            "tick_count": self.tick_count,
        }
