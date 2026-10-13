from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class LilithExplainsSweetnessEvent:
    name: str = field(
        default="lilith_explains_sweetness_to_god",
        init=False,
    )
    speaker: str = field(
        default="lilith",
        init=False,
    )
    listener: str = field(
        default="god",
        init=False,
    )
    principle: str = field(
        default="sweetness",
        init=False,
    )
    meaning: str = field(
        default=(
            "good_wine_should_have_some_sweetness"
        ),
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "speaker": self.speaker,
            "listener": self.listener,
            "principle": self.principle,
            "meaning": self.meaning,
        }


@dataclass(slots=True, frozen=True)
class SweetnessUnderstandingState:
    sweetness: bool = True

    def to_dict(self):
        return {
            "sweetness": self.sweetness,
        }


@dataclass(slots=True, frozen=True)
class MeadSweetnessAssessmentState:
    sweet: bool = True
    good: bool = False

    def to_dict(self):
        return {
            "sweet": self.sweet,
            "good": self.good,
        }


@dataclass(slots=True, frozen=True)
class GodFinishesSerpentsMeadEvent:
    understands: SweetnessUnderstandingState
    assessment: MeadSweetnessAssessmentState

    name: str = field(
        default=(
            "god_finishes_serpents_mead_"
            "and_understands_sweetness"
        ),
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    drink: str = field(
        default="mead",
        init=False,
    )
    source: str = field(
        default="serpent",
        init=False,
    )
    finished: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.understands,
            SweetnessUnderstandingState,
        ):
            raise TypeError(
                "Mead understanding event requires "
                "SweetnessUnderstandingState."
            )

        if not isinstance(
            self.assessment,
            MeadSweetnessAssessmentState,
        ):
            raise TypeError(
                "Mead understanding event requires "
                "MeadSweetnessAssessmentState."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "source": self.source,
            "finished": self.finished,
            "understands":
                self.understands.to_dict(),
            "assessment":
                self.assessment.to_dict(),
        }
