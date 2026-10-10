from copy import deepcopy

from core.entity.components import SpatialVector3
from core.entity.quantum_cat_route_state import (
    QuantumCatRouteState,
)
from cats.cat_knowledge import CatKnowledge
from cats.cat_olfaction import CatOlfaction
from cats.cat_intention_state import (
    CatScentSearchTarget,
)
from cats.cat_scent_direction_state import (
    CatScentTrailDirection,
)
from cats.cat_scent_navigation_state import (
    CatScentSearchState,
)
from cats.cat_scent_navigation_result_state import (
    CatScentReacquiredEvent,
    CatScentSearchFailedResult,
    CatScentSearchingEvent,
    CatScentSearchStepCompletedEvent,
)
from universe.quantum_cat_route_advance_state import (
    QUANTUM_CAT_ROUTE_ADVANCE_RESULT_TYPES,
)


class CatScentSearchIntentionHandler:

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
            CatScentSearchTarget,
        ):
            return self._record(
                CatScentSearchFailedResult(
                    cat=cat.name,
                    reason="invalid_search_target",
                )
            )

        identity = target.identity
        direction = target.trail_direction

        if not isinstance(
            direction,
            CatScentTrailDirection,
        ):
            return self._record(
                CatScentSearchFailedResult(
                    cat=cat.name,
                    identity=identity,
                    reason="invalid_search_direction",
                )
            )

        unit_vector = direction.unit_vector

        if (
            identity is None
            or not isinstance(
                unit_vector,
                SpatialVector3,
            )
        ):
            return self._record(
                CatScentSearchFailedResult(
                    cat=cat.name,
                    identity=identity,
                    reason="invalid_search_direction",
                )
            )

        search = cat.scent_search

        if (
            search is not None
            and not isinstance(
                search,
                CatScentSearchState,
            )
        ):
            raise TypeError(
                "Cat scent search state must be "
                "CatScentSearchState."
            )

        if (
            isinstance(
                search,
                CatScentSearchState,
            )
            and search.active
            and search.identity
            == identity
        ):
            return self._advance_scent_search(
                cat=cat,
                intention=intention,
                cronenbergs=cronenbergs,
            )

        start = cat.position

        if not isinstance(
            start,
            SpatialVector3,
        ):
            return self._record(
                CatScentSearchFailedResult(
                    cat=cat.name,
                    identity=identity,
                    reason="missing_position",
                )
            )

        distance = float(
            target.search_distance
        )

        destination = start.translated(
            dx=(
                unit_vector.x
                * distance
            ),
            dy=(
                unit_vector.y
                * distance
            ),
            dz=(
                unit_vector.z
                * distance
            ),
        )

        quantum_space = getattr(
            self.universe,
            "quantum_space",
            None,
        )

        if quantum_space is None:
            return self._record(
                CatScentSearchFailedResult(
                    cat=cat.name,
                    identity=identity,
                    reason=(
                        "quantum_space_unavailable"
                    ),
                )
            )

        planned = (
            quantum_space
            .plan_direct_cat_route(
                cat_id=cat.name,
                start_position=start,
                destination_position=
                    destination,
                destination=(
                    f"scent_search:{identity}"
                ),
                step_size=step_size,
            )
        )

        route = planned.route
        route.state = QuantumCatRouteState.READY

        cat.active_route_id = (
            route.route_id
        )

        cat.scent_search = (
            CatScentSearchState(
                active=True,
                identity=identity,
                layer=cat.current_layer,
                route_id=route.route_id,
                attempts=(
                    int(target.attempt)
                    - 1
                ),
                current_attempt=
                    int(target.attempt),
                max_attempts=
                    int(target.max_attempts),
                start_position=start,
                destination=destination,
                trail_direction=deepcopy(
                    direction
                ),
                arrived=False,
            )
        )

        event = (
            CatScentSearchingEvent(
                cat=cat.name,
                identity=identity,
                attempt=target.attempt,
                max_attempts=
                    target.max_attempts,
                route_id=route.route_id,
                start_position=start,
                destination=destination,
            )
        )

        cat.mind.active_body_execution = (
            deepcopy(event)
        )

        return self._record(
            event
        )

    def _advance_scent_search(
        self,
        cat,
        intention,
        cronenbergs=None,
    ):
        search = cat.scent_search

        if not isinstance(
            search,
            CatScentSearchState,
        ):
            raise TypeError(
                "Cat scent search state must be "
                "CatScentSearchState."
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

        olfaction = CatOlfaction.sniff(
            cat=cat,
            universe=self.universe,
        )

        reacquired = next(
            (
                item
                for item
                in olfaction.detected_aromas
                if (
                    item.recognition.recognized
                    and item.recognition.identity
                    == search.identity
                )
            ),
            None,
        )

        if reacquired is not None:
            CatKnowledge.remember_olfaction(
                cat=cat,
                olfaction=olfaction,
                current_layer=(
                    cat.current_layer
                    or "unknown"
                ),
                universe_tick=getattr(
                    self.universe,
                    "universe_tick",
                    None,
                ),
            )

            route = (
                self.universe
                .quantum_space
                .find_cat_route(
                    cat.name
                )
            )

            if route is not None:
                route.stop_observation()

            search.active = False
            search.arrived = False
            search.reacquired = True
            search.reacquired_at = (
                cat.position
            )
            search.reacquired_source_id = (
                reacquired.entity_id
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
                CatScentReacquiredEvent(
                    cat=cat.name,
                    identity=search.identity,
                    source_id=
                        reacquired.entity_id,
                    position=cat.position,
                    olfaction=deepcopy(
                        olfaction
                    ),
                )
            )

            mind.active_body_execution = (
                deepcopy(event)
            )

            return self._record(
                event
            )

        if result.arrived:
            return self._finish_scent_search(
                cat=cat,
                intention=intention,
            )

        event = (
            CatScentSearchingEvent(
                cat=cat.name,
                identity=search.identity,
                attempt=
                    search.current_attempt,
                max_attempts=
                    search.max_attempts,
                route_id=search.route_id,
                position=result.position,
                destination=
                    search.destination,
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

    def _finish_scent_search(
        self,
        cat,
        intention,
    ):
        search = cat.scent_search

        if not isinstance(
            search,
            CatScentSearchState,
        ):
            raise TypeError(
                "Cat scent search state must be "
                "CatScentSearchState."
            )

        search.active = False
        search.arrived = True
        search.attempts = int(
            search.current_attempt
            or 1
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
            CatScentSearchStepCompletedEvent(
                cat=cat.name,
                identity=search.identity,
                attempt=search.attempts,
                max_attempts=
                    search.max_attempts,
                position=cat.position,
                trail_direction=deepcopy(
                    search.trail_direction
                ),
            )
        )

        mind.active_body_execution = (
            deepcopy(event)
        )

        return self._record(
            event
        )
