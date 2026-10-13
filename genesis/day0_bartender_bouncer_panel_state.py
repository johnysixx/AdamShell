from dataclasses import dataclass, field

from genesis.day0_bartender_judge_and_water_state import (
    WagerDecisionMethodSnapshot,
)


@dataclass(slots=True, frozen=True)
class WagerExplanationState:
    participants: tuple[str, ...]
    contest: tuple[str, ...] = (
        "wine",
        "mead",
        "beer",
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "participants",
            tuple(
                str(participant)
                for participant
                in self.participants
            ),
        )

        object.__setattr__(
            self,
            "contest",
            tuple(
                str(drink)
                for drink
                in self.contest
            ),
        )

    def to_dict(self):
        return {
            "participants": list(
                self.participants
            ),
            "contest": list(
                self.contest
            ),
        }


@dataclass(slots=True, frozen=True)
class LilithExplainsWagerToBartenderEvent:
    wager: WagerExplanationState
    proposal: WagerDecisionMethodSnapshot

    name: str = field(
        default=(
            "lilith_explains_wager_and_"
            "bartender_judge_proposal"
        ),
        init=False,
    )
    speaker: str = field(
        default="lilith",
        init=False,
    )
    listener: str = field(
        default="bartender",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.wager,
            WagerExplanationState,
        ):
            raise TypeError(
                "Wager explanation event requires "
                "WagerExplanationState."
            )

        if not isinstance(
            self.proposal,
            WagerDecisionMethodSnapshot,
        ):
            raise TypeError(
                "Wager explanation event requires "
                "WagerDecisionMethodSnapshot."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "speaker": self.speaker,
            "listener": self.listener,
            "wager": self.wager.to_dict(),
            "proposal": self.proposal.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class SerpentObjectsSingleJudgeEvent:
    name: str = field(
        default=(
            "serpent_objects_single_judge_"
            "is_not_enough"
        ),
        init=False,
    )
    speaker: str = field(
        default="serpent",
        init=False,
    )
    single_judge: str = field(
        default="bartender",
        init=False,
    )
    objection: str = field(
        default="one_judge_is_not_enough",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "speaker": self.speaker,
            "single_judge": self.single_judge,
            "objection": self.objection,
        }


@dataclass(slots=True, frozen=True)
class BartenderProposesBouncerPanelEvent:
    proposal: WagerDecisionMethodSnapshot

    name: str = field(
        default=(
            "bartender_proposes_bouncer_"
            "as_second_taster"
        ),
        init=False,
    )
    speaker: str = field(
        default="bartender",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.proposal,
            WagerDecisionMethodSnapshot,
        ):
            raise TypeError(
                "Bouncer panel event requires "
                "WagerDecisionMethodSnapshot."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "speaker": self.speaker,
            "proposal":
                self.proposal.to_dict(),
        }
