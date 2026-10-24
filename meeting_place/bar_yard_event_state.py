from dataclasses import dataclass, field

from .lemon_tree_state import (
    LemonTreeState,
)


@dataclass(slots=True, frozen=True)
class LemonNotFoundResult:
    picker: str

    name: str = field(
        default="lemon_not_found",
        init=False,
    )

    picked: bool = field(
        default=False,
        init=False,
    )

    lemons_remaining: int = field(
        default=0,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "picker",
            str(self.picker),
        )

@dataclass(slots=True, frozen=True)
class LemonPickedResult:
    picker: str
    lemons_remaining: int

    name: str = field(
        default="lemon_picked",
        init=False,
    )

    fruit: str = field(
        default="lemon",
        init=False,
    )

    source: str = field(
        default="lemon_tree",
        init=False,
    )

    picked: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "picker",
            str(self.picker),
        )

        object.__setattr__(
            self,
            "lemons_remaining",
            int(
                self.lemons_remaining
            ),
        )

@dataclass(slots=True, frozen=True)
class LemonTreeBeginsFloweringEvent:
    month: int
    flowers: int

    name: str = field(
        default=(
            "lemon_tree_begins_flowering"
        ),
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "month",
            int(self.month),
        )

        object.__setattr__(
            self,
            "flowers",
            int(self.flowers),
        )

@dataclass(slots=True, frozen=True)
class LemonTreeNewCropEvent:
    lemons: int

    name: str = field(
        default="lemon_tree_new_crop",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "lemons",
            int(self.lemons),
        )

LEMON_TREE_LIFECYCLE_EVENT_TYPES = (
    LemonTreeBeginsFloweringEvent,
    LemonTreeNewCropEvent,
)


@dataclass(slots=True, frozen=True)
class LemonTreeMonthPassedResult:
    state: LemonTreeState
    month: int | None = None
    changed: bool = False
    events: tuple = ()

    name: str = field(
        default="lemon_tree_month_passed",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            LemonTreeState,
        ):
            raise TypeError(
                "Lemon tree month result "
                "state must use "
                "LemonTreeState."
            )

        if self.month is not None:
            object.__setattr__(
                self,
                "month",
                int(self.month),
            )

        events = tuple(
            self.events
        )

        for event in events:
            if not isinstance(
                event,
                LEMON_TREE_LIFECYCLE_EVENT_TYPES,
            ):
                raise TypeError(
                    "Lemon tree month result "
                    "requires typed lifecycle "
                    "event objects."
                )

        object.__setattr__(
            self,
            "events",
            events,
        )

        object.__setattr__(
            self,
            "changed",
            bool(self.changed),
        )
