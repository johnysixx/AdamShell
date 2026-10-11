from dataclasses import dataclass, field

from cats.cat_distribution_result_state import (
    CatAssignedToRecipientEvent,
    CatDistributionSkippedResult,
    CatDistributionSuggestedResult,
)
from cats.kitten_growth_state import (
    KittenGrowthAlreadyProcessedEvent,
    KittenGrowthAppliedEvent,
)
from meeting_place.cat_meow_event_state import (
    BartenderCatMeowEvent,
    BartenderMeowReplyEvent,
)


GrowthEvent = (
    KittenGrowthAppliedEvent
    | KittenGrowthAlreadyProcessedEvent
)

DistributionResult = (
    CatAssignedToRecipientEvent
    | CatDistributionSkippedResult
    | CatDistributionSuggestedResult
)


@dataclass(slots=True, frozen=True)
class CatBartenderMeowExchangeEvent:
    cat: str
    cat_meow: BartenderCatMeowEvent
    bartender_meow: BartenderMeowReplyEvent
    tick: int = 0

    name: str = field(
        default="cat_bartender_meow_exchange",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.cat_meow,
            BartenderCatMeowEvent,
        ):
            raise TypeError(
                "Cat bartender MEOW exchange "
                "requires BartenderCatMeowEvent."
            )

        if not isinstance(
            self.bartender_meow,
            BartenderMeowReplyEvent,
        ):
            raise TypeError(
                "Cat bartender MEOW exchange "
                "requires BartenderMeowReplyEvent."
            )

        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        object.__setattr__(
            self,
            "tick",
            int(self.tick),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "cat_meow":
                self.cat_meow.to_dict(),
            "bartender_meow":
                self.bartender_meow.to_dict(),
            "tick": self.tick,
        }


@dataclass(slots=True, frozen=True)
class CatMilkServiceFailedEvent:
    cat: str
    reason: str = "milk_missing"

    name: str = field(
        default="cat_milk_service_failed",
        init=False,
    )

    served: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "reason": self.reason,
            "served": self.served,
        }


@dataclass(slots=True, frozen=True)
class CatDrankMilkAtBarEvent:
    cat: str
    bowl: str
    growth: GrowthEvent | None
    distribution: DistributionResult | None
    tick: int = 0

    name: str = field(
        default="cat_drank_milk_at_bar",
        init=False,
    )

    milk: str = field(
        default="milk",
        init=False,
    )

    served: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if (
            self.growth is not None
            and not isinstance(
                self.growth,
                (
                    KittenGrowthAppliedEvent,
                    KittenGrowthAlreadyProcessedEvent,
                ),
            )
        ):
            raise TypeError(
                "Cat milk growth must use "
                "a kitten growth event object."
            )

        if (
            self.distribution is not None
            and not isinstance(
                self.distribution,
                (
                    CatAssignedToRecipientEvent,
                    CatDistributionSkippedResult,
                    CatDistributionSuggestedResult,
                ),
            )
        ):
            raise TypeError(
                "Cat milk distribution must use "
                "a cat distribution result object."
            )

        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        object.__setattr__(
            self,
            "bowl",
            str(self.bowl),
        )

        object.__setattr__(
            self,
            "tick",
            int(self.tick),
        )

    def to_dict(self):
        result = {
            "name": self.name,
            "cat": self.cat,
            "milk": self.milk,
            "bowl": self.bowl,
            "growth": (
                None
                if self.growth is None
                else self.growth.to_dict()
            ),
            "served": self.served,
            "tick": self.tick,
        }

        if self.distribution is not None:
            # Preserve the existing public boundary:
            # distribution already returned as a typed object.
            result["distribution"] = (
                self.distribution
            )

        return result
