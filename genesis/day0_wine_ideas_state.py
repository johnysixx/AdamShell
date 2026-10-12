from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    BarDrinkIdea,
)


@dataclass(slots=True, frozen=True)
class BartenderAsksGodForOrderEvent:
    name: str = field(
        default="bartender_asks_god_for_order",
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    question: str = field(
        default="what_will_you_have",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "question": self.question,
        }


@dataclass(slots=True, frozen=True)
class GodStillChoosingEvent:
    name: str = field(
        default="god_says_still_choosing",
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    ordered: bool = field(
        default=False,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "ordered": self.ordered,
        }


@dataclass(slots=True, frozen=True)
class LilithTastesMeadEvent:
    name: str = field(
        default="lilith_tastes_mead",
        init=False,
    )
    guest: str = field(
        default="lilith",
        init=False,
    )
    drink: str = field(
        default="mead",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
        }


@dataclass(slots=True, frozen=True)
class LilithSweetnessWineIdeaEvent:
    name: str = field(
        default="lilith_says_wine_should_be_sweet",
        init=False,
    )
    subject: str = field(
        default="wine",
        init=False,
    )
    desired_property: str = field(
        default="sweet",
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
class LilithSweetnessWineIdeaResult:
    tasting: LilithTastesMeadEvent
    idea: BarDrinkIdea

    def __post_init__(self):
        if not isinstance(
            self.tasting,
            LilithTastesMeadEvent,
        ):
            raise TypeError(
                "Lilith sweetness result requires "
                "LilithTastesMeadEvent."
            )

        if not isinstance(
            self.idea,
            BarDrinkIdea,
        ):
            raise TypeError(
                "Lilith sweetness result requires "
                "BarDrinkIdea."
            )

    def to_dict(self):
        return {
            "tasting":
                self.tasting.to_dict(),
            "idea":
                self.idea.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class GodOrdersLilithEvent:
    name: str = field(
        default="god_orders_lilith",
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

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
        }


@dataclass(slots=True, frozen=True)
class SerpentTastesMeadEvent:
    name: str = field(
        default="serpent_tastes_mead",
        init=False,
    )
    guest: str = field(
        default="serpent",
        init=False,
    )
    drink: str = field(
        default="mead",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
        }


@dataclass(slots=True, frozen=True)
class SerpentTastesBeerEvent:
    name: str = field(
        default="serpent_tastes_beer",
        init=False,
    )
    guest: str = field(
        default="serpent",
        init=False,
    )
    drink: str = field(
        default="beer",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
        }


@dataclass(slots=True, frozen=True)
class SerpentMeadBeerTastingResult:
    mead: SerpentTastesMeadEvent
    beer: SerpentTastesBeerEvent

    def __post_init__(self):
        if not isinstance(
            self.mead,
            SerpentTastesMeadEvent,
        ):
            raise TypeError(
                "Serpent tasting result requires "
                "SerpentTastesMeadEvent."
            )

        if not isinstance(
            self.beer,
            SerpentTastesBeerEvent,
        ):
            raise TypeError(
                "Serpent tasting result requires "
                "SerpentTastesBeerEvent."
            )

    def to_dict(self):
        return {
            "mead":
                self.mead.to_dict(),
            "beer":
                self.beer.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class SerpentProposesBitternessForWineEvent:
    name: str = field(
        default="serpent_proposes_bitterness_for_wine",
        init=False,
    )
    subject: str = field(
        default="wine",
        init=False,
    )
    sweetness: str = field(
        default="good_but_not_enough",
        init=False,
    )
    desired_property: str = field(
        default="bitterness",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "subject": self.subject,
            "sweetness": self.sweetness,
            "desired_property":
                self.desired_property,
        }
