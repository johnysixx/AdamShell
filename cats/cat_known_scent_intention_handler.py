from copy import deepcopy

from core.entity.components import SpatialVector3
from core.entity.quantum_cat_route_state import (
    QuantumCatRouteState,
)
from cats.cat_intention_state import (
    CatKnownScentTarget,
)
from cats.cat_scent_navigation_state import (
    CatKnownScentFollowState,
)
from cats.cat_scent_navigation_result_state import (
    CatKnownScentFollowFailedResult,
    CatKnownScentFollowingEvent,
    CatKnownScentReachedEvent,
)
from universe.quantum_cat_route_advance_state import (
    QUANTUM_CAT_ROUTE_ADVANCE_RESULT_TYPES,
)


class CatKnownScentIntentionHandler:

    def __init__(
        self,
        universe,
        recorder,
    ):
        self.universe = universe
        self._recorder = recorder

    def _record(
        self,
        result,
    ):
        return self._recorder(
            result
        )

    def execute(
        self,
        cat,
        intention,
        cronenbergs=None,
        step_size=None,
    ):
        target = intention.target

        if not isinstance(
            target,
            CatKnownScentTarget,
        ):
            return self._record(
                CatKnownScentFollowFailedResult(
                    cat=cat.name,
                    reason="invalid_scent_target",
                )
            )

        layer = target.layer
        position = target.position

        if (
            layer is None
            or not isinstance(
                position,
                SpatialVector3,
            )
        ):
            return self._record(
                CatKnownScentFollowFailedResult(
                    cat=cat.name,
                    identity=target.identity,
                    reason="invalid_scent_target",
                )
            )

        if layer != cat.current_layer:
            return self._record(
                CatKnownScentFollowFailedResult(
                    cat=cat.name,
                    identity=target.identity,
                    reason=(
                        "cross_layer_scent_"
                        "navigation_not_available_yet"
                    ),
                )
            )

        follow = cat.known_scent_follow

        if (
            follow is not None
            and not isinstance(
                follow,
                CatKnownScentFollowState,
            )
        ):
            raise TypeError(
                "Cat known scent follow state "
                "must be "
                "CatKnownScentFollowState."
            )

        if (
            isinstance(
                follow,
                CatKnownScentFollowState,
            )
            and follow.active
            and follow.source_id
            == target.source_id
            and follow.destination
            == position
        ):
            return (
                self
                ._advance_known_scent_follow(
                    cat=cat,
                    intention=intention,
                    cronenbergs=
                        cronenbergs,
                )
            )

        cat_position = cat.position

        if not isinstance(
            cat_position,
            SpatialVector3,
        ):
            return self._record(
                CatKnownScentFollowFailedResult(
                    cat=cat.name,
                    identity=target.identity,
                    reason="missing_position",
                )
            )

        already_there = (
            cat_position.is_close_to(
                position,
                tolerance=1e-09,
            )
        )

        if already_there:
            return (
                self
                ._finish_known_scent_follow(
                    cat=cat,
                    intention=intention,
                    position=position,
                )
            )

        quantum_space = getattr(
            self.universe,
            "quantum_space",
            None,
        )

        if quantum_space is None:
            return self._record(
                CatKnownScentFollowFailedResult(
                    cat=cat.name,
                    identity=target.identity,
                    reason=(
                        "quantum_space_unavailable"
                    ),
                )
            )

        planned = (
            quantum_space
            .plan_direct_cat_route(
                cat_id=cat.name,
                start_position=
                    cat_position,
                destination_position=
                    position,
                destination=(
                    f"known_scent:"
                    f"{target.identity}"
                ),
                step_size=step_size,
            )
        )

        route = planned.route
        route.state = QuantumCatRouteState.READY

        cat.active_route_id = (
            route.route_id
        )

        cat.known_scent_follow = (
            CatKnownScentFollowState(
                active=True,
                arrived=False,
                route_id=route.route_id,
                identity=target.identity,
                source_id=
                    target.source_id,
                destination=position,
                trail_direction=deepcopy(
                    target.trail_direction
                ),
            )
        )

        event = (
            CatKnownScentFollowingEvent(
                cat=cat.name,
                identity=target.identity,
                layer=layer,
                destination=position,
                route_id=route.route_id,
            )
        )

        cat.mind.active_body_execution = (
            deepcopy(event)
        )

        return self._record(
            event
        )

    def _advance_known_scent_follow(
        self,
        cat,
        intention,
        cronenbergs=None,
    ):
        follow = cat.known_scent_follow

        if not isinstance(
            follow,
            CatKnownScentFollowState,
        ):
            raise TypeError(
                "Cat known scent follow state "
                "must be "
                "CatKnownScentFollowState."
            )

        result = (
            self.universe
            .quantum_space
            .advance_cat_route(
                cat=cat,
                cronenbergs=(
                    cronenbergs
                    if cronenbergs
                    is not None
                    else getattr(
                        self.universe,
                        "cronenbergs",
                        [],
                    )
                ),
                encounter_system=(
                    self.universe
                    .cat_cronenberg_encounter
                ),
                universe=self.universe,
            )
        )

        if not isinstance(
            result,
            QUANTUM_CAT_ROUTE_ADVANCE_RESULT_TYPES,
        ):
            raise TypeError(
                "Quantum cat route advancement "
                "must return a route result object."
            )

        if result.arrived:
            return (
                self
                ._finish_known_scent_follow(
                    cat=cat,
                    intention=intention,
                    position=cat.position,
                )
            )

        event = (
            CatKnownScentFollowingEvent(
                cat=cat.name,
                identity=follow.identity,
                layer=cat.current_layer,
                destination=
                    follow.destination,
                route_id=follow.route_id,
                position=result.position,
                executed=(
                    result.result
                    != "no_active_route"
                ),
            )
        )

        cat.mind.active_body_execution = (
            deepcopy(event)
        )

        return self._record(
            event
        )

    def _finish_known_scent_follow(
        self,
        cat,
        intention,
        position,
    ):
        target = intention.target
        follow = cat.known_scent_follow

        if follow is None:
            follow = (
                CatKnownScentFollowState()
            )
            cat.known_scent_follow = (
                follow
            )

        elif not isinstance(
            follow,
            CatKnownScentFollowState,
        ):
            raise TypeError(
                "Cat known scent follow state "
                "must be "
                "CatKnownScentFollowState."
            )

        follow.active = False
        follow.arrived = True
        follow.identity = target.identity
        follow.source_id = (
            target.source_id
        )

        if not isinstance(
            position,
            SpatialVector3,
        ):
            raise TypeError(
                "Known scent destination must "
                "be SpatialVector3."
            )

        follow.destination = position
        follow.trail_direction = (
            deepcopy(
                target.trail_direction
            )
        )

        if hasattr(
            cat,
            "active_route_id",
        ):
            del cat.active_route_id

        mind = cat.mind
        mind.previous_intention = (
            deepcopy(intention)
        )
        mind.current_intention = None

        event = (
            CatKnownScentReachedEvent(
                cat=cat.name,
                identity=target.identity,
                layer=cat.current_layer,
                destination=position,
                trail_direction=deepcopy(
                    target.trail_direction
                ),
            )
        )

        mind.active_body_execution = (
            deepcopy(event)
        )

        return self._record(
            event
        )
