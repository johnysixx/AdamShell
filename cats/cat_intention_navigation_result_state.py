from dataclasses import dataclass, field

from cats.cat_navigation_result_state import (
    CatNavigationNotOfferedResult,
    CatNavigationOfferedEvent,
    CatNavigationOfferAcceptedEvent,
    CatNavigationOfferNotAcceptedResult,
)


@dataclass(slots=True, frozen=True)
class CatIntentionNavigationFailedResult:

    reason: str
    cat: str | None = None
    intention: str | None = None
    body_intent: str | None = None
    navigation_offer: object | None = None
    acceptance: object | None = None
    previous_suggested_intent: str | None = None

    name: str = field(
        default="cat_intention_body_action_failed",
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if (
            self.navigation_offer is not None
            and not isinstance(
                self.navigation_offer,
                (
                    CatNavigationNotOfferedResult,
                    CatNavigationOfferedEvent,
                ),
            )
        ):
            raise TypeError(
                "Navigation failure offer must "
                "be a navigation result object."
            )

        if (
            self.acceptance is not None
            and not isinstance(
                self.acceptance,
                CatNavigationOfferNotAcceptedResult,
            )
        ):
            raise TypeError(
                "Navigation failure acceptance "
                "must be a navigation result object."
            )


@dataclass(slots=True, frozen=True)
class CatIntentionNavigationStartedEvent:

    cat: str
    intention: str
    body_intent: str
    target: object
    route_id: str
    destination: object
    navigation_offer: CatNavigationOfferedEvent
    acceptance: CatNavigationOfferAcceptedEvent

    name: str = field(
        default="cat_intention_navigation_started",
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    executed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.navigation_offer,
            CatNavigationOfferedEvent,
        ):
            raise TypeError(
                "Started navigation requires "
                "CatNavigationOfferedEvent."
            )

        if not isinstance(
            self.acceptance,
            CatNavigationOfferAcceptedEvent,
        ):
            raise TypeError(
                "Started navigation requires "
                "CatNavigationOfferAcceptedEvent."
            )
