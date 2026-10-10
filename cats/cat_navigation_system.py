import random

from core.entity.quantum_cat_route_state import (
    QuantumCatRouteState,
)
from cats.cat import Cat
from cats.cat_navigation_offer_state import (
    CatNavigationOfferState,
)
from cats.cat_navigation_decision_state import (
    CatNavigationDecisionState,
)
from cats.cat_navigation_decision import (
    CatNavigationDecision,
)
from cats.cat_navigation_result_state import (
    CatNavigationDecisionFailedResult,
    CatNavigationNotOfferedResult,
    CatNavigationOfferedEvent,
    CatNavigationOfferAcceptedEvent,
    CatNavigationOfferDecidedEvent,
    CatNavigationOfferDeclinedEvent,
    CatNavigationOfferNotAcceptedResult,
    CatNavigationOfferNotDeclinedResult,
)
from universe.quantum_cat_navigation_result_state import (
    QuantumCatRouteNotPlannedResult,
    QuantumCatRoutePlannedResult,
)


class CatNavigationSystem:

    def __init__(
        self,
        cats_layer,
    ):
        self.cats_layer = cats_layer
        self.universe = (
            cats_layer.universe
        )

    def emit_event(
        self,
        event,
    ):
        return (
            self.cats_layer
            .emit_event(
                event
            )
        )

    def offer_navigation_for_suggested_intent(
        self,
        cat,
        cronenbergs=None,
        step_size=None,
    ):
        if not isinstance(
            cat,
            Cat,
        ):
            return (
                CatNavigationNotOfferedResult(
                    reason="invalid_cat",
                )
            )

        if cat.type != "cat":
            return (
                CatNavigationNotOfferedResult(
                    reason="not_a_cat",
                    cat=cat.name,
                )
            )

        current_offer = (
            cat.navigation_offer
        )

        if (
            current_offer is not None
            and not isinstance(
                current_offer,
                CatNavigationOfferState,
            )
        ):
            raise TypeError(
                "Cat navigation offer state "
                "must be "
                "CatNavigationOfferState."
            )

        suggested_intent = (
            cat.suggested_intent
        )

        if suggested_intent is None:
            return (
                CatNavigationNotOfferedResult(
                    reason="no_suggested_intent",
                    cat=cat.name,
                )
            )

        start_position = (
            cat.position
        )

        if start_position is None:
            return (
                CatNavigationNotOfferedResult(
                    reason="cat_has_no_position",
                    cat=cat.name,
                    suggested_intent=
                        suggested_intent,
                )
            )

        if not hasattr(
            self.universe,
            "quantum_space",
        ):
            self.universe.enable_quantum_layer()

        quantum_space = (
            self.universe.quantum_space
        )

        if (
            suggested_intent
            == "hunt_nearest_cronenberg"
        ):
            available_cronenbergs = (
                list(cronenbergs)
                if cronenbergs is not None
                else list(
                    self.universe.cronenbergs
                )
            )

            plan = (
                quantum_space
                .plan_cat_route_to_nearest_huntable_cronenberg(
                    cat=cat,
                    cronenbergs=
                        available_cronenbergs,
                    start_position=
                        start_position,
                    step_size=step_size,
                )
            )

        elif (
            suggested_intent
            == "return_to_bar"
        ):
            plan = (
                quantum_space
                .plan_cat_route_to_bar(
                    cat_id=cat.name,
                    start_position=
                        start_position,
                    step_size=step_size,
                )
            )

        elif (
            suggested_intent
            == "follow_entity"
        ):
            target_id = (
                cat.navigation_target
            )

            recipient_registry = getattr(
                self.universe,
                "cat_recipient_registry",
                None,
            )

            if recipient_registry is None:
                return (
                    CatNavigationNotOfferedResult(
                        reason=(
                            "recipient_registry_missing"
                        ),
                        cat=cat.name,
                        suggested_intent=
                            suggested_intent,
                        navigation_target=
                            target_id,
                    )
                )

            recipient = (
                recipient_registry.find(
                    target_id
                )
            )

            if recipient is None:
                return (
                    CatNavigationNotOfferedResult(
                        reason="recipient_not_found",
                        cat=cat.name,
                        suggested_intent=
                            suggested_intent,
                        navigation_target=
                            target_id,
                    )
                )

            recipient_layer = getattr(
                recipient,
                "current_layer",
                None,
            )

            if (
                recipient_layer
                != cat.current_layer
            ):
                return (
                    CatNavigationNotOfferedResult(
                        reason=(
                            "recipient_in_other_layer"
                        ),
                        cat=cat.name,
                        suggested_intent=
                            suggested_intent,
                        navigation_target=
                            target_id,
                        recipient_layer=
                            recipient_layer,
                        cat_layer=
                            cat.current_layer,
                    )
                )

            recipient_position = getattr(
                recipient,
                "position",
                None,
            )

            if recipient_position is None:
                return (
                    CatNavigationNotOfferedResult(
                        reason=(
                            "recipient_has_no_position"
                        ),
                        cat=cat.name,
                        suggested_intent=
                            suggested_intent,
                        navigation_target=
                            target_id,
                    )
                )

            plan = (
                quantum_space
                .plan_direct_cat_route(
                    cat_id=cat.name,
                    start_position=
                        start_position,
                    destination_position=
                        recipient_position,
                    destination=(
                        f"recipient:{target_id}"
                    ),
                    step_size=step_size,
                )
            )

        else:
            return (
                CatNavigationNotOfferedResult(
                    reason=(
                        "unsupported_suggested_intent"
                    ),
                    cat=cat.name,
                    suggested_intent=
                        suggested_intent,
                )
            )

        if isinstance(
            plan,
            QuantumCatRouteNotPlannedResult,
        ):
            return (
                CatNavigationNotOfferedResult(
                    reason=plan.reason,
                    cat=cat.name,
                    suggested_intent=
                        suggested_intent,
                    plan=plan,
                )
            )

        if not isinstance(
            plan,
            QuantumCatRoutePlannedResult,
        ):
            raise TypeError(
                "Cat navigation planner must "
                "return a quantum cat route "
                "result object."
            )

        route = (
            plan.route
        )

        cat.navigation_offer = (
            CatNavigationOfferState(
                suggested_intent=
                    suggested_intent,
                route_id=
                    route.route_id,
                destination=
                    route.destination,
                route_step_count=len(
                    route.route_steps
                ),
                accepted=False,
                declined=False,
                offered=True,
            )
        )

        event = (
            CatNavigationOfferedEvent(
                cat=cat.name,
                suggested_intent=
                    suggested_intent,
                route_id=
                    route.route_id,
                destination=
                    route.destination,
                route_step_count=len(
                    route.route_steps
                ),
            )
        )

        self.emit_event(
            event
        )

        return event

    def accept_navigation_offer(
        self,
        cat,
    ):
        if not isinstance(
            cat,
            Cat,
        ):
            return (
                CatNavigationOfferNotAcceptedResult(
                    reason="invalid_cat",
                )
            )

        offer = (
            cat.navigation_offer
        )

        if offer is None:
            return (
                CatNavigationOfferNotAcceptedResult(
                    reason="no_navigation_offer",
                    cat=cat.name,
                )
            )

        if not isinstance(
            offer,
            CatNavigationOfferState,
        ):
            raise TypeError(
                "Cat navigation offer state "
                "must be "
                "CatNavigationOfferState."
            )

        quantum_space = getattr(
            self.universe,
            "quantum_space",
            None,
        )

        if quantum_space is None:
            return (
                CatNavigationOfferNotAcceptedResult(
                    reason=(
                        "quantum_space_unavailable"
                    ),
                    cat=cat.name,
                )
            )

        route = (
            quantum_space.find_cat_route(
                cat.name
            )
        )

        if route is None:
            return (
                CatNavigationOfferNotAcceptedResult(
                    reason=(
                        "offered_route_not_found"
                    ),
                    cat=cat.name,
                )
            )

        offer.accepted = True
        offer.declined = False

        cat.intent = (
            offer.suggested_intent
        )

        cat.active_route_id = (
            route.route_id
        )

        route.state = (
            QuantumCatRouteState.READY
        )

        event = (
            CatNavigationOfferAcceptedEvent(
                cat=cat.name,
                intent=cat.intent,
                route_id=
                    route.route_id,
                destination=
                    route.destination,
                route=route,
            )
        )

        self.emit_event(
            event
        )

        return event

    def decline_navigation_offer(
        self,
        cat,
    ):
        if not isinstance(
            cat,
            Cat,
        ):
            return (
                CatNavigationOfferNotDeclinedResult(
                    reason="invalid_cat",
                )
            )

        offer = (
            cat.navigation_offer
        )

        if offer is None:
            return (
                CatNavigationOfferNotDeclinedResult(
                    reason="no_navigation_offer",
                    cat=cat.name,
                )
            )

        if not isinstance(
            offer,
            CatNavigationOfferState,
        ):
            raise TypeError(
                "Cat navigation offer state "
                "must be "
                "CatNavigationOfferState."
            )

        quantum_space = getattr(
            self.universe,
            "quantum_space",
            None,
        )

        route = (
            quantum_space.find_cat_route(
                cat.name
            )
            if quantum_space is not None
            else None
        )

        if route is not None:
            route.stop_observation()

        offer.accepted = False
        offer.declined = True

        if hasattr(
            cat,
            "intent",
        ):
            del cat.intent

        if hasattr(
            cat,
            "active_route_id",
        ):
            del cat.active_route_id

        event = (
            CatNavigationOfferDeclinedEvent(
                cat=cat.name,
                route_id=
                    offer.route_id,
                destination=
                    offer.destination,
                route=route,
            )
        )

        self.emit_event(
            event
        )

        return event

    def decide_navigation_offer(
        self,
        cat,
        rng=None,
        acceptance_chance=0.7,
    ):
        if not isinstance(
            cat,
            Cat,
        ):
            return (
                CatNavigationDecisionFailedResult(
                    reason="invalid_cat",
                )
            )

        offer = (
            cat.navigation_offer
        )

        if offer is None:
            return (
                CatNavigationDecisionFailedResult(
                    reason="no_navigation_offer",
                    cat=cat.name,
                )
            )

        if not isinstance(
            offer,
            CatNavigationOfferState,
        ):
            raise TypeError(
                "Cat navigation offer state "
                "must be "
                "CatNavigationOfferState."
            )

        current_decision = (
            cat.last_navigation_decision
        )

        if (
            current_decision is not None
            and not isinstance(
                current_decision,
                CatNavigationDecisionState,
            )
        ):
            raise TypeError(
                "Cat navigation decision state "
                "must be "
                "CatNavigationDecisionState."
            )

        acceptance_chance = float(
            acceptance_chance
        )

        if not (
            0.0
            <= acceptance_chance
            <= 1.0
        ):
            raise ValueError(
                "Cat navigation acceptance chance "
                "must be between 0 and 1."
            )

        rng = (
            rng
            or random
        )

        decision_roll = float(
            rng.random()
        )

        accepted = (
            decision_roll
            < acceptance_chance
        )

        decision_value = (
            CatNavigationDecision.ACCEPTED
            if accepted
            else CatNavigationDecision.DECLINED
        )

        cat.last_navigation_decision = (
            CatNavigationDecisionState(
                route_id=
                    offer.route_id,
                destination=
                    offer.destination,
                suggested_intent=
                    offer.suggested_intent,
                decision_roll=
                    decision_roll,
                acceptance_chance=
                    acceptance_chance,
                decision=
                    decision_value,
                decided=True,
            )
        )

        if accepted:
            result = (
                self.cats_layer.accept_navigation_offer(
                    cat
                )
            )

        else:
            result = (
                self.cats_layer.decline_navigation_offer(
                    cat
                )
            )

        event = (
            CatNavigationOfferDecidedEvent(
                cat=cat.name,
                route_id=
                    offer.route_id,
                destination=
                    offer.destination,
                suggested_intent=
                    offer.suggested_intent,
                decision_roll=
                    decision_roll,
                acceptance_chance=
                    acceptance_chance,
                decision=
                    decision_value,
                result_event=
                    result,
            )
        )

        self.emit_event(
            event
        )

        return event
