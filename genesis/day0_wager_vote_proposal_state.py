from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    BarWagerDecisionMethod,
)


@dataclass(slots=True, frozen=True)
class GodAsksWhoDecidesWagerEvent:
    name: str = field(
        default="god_asks_who_will_decide_wager",
        init=False,
    )
    speaker: str = field(
        default="god",
        init=False,
    )
    listener: str = field(
        default="lilith",
        init=False,
    )
    question: str = field(
        default="who_decides_winner",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "speaker": self.speaker,
            "listener": self.listener,
            "question": self.question,
        }


@dataclass(slots=True, frozen=True)
class LilithProposesParticipantVoteEvent:
    decision_method: BarWagerDecisionMethod

    name: str = field(
        default=(
            "lilith_proposes_participant_vote"
        ),
        init=False,
    )
    speaker: str = field(
        default="lilith",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.decision_method,
            BarWagerDecisionMethod,
        ):
            raise TypeError(
                "Participant vote proposal requires "
                "BarWagerDecisionMethod."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "speaker": self.speaker,
            "decision_method":
                self.decision_method.to_dict(),
        }
