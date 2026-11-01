from copy import deepcopy
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class GodsPermissions:
    """Immutable permissions for the gods layer."""

    can_create: bool = True
    can_administer: bool = True
    can_modify: bool = True

    def to_dict(self):
        return {
            "can_create": self.can_create,
            "can_administer": self.can_administer,
            "can_modify": self.can_modify,
        }


def _serialize_gods_state_value(
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


@dataclass(
    slots=True,
    frozen=True,
)
class GodBookCreatedEvent:

    god: str
    book: object

    name: str = field(
        default="god_book_created",
        init=False,
    )

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "god",
            str(self.god),
        )

    def to_dict(
        self,
    ):
        return {
            "name": self.name,
            "god": self.god,
            "book": self.book,
        }


@dataclass(
    slots=True,
    frozen=True,
)
class GodMaskReleasedResult:

    released_mask: str
    god: object
    mask: object

    name: str = field(
        default="god_mask_released",
        init=False,
    )

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "released_mask",
            str(
                self.released_mask
            ),
        )

    def to_dict(
        self,
    ):
        return {
            "name": self.name,
            "released_mask": (
                self.released_mask
            ),
            "god": self.god,
            "mask": self.mask,
        }


@dataclass(slots=True)
class GodsState:

    layer_type: str = "entity_layer"
    status: str = "created"
    gods: list = field(default_factory=list)
    events: list = field(default_factory=list)
    tick_count: int = 0
    permissions: GodsPermissions = field(
        default_factory=GodsPermissions
    )

    def to_dict(self):
        return {
            "type": self.layer_type,
            "state": self.status,
            "gods": list(self.gods),
            "events": [
                _serialize_gods_state_value(
                    event
                )
                for event in self.events
            ],
            "tick_count": self.tick_count,
            "permissions": self.permissions.to_dict(),
        }
