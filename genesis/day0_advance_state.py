from dataclasses import dataclass

from genesis.day0_beer_bitterness_state import (
    GodTastesBeerAndUnderstandsBitternessEvent,
    LilithSipsLilithAndReactsToBeerEvent,
)
from genesis.day0_first_conversation_state import (
    SerpentLilithConversationStartedEvent,
)
from genesis.day0_god_drink_wager_state import (
    GodAcceptsDrinkWagerEvent,
    SerpentOffersGodWagerParticipationEvent,
    SerpentTellsGodAboutDrinkWagerEvent,
)
from genesis.day0_god_lilith_service_state import (
    GodsLilithFailureResult,
    GodsLilithServiceResult,
)
from genesis.day0_god_wine_discussion_state import (
    GodJoinsSerpentLilithTableEvent,
    GodTastesLilithEvent,
    LilithAcidityRevisionResult,
    LilithGivesSerpentLilithTasteEvent,
    SerpentCallsGodToTableEvent,
    SerpentExplainsWineDiscussionEvent,
)
from genesis.day0_god_wine_service_state import (
    GodOrdersWineToJudgeDiscussionEvent,
    GodWineServiceResult,
    SerpentGrimacesAtLilithEvent,
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
from genesis.day0_sweetness_understanding_state import (
    GodFinishesSerpentsMeadEvent,
    LilithExplainsSweetnessEvent,
)
from genesis.day0_table_wine_state import (
    GodBrowsesDrinkMenuEvent,
    GodLooksAroundBarEvent,
    SerpentLilithContinueWineDiscussionEvent,
)
from genesis.day0_wine_assessment_state import (
    GodTastesExistingWineEvent,
    SerpentModerateAcidityResult,
)
from genesis.day0_wine_ideas_state import (
    BartenderAsksGodForOrderEvent,
    GodOrdersLilithEvent,
    GodStillChoosingEvent,
    LilithSweetnessWineIdeaResult,
    SerpentMeadBeerTastingResult,
)
from core.entity.social_entity import (
    CatPettedEvent,
)
from genesis.day0_bartender_bouncer_panel_state import (
    BartenderProposesBouncerPanelEvent,
    LilithExplainsWagerToBartenderEvent,
    SerpentObjectsSingleJudgeEvent,
)
from genesis.day0_bartender_judge_and_water_state import (
    GodRejectsParticipantVoteEvent,
    LilithGodMoveToBarEvent,
    SerpentOrdersWaterEvent,
    SerpentWaterServiceResult,
)
from genesis.day0_bouncer_tasting_state import (
    BouncerJudgeAcceptanceResult,
    BouncerTastingServiceResult,
)
from genesis.day0_bouncer_wager_entry_state import (
    BouncerEntersBarWithGarfieldEvent,
    SerpentExplainsWagerToBouncerEvent,
)
from genesis.day0_cat_d20_arrival_state import (
    BartenderSuggestsInvitingBouncerEvent,
    CatD20DiscussionArrivalResult,
    CatD20ScratchedEvent,
    TwoJudgePanelAcceptedEvent,
)
from genesis.day0_garfield_manifestation_state import (
    GarfieldArrivalResult,
)
from genesis.day0_serpent_returns_to_bar_state import (
    LilithGodContinueTalkingAtTableEvent,
    SerpentLeavesTableForBarEvent,
)
from genesis.day0_wager_vote_proposal_state import (
    GodAsksWhoDecidesWagerEvent,
    LilithProposesParticipantVoteEvent,
)
from meeting_place.bar_objects import (
    CatD20GarfieldTargetPreparedEvent,
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


@dataclass(slots=True, frozen=True)
class GodAtTableAdvanceResult:
    previous: GodFirstLilithTasteAdvanceResult
    called: SerpentCallsGodToTableEvent
    joined: GodJoinsSerpentLilithTableEvent


@dataclass(slots=True, frozen=True)
class AcidityWineIdeaAdvanceResult:
    previous: GodAtTableAdvanceResult
    explained: SerpentExplainsWineDiscussionEvent
    revised: LilithAcidityRevisionResult
    tasted: LilithGivesSerpentLilithTasteEvent


@dataclass(slots=True, frozen=True)
class GodReceivesWineAdvanceResult:
    previous: AcidityWineIdeaAdvanceResult
    reaction: SerpentGrimacesAtLilithEvent
    order: GodOrdersWineToJudgeDiscussionEvent
    service: GodWineServiceResult


@dataclass(slots=True, frozen=True)
class BalancedAcidityAdvanceResult:
    previous: GodReceivesWineAdvanceResult
    balance: SerpentModerateAcidityResult


@dataclass(slots=True, frozen=True)
class GodUnderstandsSweetnessAdvanceResult:
    previous: BalancedAcidityAdvanceResult
    wine: GodTastesExistingWineEvent
    explanation: LilithExplainsSweetnessEvent
    mead: GodFinishesSerpentsMeadEvent


@dataclass(slots=True, frozen=True)
class ThreeWayDrinkWagerAdvanceResult:
    previous: GodUnderstandsSweetnessAdvanceResult
    explained: SerpentTellsGodAboutDrinkWagerEvent
    offered: SerpentOffersGodWagerParticipationEvent
    accepted: GodAcceptsDrinkWagerEvent


@dataclass(slots=True, frozen=True)
class BeerBitternessAdvanceResult:
    previous: ThreeWayDrinkWagerAdvanceResult
    god_beer: GodTastesBeerAndUnderstandsBitternessEvent
    lilith: LilithSipsLilithAndReactsToBeerEvent

@dataclass(slots=True, frozen=True)
class SerpentAtBarAdvanceResult:
    previous: BeerBitternessAdvanceResult
    serpent: SerpentLeavesTableForBarEvent
    conversation: LilithGodContinueTalkingAtTableEvent


@dataclass(slots=True, frozen=True)
class WagerVoteProposalAdvanceResult:
    previous: SerpentAtBarAdvanceResult
    question: GodAsksWhoDecidesWagerEvent
    proposal: LilithProposesParticipantVoteEvent


@dataclass(slots=True, frozen=True)
class EveryoneAtBarWithWaterAdvanceResult:
    previous: WagerVoteProposalAdvanceResult
    water_order: SerpentOrdersWaterEvent
    judge_proposal: GodRejectsParticipantVoteEvent
    move: LilithGodMoveToBarEvent
    water: SerpentWaterServiceResult


@dataclass(slots=True, frozen=True)
class BartenderBouncerPanelAdvanceResult:
    previous: EveryoneAtBarWithWaterAdvanceResult
    explanation: LilithExplainsWagerToBartenderEvent
    objection: SerpentObjectsSingleJudgeEvent
    panel: BartenderProposesBouncerPanelEvent


@dataclass(slots=True, frozen=True)
class CatD20ArrivalAdvanceResult:
    previous: BartenderBouncerPanelAdvanceResult
    cat_d20: CatD20DiscussionArrivalResult


@dataclass(slots=True, frozen=True)
class GarfieldArrivalAdvanceResult:
    previous: CatD20ArrivalAdvanceResult
    accepted: TwoJudgePanelAcceptedEvent
    invite: BartenderSuggestsInvitingBouncerEvent
    scratches: tuple[CatD20ScratchedEvent, ...]
    prepared: CatD20GarfieldTargetPreparedEvent
    garfield: GarfieldArrivalResult


@dataclass(slots=True, frozen=True)
class BouncerInsideAdvanceResult:
    previous: GarfieldArrivalAdvanceResult
    bouncer: BouncerEntersBarWithGarfieldEvent


@dataclass(slots=True, frozen=True)
class BouncerKnowsWagerAdvanceResult:
    previous: BouncerInsideAdvanceResult
    explanation: SerpentExplainsWagerToBouncerEvent


@dataclass(slots=True, frozen=True)
class BouncerAcceptsJudgeAdvanceResult:
    previous: BouncerKnowsWagerAdvanceResult
    garfield_scratches: tuple[CatPettedEvent, ...]
    service: BouncerTastingServiceResult
    tasting: BouncerJudgeAcceptanceResult

@dataclass(slots=True, frozen=True)
class FirstPrivateConversationAdvanceResult:
    previous_checkpoint: dict[str, object]
    current: dict[str, object]
    conversation: SerpentLilithConversationStartedEvent

