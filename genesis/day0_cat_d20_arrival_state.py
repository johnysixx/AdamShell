from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatD20WelcomeEventState:
    name: str
    cat: str
    milk_served: bool
    box: str
    box_location: str
    cat_entered_box: bool
    tick: int

    @classmethod
    def from_mapping(
        cls,
        value,
    ):
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "CatD20 welcome event requires "
                "a mapping boundary value."
            )

        return cls(
            name=value["name"],
            cat=value["cat"],
            milk_served=value["milk_served"],
            box=value["box"],
            box_location=value["box_location"],
            cat_entered_box=value[
                "cat_entered_box"
            ],
            tick=value["tick"],
        )


@dataclass(slots=True, frozen=True)
class CatD20WelcomeResultState:
    name: str
    cat: object
    box: object | None
    created: bool
    entity: object | None = None
    event: CatD20WelcomeEventState | None = None

    @classmethod
    def from_mapping(
        cls,
        value,
    ):
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "CatD20 welcome result requires "
                "a mapping boundary value."
            )

        source_event = value.get(
            "event"
        )

        event = (
            None
            if source_event is None
            else CatD20WelcomeEventState
            .from_mapping(
                source_event
            )
        )

        return cls(
            name=value["name"],
            cat=value["cat"],
            box=value.get("box"),
            created=bool(
                value["created"]
            ),
            entity=value.get(
                "entity"
            ),
            event=event,
        )


@dataclass(slots=True, frozen=True)
class CatD20ArrivesDuringJudgeDiscussionEvent:
    cat: str
    current_layer: str | None
    state: str | None

    name: str = field(
        default=(
            "cat_d20_arrives_during_"
            "judge_discussion"
        ),
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "current_layer":
                self.current_layer,
            "state": self.state,
        }


@dataclass(slots=True, frozen=True)
class CatD20DiscussionArrivalResult:
    arrival: CatD20WelcomeResultState
    event: CatD20ArrivesDuringJudgeDiscussionEvent
    cat: object

    def __post_init__(self):
        if not isinstance(
            self.arrival,
            CatD20WelcomeResultState,
        ):
            raise TypeError(
                "CatD20 discussion arrival requires "
                "CatD20WelcomeResultState."
            )

        if not isinstance(
            self.event,
            CatD20ArrivesDuringJudgeDiscussionEvent,
        ):
            raise TypeError(
                "CatD20 discussion arrival requires "
                "CatD20ArrivesDuringJudgeDiscussionEvent."
            )

        if self.arrival.cat is not self.cat:
            raise ValueError(
                "CatD20 arrival cat identity "
                "must be preserved."
            )


@dataclass(slots=True, frozen=True)
class TwoJudgePanelAcceptedEvent:
    accepted_by: tuple[str, ...]
    judges: tuple[str, ...]

    name: str = field(
        default=(
            "wager_participants_accept_"
            "two_judge_panel"
        ),
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "accepted_by",
            tuple(
                str(participant)
                for participant
                in self.accepted_by
            ),
        )

        object.__setattr__(
            self,
            "judges",
            tuple(
                str(judge)
                for judge
                in self.judges
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "accepted_by": list(
                self.accepted_by
            ),
            "judges": list(
                self.judges
            ),
        }


@dataclass(slots=True, frozen=True)
class BartenderSuggestsInvitingBouncerEvent:
    name: str = field(
        default=(
            "bartender_suggests_inviting_"
            "bouncer_inside"
        ),
        init=False,
    )
    speaker: str = field(
        default="bartender",
        init=False,
    )
    invite: str = field(
        default="bouncer",
        init=False,
    )
    purpose: str = field(
        default="agree_on_wager_judging",
        init=False,
    )
    bouncer_entered: bool = field(
        default=False,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "speaker": self.speaker,
            "invite": self.invite,
            "purpose": self.purpose,
            "bouncer_entered":
                self.bouncer_entered,
        }


@dataclass(slots=True, frozen=True)
class CatD20ScratchedEvent:
    scratched_by: str

    name: str = field(
        default="cat_d20_scratched",
        init=False,
    )
    cat: str = field(
        default="cat_d20",
        init=False,
    )
    pleasant: bool = field(
        default=True,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "scratched_by":
                self.scratched_by,
            "pleasant": self.pleasant,
        }


@dataclass(slots=True, frozen=True)
class CatD20SocialState:
    scratched_by: tuple[str, ...]

    def __post_init__(self):
        object.__setattr__(
            self,
            "scratched_by",
            tuple(
                str(scratcher)
                for scratcher
                in self.scratched_by
            ),
        )
