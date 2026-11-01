from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class LibraryDoor:
    state: str = "open"
    sign: str = "OPEN"
    god_sign: str | None = None

    def to_dict(self):
        return {
            "state": self.state,
            "sign": self.sign,
            "god_sign": self.god_sign,
        }


@dataclass(slots=True, frozen=True)
class LibraryAccess:
    """Immutable library layer access metadata."""

    source_layer: str = "quantum_layer"
    exit_to: str = "meeting_place"
    eden: bool = False
    universe: bool = False

    def to_dict(self):
        return {
            "from": self.source_layer,
            "exit_to": self.exit_to,
            "eden": self.eden,
            "universe": self.universe,
        }


@dataclass(slots=True, frozen=True)
class LibraryPermissions:
    god: str = "write"
    serpent: str = "read"
    pazuzu: str = "read"
    classical_probe_debug_entity: str = "read"
    meeting_place: str = "read"

    def access_for(self, entity_name):
        allowed_names = (
            "god",
            "serpent",
            "pazuzu",
            "classical_probe_debug_entity",
            "meeting_place",
        )

        if not isinstance(entity_name, str):
            return None

        if entity_name not in allowed_names:
            return None

        return getattr(self, entity_name)

    def to_dict(self):
        return {
            "god": self.god,
            "serpent": self.serpent,
            "pazuzu": self.pazuzu,
            "classical_probe_debug_entity": (
                self.classical_probe_debug_entity
            ),
            "meeting_place": self.meeting_place,
        }


@dataclass(slots=True, frozen=True)
class LibraryVisitor:
    name: str
    visitor_type: str = "visitor"

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.visitor_type,
        }


@dataclass(
    slots=True,
    frozen=True,
)
class LibraryEvent:

    name: str

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "name",
            str(self.name),
        )

    def to_dict(
        self,
    ):
        return {
            "name": self.name,
        }


@dataclass(
    slots=True,
    frozen=True,
)
class LibraryPresenceStatusResult:

    god_present: bool
    is_open: bool = True
    door_sign: str = "OPEN"

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "god_present",
            bool(self.god_present),
        )
        object.__setattr__(
            self,
            "is_open",
            bool(self.is_open),
        )
        object.__setattr__(
            self,
            "door_sign",
            str(self.door_sign),
        )

    def to_dict(
        self,
    ):
        return {
            "god_present": self.god_present,
            "is_open": self.is_open,
            "door_sign": self.door_sign,
        }


@dataclass(
    slots=True,
    frozen=True,
)
class GodEnteredLibraryEvent:

    god: object
    door_sign: str

    name: str = field(
        default="god_entered_library",
        init=False,
    )

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "door_sign",
            str(self.door_sign),
        )

    def to_dict(
        self,
    ):
        return {
            "event": self.name,
            "god": self.god,
            "door_sign": self.door_sign,
        }


@dataclass(
    slots=True,
    frozen=True,
)
class GodLeftLibraryEvent:

    god: object

    name: str = field(
        default="god_left_library",
        init=False,
    )

    def to_dict(
        self,
    ):
        return {
            "event": self.name,
            "god": self.god,
        }


@dataclass(slots=True)
class LibraryState:

    layer_type: str = "knowledge_layer"
    status: str = "initialized"
    librarian: object = None
    god_present: bool = False
    is_open: bool = True
    door_sign: str = "OPEN"
    door: LibraryDoor = field(
        default_factory=LibraryDoor
    )
    access: LibraryAccess = field(
        default_factory=LibraryAccess
    )
    permissions: LibraryPermissions = field(
        default_factory=LibraryPermissions
    )
    books: list = field(default_factory=list)
    catalog: list = field(default_factory=list)
    events: list = field(default_factory=list)
    visitors: tuple[LibraryVisitor, ...] = ()
    tick_count: int = 0

    def to_dict(self):
        return {
            "type": self.layer_type,
            "state": self.status,
            "librarian": self.librarian,
            "god_present": self.god_present,
            "is_open": self.is_open,
            "door_sign": self.door_sign,
            "door": self.door.to_dict(),
            "access": self.access.to_dict(),
            "permissions": self.permissions.to_dict(),
            "books": list(self.books),
            "catalog": list(self.catalog),
            "events": [
                event.to_dict()
                for event in self.events
            ],
            "visitors": [
                visitor.to_dict()
                for visitor in self.visitors
            ],
            "tick_count": self.tick_count,
        }
