from dataclasses import dataclass

from genesis.day0_god_lilith_service_state import (
    GodsLilithFailureResult,
    GodsLilithServiceResult,
)
from genesis.day0_god_wine_discussion_state import (
    GodTastesLilithEvent,
)
from genesis.day0_lemon_service_state import (
    BartenderLemonRestockResult,
    BartenderLemonReturnResult,
)
from genesis.day0_lilith_service_state import (
    BartenderLearnsLilithDrinkResult,
    LilithCorrectsVodkaWithLemonEvent,
    LilithDrinkRevisionResult,
    LilithDrinkServiceResult,
    LilithJoinsSerpentAtTableEvent,
    LilithRequestsSecondSugarCubeEvent,
)
from genesis.day0_table_wine_state import (
    GodBrowsesDrinkMenuEvent,
    GodLooksAroundBarEvent,
    SerpentLilithContinueWineDiscussionEvent,
)
from genesis.day0_wine_ideas_state import (
    BartenderAsksGodForOrderEvent,
    GodOrdersLilithEvent,
    GodStillChoosingEvent,
    LilithSweetnessWineIdeaResult,
    SerpentMeadBeerTastingResult,
)
from meeting_place.bar_objects import (
    BarDrink,
    BarDrinkDiscussion,
    BarDrinkIdea,
)


@dataclass(slots=True, frozen=True)
class LilithDrinkLearnedAdvanceResult:
    returned: BartenderLemonReturnResult
    vodka_with_lemon: BarDrink
    correction: LilithCorrectsVodkaWithLemonEvent
    learned: BartenderLearnsLilithDrinkResult


@dataclass(slots=True, frozen=True)
class GoodDrinkDiscussionAdvanceResult:
    served: LilithDrinkServiceResult
    tasted: LilithRequestsSecondSugarCubeEvent
    revised: LilithDrinkRevisionResult
    moved: LilithJoinsSerpentAtTableEvent
    discussion: BarDrinkDiscussion


@dataclass(slots=True, frozen=True)
class GodBrowsingMenuAdvanceResult:
    looked: GodLooksAroundBarEvent
    continued: SerpentLilithContinueWineDiscussionEvent
    browsed: GodBrowsesDrinkMenuEvent


@dataclass(slots=True, frozen=True)
class SecondWineIdeaAdvanceResult:
    bartender: BartenderAsksGodForOrderEvent
    god: GodStillChoosingEvent
    wine_idea: LilithSweetnessWineIdeaResult


@dataclass(slots=True, frozen=True)
class ThirdWineIdeaAdvanceResult:
    god_order: GodOrdersLilithEvent
    tasting: SerpentMeadBeerTastingResult
    wine_idea: BarDrinkIdea


@dataclass(slots=True, frozen=True)
class LemonRestockAdvanceResult:
    previous: ThirdWineIdeaAdvanceResult
    failure: GodsLilithFailureResult
    restock: BartenderLemonRestockResult


@dataclass(slots=True, frozen=True)
class GodHoldingLilithAdvanceResult:
    previous: LemonRestockAdvanceResult
    drink: BarDrink
    service: GodsLilithServiceResult


@dataclass(slots=True, frozen=True)
class GodFirstLilithTasteAdvanceResult:
    previous: GodHoldingLilithAdvanceResult
    tasting: GodTastesLilithEvent
