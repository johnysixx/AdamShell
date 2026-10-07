from dataclasses import dataclass, field

from core.entity.quantum_cat_route import (
    QuantumCatRoute,
)
from cats.cat_navigation_decision import (
    CatNavigationDecision,
)
from universe.quantum_cat_navigation_result_state import (
    QuantumCatRouteNotPlannedResult,
)


@dataclass(slots=True, frozen=True)
class CatNavigationNotOfferedResult:

    reason: str
    cat: str | None = None
    suggested_intent: str | None = None
    navigation_target: str | None = None
    recipient_layer: object = None
    cat_layer: object = None
    plan: QuantumCatRouteNotPlannedResult | None = None

    name: str = field(
        default="cat_navigation_not_offered",
        init=False,
    )

    offered: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatNavigationOfferedEvent:

    cat: str
    suggested_intent: str
    route_id: str
    destination: object
    route_step_count: int

    name: str = field(
        default="cat_navigation_offered",
        init=False,
    )

    accepted: bool = field(
        default=False,
        init=False,
    )

    offered: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "route_step_count",
            int(self.route_step_count),
        )


@dataclass(slots=True, frozen=True)
class CatNavigationOfferNotAcceptedResult:

    reason: str
    cat: str | None = None

    name: str = field(
        default="cat_navigation_offer_not_accepted",
        init=False,
    )

    accepted: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatNavigationOfferAcceptedEvent:

    cat: str
    intent: str
    route_id: str
    destination: object
    route: QuantumCatRoute

    name: str = field(
        default="cat_navigation_offer_accepted",
        init=False,
    )

    accepted: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.route,
            QuantumCatRoute,
        ):
            raise TypeError(
                "Accepted navigation route must "
                "be QuantumCatRoute."
            )


@dataclass(slots=True, frozen=True)
class CatNavigationOfferNotDeclinedResult:

    reason: str
    cat: str | None = None

    name: str = field(
        default="cat_navigation_offer_not_declined",
        init=False,
    )

    declined: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatNavigationOfferDeclinedEvent:

    cat: str
    route_id: str | None
    destination: object
    route: QuantumCatRoute | None

    name: str = field(
        default="cat_navigation_offer_declined",
        init=False,
    )

    declined: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if (
            self.route is not None
            and not isinstance(
                self.route,
                QuantumCatRoute,
            )
        ):
            raise TypeError(
                "Declined navigation route must "
                "be QuantumCatRoute or None."
            )


@dataclass(slots=True, frozen=True)
class CatNavigationDecisionFailedResult:

    reason: str
    cat: str | None = None

    name: str = field(
        default="cat_navigation_decision_failed",
        init=False,
    )

    decided: bool = field(
        default=False,
        init=False,
    )


NAVIGATION_RESOLUTION_TYPES = (
    CatNavigationOfferAcceptedEvent,
    CatNavigationOfferNotAcceptedResult,
    CatNavigationOfferDeclinedEvent,
    CatNavigationOfferNotDeclinedResult,
)


@dataclass(slots=True, frozen=True)
class CatNavigationOfferDecidedEvent:

    cat: str
    route_id: str | None
    destination: object
    suggested_intent: str | None
    decision_roll: float
    acceptance_chance: float
    decision: CatNavigationDecision
    result_event: object

    name: str = field(
        default="cat_navigation_offer_decided",
        init=False,
    )

    decided: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.decision,
            CatNavigationDecision,
        ):
            raise TypeError(
                "Navigation decision must use "
                "CatNavigationDecision."
            )

        if not isinstance(
            self.result_event,
            NAVIGATION_RESOLUTION_TYPES,
        ):
            raise TypeError(
                "Navigation decision result must "
                "be a navigation resolution object."
            )

        object.__setattr__(
            self,
            "decision_roll",
            float(self.decision_roll),
        )

        object.__setattr__(
            self,
            "acceptance_chance",
            float(self.acceptance_chance),
        )

    @property
    def route(self):
        return getattr(
            self.result_event,
            "route",
            None,
        )
