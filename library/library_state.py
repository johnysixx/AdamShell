from dataclasses import dataclass, field


def _default_door():
    return {
        "state": "open",
        "sign": "OPEN",
        "god_sign": None,
    }


def _default_access():
    return {
        "from": "quantum_layer",
        "exit_to": "meeting_place",
        "eden": False,
        "universe": False,
    }


def _default_permissions():
    return {
        "god": "write",
        "serpent": "read",
        "pazuzu": "read",
        "classical_probe_debug_entity": "read",
        "meeting_place": "read",
    }


@dataclass(slots=True)
class LibraryState:

    layer_type: str = "knowledge_layer"
    status: str = "initialized"
    librarian: object = None
    god_present: bool = False
    is_open: bool = True
    door_sign: str = "OPEN"
    door: dict = field(default_factory=_default_door)
    access: dict = field(default_factory=_default_access)
    permissions: dict = field(
        default_factory=_default_permissions
    )
    books: list = field(default_factory=list)
    catalog: list = field(default_factory=list)
    events: list = field(default_factory=list)
    visitors: list = field(default_factory=list)
    tick_count: int = 0

    def to_dict(self):
        return {
            "type": self.layer_type,
            "state": self.status,
            "librarian": self.librarian,
            "god_present": self.god_present,
            "is_open": self.is_open,
            "door_sign": self.door_sign,
            "door": dict(self.door),
            "access": dict(self.access),
            "permissions": dict(self.permissions),
            "books": list(self.books),
            "catalog": list(self.catalog),
            "events": list(self.events),
            "visitors": list(self.visitors),
            "tick_count": self.tick_count,
        }
