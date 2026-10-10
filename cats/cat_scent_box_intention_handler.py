from copy import deepcopy

from core.entity.components import SpatialVector3
from core.entity.quantum_cat_route_state import (
    QuantumCatRouteState,
)
from cats.cat_intention_state import (
    CatScentBoxTarget,
)
from cats.cat_scent_navigation_state import (
    CatScentBoxFollowState,
)
from cats.cat_scent_box_result_state import (
    CAT_SCENT_BOX_RESULT_TYPES,
    CatScentBoxFollowingEvent,
    CatScentBoxTransferredEvent,
    CatScentBoxTransferFailedResult,
)
from universe.quantum_cat_route_advance_state import (
    QUANTUM_CAT_ROUTE_ADVANCE_RESULT_TYPES,
)
from quantum.cat_box_transfer_result_state import (
    CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES,
)


class CatScentBoxIntentionHandler:

    def __init__(
        self,
        universe,
        recorder,
        same_position,
    ):
        self.universe = universe
        self._recorder = recorder
        self._position_matcher = same_position

    def _record(
        self,
        result,
    ):
        return self._recorder(
            result
        )

    def _same_position(
        self,
        first,
        second,
        tolerance=1e-09,
    ):
        return self._position_matcher(
            first,
            second,
            tolerance=tolerance,
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
            CatScentBoxTarget,
        ):
            return self._record(
                CatScentBoxTransferFailedResult(
                    cat=cat.name,
                    reason=(
                        "invalid_scent_box_target"
                    ),
                )
            )

        source_box_id = (
            target.box_id
        )

        target_box_id = (
            target.counterpart_box_id
        )

        if (
            source_box_id is None
            or target_box_id is None
        ):
            return self._record(
                CatScentBoxTransferFailedResult(
                    cat=cat.name,
                    identity=target.identity,
                    source_box_id=
                        source_box_id,
                    target_box_id=
                        target_box_id,
                    source_layer=
                        target.source_layer,
                    target_layer=
                        target.target_layer,
                    reason="missing_box_pair",
                )
            )

        transfer_system = getattr(
            self.universe,
            "cat_box_transfer",
            None,
        )

        if transfer_system is None:
            return self._record(
                CatScentBoxTransferFailedResult(
                    cat=cat.name,
                    identity=target.identity,
                    source_box_id=
                        source_box_id,
                    target_box_id=
                        target_box_id,
                    source_layer=
                        target.source_layer,
                    target_layer=
                        target.target_layer,
                    reason=(
                        "cat_box_transfer_unavailable"
                    ),
                )
            )

        source_box = next(
            (
                box
                for box
                in getattr(
                    self.universe,
                    "quantum_boxes",
                    [],
                )
                if getattr(
                    box,
                    "id",
                    None,
                )
                == source_box_id
            ),
            None,
        )

        if source_box is None:
            return (
                self
                ._finish_scent_box_follow(
                    cat=cat,
                    intention=intention,
                    event=(
                        CatScentBoxTransferFailedResult(
                            cat=cat.name,
                            identity=
                                target.identity,
                            source_box_id=
                                source_box_id,
                            target_box_id=
                                target_box_id,
                            source_layer=
                                target.source_layer,
                            target_layer=
                                target.target_layer,
                            reason=(
                                "source_box_not_found"
                            ),
                        )
                    ),
                )
            )

        if (
            getattr(
                source_box,
                "current_layer",
                None,
            )
            != cat.current_layer
        ):
            return (
                self
                ._finish_scent_box_follow(
                    cat=cat,
                    intention=intention,
                    event=(
                        CatScentBoxTransferFailedResult(
                            cat=cat.name,
                            identity=
                                target.identity,
                            source_box_id=
                                source_box_id,
                            target_box_id=
                                target_box_id,
                            source_layer=
                                target.source_layer,
                            target_layer=
                                target.target_layer,
                            reason=(
                                "source_box_not_in_cat_layer"
                            ),
                        )
                    ),
                )
            )

        follow = (
            cat.scent_box_follow
        )

        if (
            follow is not None
            and not isinstance(
                follow,
                CatScentBoxFollowState,
            )
        ):
            raise TypeError(
                "Cat scent box follow state "
                "must be "
                "CatScentBoxFollowState."
            )

        if (
            isinstance(
                follow,
                CatScentBoxFollowState,
            )
            and follow.active
            and follow.source_box_id
            == source_box_id
            and follow.target_box_id
            == target_box_id
        ):
            return (
                self
                ._advance_scent_box_follow(
                    cat=cat,
                    intention=intention,
                    cronenbergs=
                        cronenbergs,
                )
            )

        cat_position = cat.position

        source_position = getattr(
            source_box,
            "position",
            None,
        )

        if (
            not isinstance(
                cat_position,
                SpatialVector3,
            )
            or not isinstance(
                source_position,
                SpatialVector3,
            )
        ):
            return self._record(
                CatScentBoxTransferFailedResult(
                    cat=cat.name,
                    identity=target.identity,
                    source_box_id=
                        source_box_id,
                    target_box_id=
                        target_box_id,
                    source_layer=
                        target.source_layer,
                    target_layer=
                        target.target_layer,
                    reason="missing_position",
                )
            )

        if self._same_position(
            cat_position,
            source_position,
        ):
            return (
                self
                ._transfer_scent_box_follow(
                    cat=cat,
                    intention=intention,
                    source_box_id=
                        source_box_id,
                    target_box_id=
                        target_box_id,
                )
            )

        quantum_space = getattr(
            self.universe,
            "quantum_space",
            None,
        )

        if quantum_space is None:
            return self._record(
                CatScentBoxTransferFailedResult(
                    cat=cat.name,
                    identity=target.identity,
                    source_box_id=
                        source_box_id,
                    target_box_id=
                        target_box_id,
                    source_layer=
                        target.source_layer,
                    target_layer=
                        target.target_layer,
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
                    source_position,
                destination=(
                    f"scent_box:"
                    f"{source_box_id}"
                ),
                step_size=step_size,
            )
        )

        route = planned.route

        route.state = (
            QuantumCatRouteState.READY
        )

        cat.active_route_id = (
            route.route_id
        )

        cat.scent_box_follow = (
            CatScentBoxFollowState(
                active=True,
                arrived_at_box=False,
                route_id=route.route_id,
                source_box_id=
                    source_box_id,
                target_box_id=
                    target_box_id,
                identity=target.identity,
                destination=
                    source_position,
            )
        )

        cat.state = (
            "following_scent_to_quantum_box"
        )

        event = (
            CatScentBoxFollowingEvent(
                cat=cat.name,
                identity=target.identity,
                source_box_id=
                    source_box_id,
                target_box_id=
                    target_box_id,
                route_id=route.route_id,
                destination=
                    source_position,
            )
        )

        cat.mind.active_body_execution = (
            deepcopy(event)
        )

        return self._record(
            event
        )

    def _advance_scent_box_follow(
        self,
        cat,
        intention,
        cronenbergs=None,
    ):
        follow = (
            cat.scent_box_follow
        )

        if not isinstance(
            follow,
            CatScentBoxFollowState,
        ):
            raise TypeError(
                "Cat scent box follow state "
                "must be "
                "CatScentBoxFollowState."
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
            follow.arrived_at_box = True
            follow.active = False

            return (
                self
                ._transfer_scent_box_follow(
                    cat=cat,
                    intention=intention,
                    source_box_id=(
                        follow.source_box_id
                    ),
                    target_box_id=(
                        follow.target_box_id
                    ),
                )
            )

        event = (
            CatScentBoxFollowingEvent(
                cat=cat.name,
                identity=follow.identity,
                source_box_id=
                    follow.source_box_id,
                target_box_id=
                    follow.target_box_id,
                route_id=follow.route_id,
                destination=
                    follow.destination,
                position=result.position,
                route_result=
                    result.result,
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

    def _transfer_scent_box_follow(
        self,
        cat,
        intention,
        source_box_id,
        target_box_id,
    ):
        target = intention.target

        if not isinstance(
            target,
            CatScentBoxTarget,
        ):
            raise TypeError(
                "Scent box target must be "
                "CatScentBoxTarget."
            )

        transfer_result = (
            self.universe
            .cat_box_transfer
            .transfer_cat(
                cat=cat,
                source_box_id=
                    source_box_id,
                target_box_id=
                    target_box_id,
            )
        )

        if not isinstance(
            transfer_result,
            CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES,
        ):
            raise TypeError(
                "Cat quantum box transfer must "
                "return a transfer result object."
            )

        transferred = (
            transfer_result.transferred
        )

        if transferred:
            event = (
                CatScentBoxTransferredEvent(
                    cat=cat.name,
                    identity=target.identity,
                    source_box_id=
                        source_box_id,
                    target_box_id=
                        target_box_id,
                    source_layer=
                        target.source_layer,
                    target_layer=
                        target.target_layer,
                )
            )

        else:
            event = (
                CatScentBoxTransferFailedResult(
                    cat=cat.name,
                    identity=target.identity,
                    source_box_id=
                        source_box_id,
                    target_box_id=
                        target_box_id,
                    source_layer=
                        target.source_layer,
                    target_layer=
                        target.target_layer,
                    reason=(
                        getattr(
                            transfer_result,
                            "reason",
                            "quantum_box_transfer_failed",
                        )
                    ),
                    arrived_at_box=True,
                )
            )

        return (
            self
            ._finish_scent_box_follow(
                cat=cat,
                intention=intention,
                event=event,
            )
        )

    def _finish_scent_box_follow(
        self,
        cat,
        intention,
        event,
    ):
        if not isinstance(
            event,
            CAT_SCENT_BOX_RESULT_TYPES,
        ):
            raise TypeError(
                "Scent box execution must finish "
                "with a scent box result object."
            )

        mind = cat.mind

        mind.previous_intention = (
            deepcopy(intention)
        )

        mind.current_intention = None

        mind.active_body_execution = (
            deepcopy(event)
        )

        if hasattr(
            cat,
            "active_route_id",
        ):
            del cat.active_route_id

        follow = (
            cat.scent_box_follow
        )

        if (
            follow is not None
            and not isinstance(
                follow,
                CatScentBoxFollowState,
            )
        ):
            raise TypeError(
                "Cat scent box follow state "
                "must be "
                "CatScentBoxFollowState."
            )

        if isinstance(
            follow,
            CatScentBoxFollowState,
        ):
            follow.active = False

            if event.arrived_at_box:
                follow.arrived_at_box = True

        return self._record(
            event
        )
