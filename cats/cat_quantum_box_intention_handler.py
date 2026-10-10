from copy import deepcopy

from core.entity.components import (
    SpatialVector3,
)
from core.entity.quantum_cat_route_state import (
    QuantumCatRouteState,
)
from core.entity.quantum_box_cat_observation import (
    QuantumBoxCatObservation,
)

from cats.cat_quantum_observation_state import (
    CatQuantumCounterpartObservation,
)
from cats.cat_intention_state import (
    CatExploreBoxTarget,
    CatQuantumBoxTravelTarget,
    CatQuantumCounterpartSenseTarget,
)
from cats.cat_box_exploration_state import (
    CatBoxExplorationState,
)
from universe.quantum_cat_route_advance_state import (
    QUANTUM_CAT_ROUTE_ADVANCE_RESULT_TYPES,
)
from quantum.cat_box_transfer_result_state import (
    CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES,
)


class CatQuantumBoxIntentionHandler:

    def __init__(
        self,
        universe,
        recorder,
        same_position,
    ):
        self.universe = universe
        self._recorder = recorder
        self._position_matcher = (
            same_position
        )

    def _record(
        self,
        event,
    ):
        return self._recorder(
            event
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

    def travel(self, cat, intention):
        target = intention.target

        if not isinstance(
            target,
            CatQuantumBoxTravelTarget,
        ):
            return self._record({
                'name': (
                    'cat_quantum_box_travel_failed'
                ),
                'cat': cat.name,
                'reason': (
                    'invalid_quantum_box_travel_target'
                ),
                'executed': False,
            })

        source_box_id = target.source_box_id
        counterpart_box_id = (
            target.counterpart_box_id
        )
        if source_box_id is None or counterpart_box_id is None:
            return self._record({'name': 'cat_quantum_box_travel_failed', 'cat': cat.name, 'reason': 'missing_box_pair', 'executed': False})
        observation = (
            cat.current_quantum_counterpart_observation
        )

        if observation is None:
            return self._record({
                'name': (
                    'cat_quantum_box_travel_failed'
                ),
                'cat': cat.name,
                'source_box_id': source_box_id,
                'counterpart_box_id': (
                    counterpart_box_id
                ),
                'reason': (
                    'counterpart_observation_missing'
                ),
                'executed': False,
            })

        if not isinstance(
            observation,
            CatQuantumCounterpartObservation,
        ):
            raise TypeError(
                'Quantum counterpart observation '
                'must be '
                'CatQuantumCounterpartObservation.'
            )
        if not observation.pair_currently_valid:
            return self._record({'name': 'cat_quantum_box_travel_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'counterpart_box_id': counterpart_box_id, 'reason': 'counterpart_observation_invalid', 'executed': False})
        if observation.source_box_id != source_box_id:
            return self._record({'name': 'cat_quantum_box_travel_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'counterpart_box_id': counterpart_box_id, 'reason': 'observation_pair_mismatch', 'executed': False})
        source_box = next((box for box in getattr(self.universe, 'quantum_boxes', []) if getattr(box, 'id', None) == source_box_id), None)
        if source_box is None:
            return self._record({'name': 'cat_quantum_box_travel_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'counterpart_box_id': counterpart_box_id, 'reason': 'source_box_no_longer_exists', 'executed': False})
        if getattr(source_box, 'current_layer', None) != cat.current_layer:
            return self._record({'name': 'cat_quantum_box_travel_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'counterpart_box_id': counterpart_box_id, 'reason': 'source_box_not_in_cat_layer', 'executed': False})
        source_position = getattr(source_box, 'position', None)
        cat_position = cat.position
        if not isinstance(source_position, SpatialVector3):
            return self._record({'name': 'cat_quantum_box_travel_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'counterpart_box_id': counterpart_box_id, 'reason': 'missing_position', 'executed': False})
        if not self._same_position(cat_position, source_position):
            return self._record({'name': 'cat_quantum_box_travel_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'counterpart_box_id': counterpart_box_id, 'reason': 'cat_not_at_source_box', 'executed': False})
        transfer_system = getattr(self.universe, 'cat_box_transfer', None)
        if transfer_system is None:
            return self._record({'name': 'cat_quantum_box_travel_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'counterpart_box_id': counterpart_box_id, 'reason': 'cat_box_tranfer_unavaible', 'executed': False})
        result = transfer_system.transfer_cat(cat=cat, source_box_id=source_box_id, target_box_id=counterpart_box_id)

        if not isinstance(
            result,
            CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES,
        ):
            raise TypeError(
                "Cat quantum box transfer must "
                "return a transfer result object."
            )

        transferred = result.transferred
        event = {'name': 'cat_traveled_through_known_quantum_box' if transferred else 'cat_quantum_box_travel_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'counterpart_box_id': counterpart_box_id, 'source_layer': target.source_layer, 'transfer': deepcopy(result), 'decision_source': 'cat_mind', 'executed': transferred}
        mind = cat.mind
        mind.previous_intention = deepcopy(intention)
        mind.current_intention = None
        if transferred:
            mind.active_body_execution = deepcopy(event)
            cat.current_quantum_counterpart_observation = None
            return self._record(event)
        failure_reason = getattr(result, 'reason', 'quantum_transfer_failed')
        cronenberg = self.universe.create_cronenberg_from_quantum_error(error=RuntimeError(f'Cat quantum box transfer failed: {failure_reason}'), source_component='cat_intention_executor', source_operation='quantum_box_travel_failed')
        memory = cat.memory.remember(event_type='quantum_box_layer_transfer_failed', universe_tick=self.universe.quantum_state.tick_count, location=(None if cat.position is None else cat.position.to_dict()), participants=[source_box_id, counterpart_box_id], details={'source_layer': target.source_layer, 'target_layer': target.target_layer, 'reason': failure_reason, 'cronenberg_id': cronenberg.id})
        event['reason'] = failure_reason
        event['cronenberg_id'] = cronenberg.id
        event['memory'] = deepcopy(memory)
        mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def sense(self, cat, intention):
        target = intention.target

        if not isinstance(
            target,
            CatQuantumCounterpartSenseTarget,
        ):
            return self._record({
                'name': (
                    'cat_quantum_counterpart_sensing_failed'
                ),
                'cat': cat.name,
                'reason': (
                    'invalid_quantum_counterpart_sense_target'
                ),
                'executed': False,
            })

        source_box_id = target.box_id
        if source_box_id is None:
            return self._record({'name': 'cat_quantum_counterpart_sensing_failed', 'cat': cat.name, 'reason': 'missing_box_id', 'executed': False})
        source_box = next((box for box in getattr(self.universe, 'quantum_boxes', []) if getattr(box, 'id', None) == source_box_id), None)
        if source_box is None:
            return self._record({'name': 'cat_quantum_counterpart_sensing_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'reason': 'source_box_no_longer_exists', 'executed': False})
        if getattr(source_box, 'current_layer', None) != cat.current_layer:
            return self._record({'name': 'cat_quantum_counterpart_sensing_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'reason': 'source_box_not_in_cat_layer', 'executed': False})
        source_position = getattr(source_box, 'position', None)
        if not isinstance(source_position, SpatialVector3):
            return self._record({'name': 'cat_quantum_counterpart_sensing_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'reason': 'cat_not_at_source_box', 'executed': False})
        if not self._same_position(cat.position, source_position):
            return self._record({'name': 'cat_quantum_counterpart_sensing_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'reason': 'cat_not_at_source_box', 'executed': False})
        pairing = getattr(source_box, 'quantum_counterpart', None)
        if pairing is None or not pairing.paired:
            return self._record({'name': 'cat_quantum_counterpart_sensing_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'reason': 'pair_no_longer_exists', 'executed': False})
        counterpart_id = pairing.box_id
        counterpart = next((box for box in getattr(self.universe, 'quantum_boxes', []) if getattr(box, 'id', None) == counterpart_id), None)
        if counterpart is None:
            return self._record({'name': 'cat_quantum_counterpart_sensing_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'reason': 'counterpart_no_longer_exists', 'executed': False})
        reverse_pairing = getattr(counterpart, 'quantum_counterpart', None)
        if reverse_pairing is None or not reverse_pairing.paired or reverse_pairing.box_id != source_box_id:
            return self._record({'name': 'cat_quantum_counterpart_sensing_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'reason': 'pair_not_reciprocal', 'executed': False})
        observation = (
            CatQuantumCounterpartObservation(
                source_box_id=source_box_id,
                counterpart_box_id=counterpart.id,
                source_layer=getattr(
                    source_box,
                    'current_layer',
                    None,
                ),
                counterpart_layer=getattr(
                    counterpart,
                    'current_layer',
                    None,
                ),
                counterpart_position=(
                    counterpart.position
                    if isinstance(
                        getattr(counterpart, 'position', None),
                        SpatialVector3,
                    )
                    else None
                ),
                observed_tick=getattr(
                    self.universe,
                    'universe_tick',
                    None,
                ),
                temporary=True,
                pair_currently_valid=True,
            )
        )
        cat.current_quantum_counterpart_observation = observation
        mind = cat.mind
        mind.previous_intention = deepcopy(intention)
        mind.current_intention = None
        event = {
            'name': (
                'cat_sensed_quantum_counterpart'
            ),
            'cat': cat.name,
            'observation': {
                'source_box_id': (
                    observation.source_box_id
                ),
                'counterpart_box_id': (
                    observation.counterpart_box_id
                ),
                'source_layer': (
                    observation.source_layer
                ),
                'counterpart_layer': (
                    observation.counterpart_layer
                ),
                'counterpart_position': (
                    None
                    if observation.counterpart_position
                    is None
                    else (
                        observation
                        .counterpart_position
                        .to_dict()
                    )
                ),
                'observed_tick': (
                    observation.observed_tick
                ),
                'temporary': (
                    observation.temporary
                ),
                'pair_currently_valid': (
                    observation
                    .pair_currently_valid
                ),
            },
            'decision_source': 'cat_mind',
            'executed': True,
        }
        mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def explore(self, cat, intention, cronenbergs=None, step_size=None):
        target = intention.target

        if not isinstance(
            target,
            CatExploreBoxTarget,
        ):
            return self._record({
                'name': (
                    'cat_box_exploration_failed'
                ),
                'cat': cat.name,
                'reason': (
                    'invalid_explore_box_target'
                ),
                'executed': False,
            })

        box_id = target.box_id
        if box_id is None:
            return self._record({'name': 'cat_box_exploration_failed', 'cat': cat.name, 'reason': 'missing_box_id', 'executed': False})
        box = next((candidate for candidate in getattr(self.universe, 'quantum_boxes', []) if getattr(candidate, 'id', None) == box_id), None)
        if box is None:
            return self._record({'name': 'cat_box_exploration_failed', 'cat': cat.name, 'box_id': box_id, 'reason': 'box_not_found', 'executed': False})
        if getattr(box, 'current_layer', None) != (cat.current_layer or 'quantum_layer'):
            return self._record({'name': 'cat_box_exploration_failed', 'cat': cat.name, 'box_id': box_id, 'reason': 'box_not_in_cat_layer', 'executed': False})
        exploration = cat.box_exploration

        if (
            exploration is not None
            and not isinstance(
                exploration,
                CatBoxExplorationState,
            )
        ):
            raise TypeError(
                'Cat box exploration state '
                'must be '
                'CatBoxExplorationState.'
            )

        if (
            exploration is not None
            and exploration.active
            and exploration.box_id == box_id
        ):
            return self._advance_box_exploration(
                cat=cat,
                intention=intention,
                cronenbergs=cronenbergs,
            )
        cat_position = cat.position
        box_position = getattr(box, 'position', None)
        if not isinstance(cat_position, SpatialVector3):
            return self._record({'name': 'cat_box_exploration_failed', 'cat': cat.name, 'box_id': box_id, 'reason': 'cat_position_missing', 'executed': False})
        if not isinstance(box_position, SpatialVector3):
            return self._record({'name': 'cat_box_exploration_failed', 'cat': cat.name, 'box_id': box_id, 'reason': 'box_position_missing', 'executed': False})
        if self._same_position(cat_position, box_position):
            return self._finish_box_exploration(cat=cat, intention=intention, box=box)
        quantum_space = getattr(self.universe, 'quantum_space', None)
        if quantum_space is None:
            return self._record({'name': 'cat_box_exploration_failed', 'cat': cat.name, 'box_id': box_id, 'reason': 'quantum_space_unavailable', 'executed': False})
        planned = quantum_space.plan_direct_cat_route(cat_id=cat.name, start_position=cat_position, destination_position=box_position, destination=f'explore_box:{box_id}', step_size=step_size)
        route = planned.route
        route.state = QuantumCatRouteState.READY
        cat.active_route_id = route.route_id
        cat.box_exploration = (
            CatBoxExplorationState(
                active=True,
                arrived=False,
                box_id=box_id,
                route_id=route.route_id,
                destination=box_position,
                observed=False,
            )
        )
        event = {'name': 'cat_approaching_box_to_explore', 'cat': cat.name, 'box_id': box_id, 'route_id': route.route_id, 'destination': box_position.to_dict(), 'arrived': False, 'decision_source': 'cat_mind', 'executed': True}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _advance_box_exploration(self, cat, intention, cronenbergs=None):
        exploration = cat.box_exploration

        if not isinstance(
            exploration,
            CatBoxExplorationState,
        ):
            raise TypeError(
                'Cat box exploration state '
                'must be '
                'CatBoxExplorationState.'
            )

        result = self.universe.quantum_space.advance_cat_route(cat=cat, cronenbergs=cronenbergs if cronenbergs is not None else getattr(self.universe, 'cronenbergs', []), encounter_system=self.universe.cat_cronenberg_encounter, universe=self.universe)
        if not isinstance(
            result,
            QUANTUM_CAT_ROUTE_ADVANCE_RESULT_TYPES,
        ):
            raise TypeError(
                "Quantum cat route advancement "
                "must return a route result object."
            )

        position = (
            None
            if result.position is None
            else result.position.to_dict()
        )
        if result.arrived:
            box = next((candidate for candidate in getattr(self.universe, 'quantum_boxes', []) if getattr(candidate, 'id', None) == exploration.box_id), None)
            if box is None:
                return self._record({'name': 'cat_box_exploration_failed', 'cat': cat.name, 'reason': 'box_disappeared', 'executed': False})
            return self._finish_box_exploration(cat=cat, intention=intention, box=box)
        event = {'name': 'cat_approaching_box_to_explore', 'cat': cat.name, 'box_id': exploration.box_id, 'route_id': exploration.route_id, 'position': position, 'destination': (None if exploration.destination is None else exploration.destination.to_dict()), 'arrived': False, 'decision_source': 'cat_mind', 'executed': result.result != 'no_active_route'}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _finish_box_exploration(self, cat, intention, box):
        box_id = getattr(box, 'id', None)
        cat_observation = getattr(
            box,
            "cat_observation_state",
            None,
        )

        if not callable(
            cat_observation
        ):
            raise TypeError(
                "Quantum box exploration requires "
                "cat_observation_state()."
            )

        observation = cat_observation(
            cat
        )

        if not isinstance(
            observation,
            QuantumBoxCatObservation,
        ):
            raise TypeError(
                "Quantum box exploration "
                "observation must use "
                "QuantumBoxCatObservation."
            )
        memory = cat.memory
        remembered = None
        if memory is not None:
            remembered = memory.remember(event_type='quantum_box_observed', universe_tick=getattr(self.universe, 'universe_tick', None), location=cat.current_layer, participants=[box_id], details={'box_id': box_id, 'position': (None if getattr(box, 'position', None) is None else box.position.to_dict()), 'observation': deepcopy(observation)})
        exploration = cat.box_exploration

        if exploration is None:
            exploration = (
                CatBoxExplorationState()
            )
            cat.box_exploration = exploration
        elif not isinstance(
            exploration,
            CatBoxExplorationState,
        ):
            raise TypeError(
                'Cat box exploration state '
                'must be '
                'CatBoxExplorationState.'
            )

        exploration.active = False
        exploration.arrived = True
        exploration.box_id = box_id
        exploration.observed = True
        if hasattr(cat, 'active_route_id'):
            del cat.active_route_id
        mind = cat.mind
        mind.previous_intention = deepcopy(intention)
        mind.current_intention = None
        event = {'name': 'cat_explored_quantum_box', 'cat': cat.name, 'box_id': box_id, 'position': (None if getattr(box, 'position', None) is None else box.position.to_dict()), 'observation': deepcopy(observation), 'memory': deepcopy(remembered), 'arrived': True, 'decision_source': 'cat_mind', 'executed': True}
        mind.active_body_execution = deepcopy(event)
        return self._record(event)
