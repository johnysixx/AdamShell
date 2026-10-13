from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class BeerTasteAssessmentState:
    good: bool | None = None
    not_so_bad: bool = True

    def to_dict(self):
        return {
            "good": self.good,
            "not_so_bad": self.not_so_bad,
        }


@dataclass(slots=True, frozen=True)
class BitternessUnderstandingState:
    bitterness: bool = True

    def to_dict(self):
        return {
            "bitterness": self.bitterness,
        }


@dataclass(slots=True, frozen=True)
class WineBitternessConclusionState:
    bitterness_belongs_in_wine: bool = False

    def to_dict(self):
        return {
            "bitterness_belongs_in_wine":
                self.bitterness_belongs_in_wine,
        }


@dataclass(slots=True, frozen=True)
class BeerBitternessConclusionState:
    bitterness_allowed: bool = True

    def to_dict(self):
        return {
            "bitterness_allowed":
                self.bitterness_allowed,
        }


@dataclass(slots=True, frozen=True)
class GodTastesBeerAndUnderstandsBitternessEvent:
    assessment: BeerTasteAssessmentState
    understands: BitternessUnderstandingState
    wine_conclusion: WineBitternessConclusionState

    name: str = field(
        default=(
            "god_tastes_beer_and_"
            "understands_bitterness"
        ),
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    drink: str = field(
        default="beer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.assessment,
            BeerTasteAssessmentState,
        ):
            raise TypeError(
                "Beer tasting event requires "
                "BeerTasteAssessmentState."
            )

        if not isinstance(
            self.understands,
            BitternessUnderstandingState,
        ):
            raise TypeError(
                "Beer tasting event requires "
                "BitternessUnderstandingState."
            )

        if not isinstance(
            self.wine_conclusion,
            WineBitternessConclusionState,
        ):
            raise TypeError(
                "Beer tasting event requires "
                "WineBitternessConclusionState."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "assessment":
                self.assessment.to_dict(),
            "understands":
                self.understands.to_dict(),
            "wine_conclusion":
                self.wine_conclusion.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class LilithSipsLilithAndReactsToBeerEvent:
    beer_conclusion: BeerBitternessConclusionState

    name: str = field(
        default=(
            "lilith_sips_lilith_"
            "and_reacts_to_beer"
        ),
        init=False,
    )
    guest: str = field(
        default="lilith",
        init=False,
    )
    drink: str = field(
        default="lilith",
        init=False,
    )
    disagrees_beer_is_good: bool = field(
        default=True,
        init=False,
    )
    effects_applied: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.beer_conclusion,
            BeerBitternessConclusionState,
        ):
            raise TypeError(
                "Lilith beer reaction requires "
                "BeerBitternessConclusionState."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "disagrees_beer_is_good":
                self.disagrees_beer_is_good,
            "beer_conclusion":
                self.beer_conclusion.to_dict(),
            "effects_applied":
                self.effects_applied,
        }
