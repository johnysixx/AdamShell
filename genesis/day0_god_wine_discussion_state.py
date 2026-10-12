from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    BarDrinkIdea,
)


@dataclass(slots=True, frozen=True)
class GodTastesLilithEvent:
    energy_before: float
    energy_after: float
    creative_will_before: float
    creative_will_after: float

    name: str = field(
        default="god_tastes_lilith",
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    drink: str = field(
        default="lilith",
        init=False,
    )
    effects_applied: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        for name in (
            "energy_before",
            "energy_after",
            "creative_will_before",
            "creative_will_after",
        ):
            object.__setattr__(
                self,
                name,
                float(
                    getattr(
                        self,
                        name,
                    )
                ),
            )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "energy_before":
                self.energy_before,
            "energy_after":
                self.energy_after,
            "creative_will_before":
                self.creative_will_before,
            "creative_will_after":
                self.creative_will_after,
            "effects_applied":
                self.effects_applied,
        }


@dataclass(slots=True, frozen=True)
class SerpentCallsGodToTableEvent:
    name: str = field(
        default=(
            "serpent_notices_god_"
            "and_calls_him_over"
        ),
        init=False,
    )
    caller: str = field(
        default="serpent",
        init=False,
    )
    called: str = field(
        default="god",
        init=False,
    )
    source: str = field(
        default="table",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "caller": self.caller,
            "called": self.called,
            "from": self.source,
        }


@dataclass(slots=True, frozen=True)
class GodJoinsSerpentLilithTableEvent:
    companions: tuple[str, ...] = (
        "serpent",
        "lilith",
    )

    name: str = field(
        default=(
            "god_joins_serpent_and_"
            "lilith_at_table"
        ),
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    drink_in_hand: str = field(
        default="lilith",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "companions",
            tuple(
                str(companion)
                for companion
                in self.companions
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "with": list(
                self.companions
            ),
            "drink_in_hand":
                self.drink_in_hand,
        }


@dataclass(slots=True, frozen=True)
class WineDiscussionSummaryState:
    fuller_flavor: bool = True
    sweetness: bool = True
    bitterness: bool = True

    def to_dict(self):
        return {
            "fuller_flavor":
                self.fuller_flavor,
            "sweetness":
                self.sweetness,
            "bitterness":
                self.bitterness,
        }


@dataclass(slots=True, frozen=True)
class SerpentExplainsWineDiscussionEvent:
    summary: WineDiscussionSummaryState

    name: str = field(
        default=(
            "serpent_explains_wine_"
            "discussion_to_god"
        ),
        init=False,
    )
    speaker: str = field(
        default="serpent",
        init=False,
    )
    listener: str = field(
        default="god",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.summary,
            WineDiscussionSummaryState,
        ):
            raise TypeError(
                "Wine discussion explanation requires "
                "WineDiscussionSummaryState."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "speaker": self.speaker,
            "listener": self.listener,
            "summary":
                self.summary.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class LilithRejectsBitternessEvent:
    name: str = field(
        default=(
            "lilith_rejects_bitterness_for_wine"
        ),
        init=False,
    )
    speaker: str = field(
        default="lilith",
        init=False,
    )
    rejected_property: str = field(
        default="bitterness",
        init=False,
    )
    reason: str = field(
        default=(
            "does_not_feel_right_for_wine"
        ),
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "speaker": self.speaker,
            "rejected_property":
                self.rejected_property,
            "reason": self.reason,
        }


@dataclass(slots=True, frozen=True)
class LilithProposesAcidityEvent:
    name: str = field(
        default=(
            "lilith_proposes_acidity_for_wine"
        ),
        init=False,
    )
    subject: str = field(
        default="wine",
        init=False,
    )
    desired_property: str = field(
        default="acidity",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "subject": self.subject,
            "desired_property":
                self.desired_property,
        }


@dataclass(slots=True, frozen=True)
class LilithAcidityRevisionResult:
    rejection: LilithRejectsBitternessEvent
    idea: BarDrinkIdea
    proposal: LilithProposesAcidityEvent

    def __post_init__(self):
        if not isinstance(
            self.rejection,
            LilithRejectsBitternessEvent,
        ):
            raise TypeError(
                "Acidity revision requires "
                "LilithRejectsBitternessEvent."
            )

        if not isinstance(
            self.idea,
            BarDrinkIdea,
        ):
            raise TypeError(
                "Acidity revision requires "
                "BarDrinkIdea."
            )

        if not isinstance(
            self.proposal,
            LilithProposesAcidityEvent,
        ):
            raise TypeError(
                "Acidity revision requires "
                "LilithProposesAcidityEvent."
            )

    def to_dict(self):
        return {
            "rejection":
                self.rejection.to_dict(),
            "idea":
                self.idea.to_dict(),
            "proposal":
                self.proposal.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class LilithGivesSerpentLilithTasteEvent:
    energy_before: float
    energy_after: float
    creative_will_before: float
    creative_will_after: float

    name: str = field(
        default=(
            "lilith_gives_serpent_"
            "taste_of_lilith"
        ),
        init=False,
    )
    giver: str = field(
        default="lilith",
        init=False,
    )
    taster: str = field(
        default="serpent",
        init=False,
    )
    drink: str = field(
        default="lilith",
        init=False,
    )
    effects_applied: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        for name in (
            "energy_before",
            "energy_after",
            "creative_will_before",
            "creative_will_after",
        ):
            object.__setattr__(
                self,
                name,
                float(
                    getattr(
                        self,
                        name,
                    )
                ),
            )

    def to_dict(self):
        return {
            "name": self.name,
            "giver": self.giver,
            "taster": self.taster,
            "drink": self.drink,
            "energy_before":
                self.energy_before,
            "energy_after":
                self.energy_after,
            "creative_will_before":
                self.creative_will_before,
            "creative_will_after":
                self.creative_will_after,
            "effects_applied":
                self.effects_applied,
        }
