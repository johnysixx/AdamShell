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


@dataclass(
    slots=True,
    frozen=True,
)
class GenesisDay0PrinciplesPresentEvent:

    participants: tuple[str, ...]

    name: str = field(
        default=(
            "genesis_day0_principles_present"
        ),
        init=False,
    )

    physical_time: object = field(
        default=None,
        init=False,
    )

    physical_space: object = field(
        default=None,
        init=False,
    )

    ordering_kind: str = field(
        default="logical_precedence",
        init=False,
    )

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "participants",
            tuple(
                str(participant)
                for participant
                in self.participants
            ),
        )

    def to_dict(
        self,
    ):
        return {
            "name": self.name,
            "participants": list(
                self.participants
            ),
            "physical_time": (
                self.physical_time
            ),
            "physical_space": (
                self.physical_space
            ),
            "ordering_kind": (
                self.ordering_kind
            ),
        }


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
