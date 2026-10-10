from copy import deepcopy
from core.entity.components import SpatialVector3
from core.entity.quantum_cat_route_state import (
    QuantumCatRouteState,
)
from core.entity.quantum_box_cat_observation import (
    QuantumBoxCatObservation,
)

from cats.cat_quantum_observation_state import (
    CatQuantumCounterpartObservation,
)
from cats.cat_knowledge import CatKnowledge
from cats.cat import Cat
from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatQuantumBoxTravelTarget,
)
from cats.cat_social_system import CatSocialSystem
from universe.quantum_cat_route_advance_state import (
    QUANTUM_CAT_ROUTE_ADVANCE_RESULT_TYPES,
)
from quantum.cat_stable_exploration_pair_result_state import (
    CAT_STABLE_EXPLORATION_PAIR_CREATION_RESULT_TYPES,
    CatStableExplorationPairCreatedResult,
)
from cats.cat_exploration_pair_execution_result_state import (
    CatAutonomousExplorationPairStartedEvent,
    CatExplorationPairCreationFailedResult,
    CatExplorationPairTransferFailedResult,
)
from quantum.cat_box_transfer_result_state import (
    CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES,
)
from cats.cat_basic_intention_result_state import (
    CatIntentionBodyActionDeferredEvent,
    CatRestStartedEvent,
    CatWanderedEvent,
    CatWanderFailedResult,
)


from cats.cat_intention_state import CatQuantumCounterpartSenseTarget

from cats.cat_intention_state import CatExploreBoxTarget

from cats.cat_box_exploration_state import CatBoxExplorationState

from cats.cat_intention_state import CatExplorationPairTarget

from cats.cat_intention_state import CatVisitRecipientTarget

from cats.cat_intention_state import CatApproachCatTarget

from cats.cat_intention_state import CatShareLegendTarget
from cats.cat_scent_box_intention_handler import (
    CatScentBoxIntentionHandler,
)
from cats.cat_scent_search_intention_handler import (
    CatScentSearchIntentionHandler,
)
from cats.cat_known_scent_intention_handler import (
    CatKnownScentIntentionHandler,
)
from cats.cat_intention_navigation_result_state import (
    CatIntentionNavigationFailedResult,
    CatIntentionNavigationStartedEvent,
)
from cats.cat_navigation_result_state import (
    CatNavigationNotOfferedResult,
    CatNavigationOfferedEvent,
    CatNavigationOfferAcceptedEvent,
    CatNavigationOfferNotAcceptedResult,
)

class CatIntentionExecutor:
    NAVIGATION_INTENTS = {'visit_bar': 'return_to_bar', 'visit_recipient': 'follow_entity', 'hunt_cronenberg': 'hunt_nearest_cronenberg', 'track_cronenberg_scent': 'hunt_nearest_cronenberg', 'avoid_cronenberg_scent': 'return_to_bar'}
    DEFERRED_INTENTS = {'observe': 'cat_observation_body_system'}

    def __init__(self, cats_layer):
        self.cats_layer = cats_layer
        self.universe = cats_layer.universe
        self.history = []
        self.social_system = CatSocialSystem(cats_layer)
        self.scent_box_intentions = (
            CatScentBoxIntentionHandler(
                universe=self.universe,
                recorder=self._record,
                same_position=self._same_position,
            )
        )

        self.scent_search_intentions = (
            CatScentSearchIntentionHandler(
                universe=self.universe,
                recorder=self._record,
            )
        )

        self.known_scent_intentions = (
            CatKnownScentIntentionHandler(
                universe=self.universe,
                recorder=self._record,
            )
        )

    def execute_current_intention(self, cat, cronenbergs=None, step_size=None):
        if not isinstance(cat, Cat):
            return self._record({'name': 'cat_intention_execution_failed', 'reason': 'invalid_cat', 'executed': False})
        if cat.type != 'cat':
            return self._record({'name': 'cat_intention_execution_failed', 'cat': cat.name, 'reason': 'entity_is_not_cat', 'executed': False})
        mind = cat.mind
        intention = getattr(mind, 'current_intention', None)
        if not intention:
            return self._record({'name': 'cat_intention_execution_skipped', 'cat': cat.name, 'reason': 'no_current_intention', 'executed': False})

        if not isinstance(
            intention,
            CatIntentionCandidate,
        ):
            raise TypeError(
                "Cat current intention must be "
                "CatIntentionCandidate."
            )

        intention_type = intention.type
        if intention_type in self.NAVIGATION_INTENTS:
            return self._execute_navigation(cat=cat, intention=intention, cronenbergs=cronenbergs, step_size=step_size)
        if intention_type == 'wander':
            return self._execute_wander(cat=cat, intention=intention, step_size=step_size)
        if intention_type == 'rest':
            return self._execute_rest(cat=cat, intention=intention)
        if intention_type == 'follow_scent_through_box':
            return self.scent_box_intentions.execute(cat=cat, intention=intention, cronenbergs=cronenbergs, step_size=step_size)
        if intention_type == 'sense_quantum_counterpart':
            return self._execute_sense_quantum_counterpart(cat=cat, intention=intention)
        if intention_type == 'travel_through_known_quantum_box':
            return self._execute_travel_through_known_quantum_box(cat=cat, intention=intention)
        if intention_type == 'explore_box':
            return self._execute_explore_box(cat=cat, intention=intention, cronenbergs=cronenbergs, step_size=step_size)
        if intention_type == 'search_for_scent':
            return self.scent_search_intentions.execute(cat=cat, intention=intention, cronenbergs=cronenbergs, step_size=step_size)
        if intention_type == 'follow_known_scent':
            return self.known_scent_intentions.execute(cat=cat, intention=intention, cronenbergs=cronenbergs, step_size=step_size)
        if intention_type == 'share_legend':
            return self._execute_share_legend(cat=cat, intention=intention)
        if intention_type == 'create_exploration_pair':
            return self._execute_exploration_pair_creation(cat=cat, intention=intention)
        if intention_type == 'approach_cat':
            return self._execute_approach_cat(cat=cat, intention=intention, step_size=step_size)
        if intention_type in self.DEFERRED_INTENTS:
            return self._defer_intention(cat=cat, intention=intention)
        return self._record({'name': 'cat_intention_execution_failed', 'cat': cat.name, 'intention': intention_type, 'reason': 'unsupported_intention', 'executed': False})

    def _execute_navigation(
        self,
        cat,
        intention,
        cronenbergs,
        step_size,
    ):
        intention_type = (
            intention.type
        )

        body_intent = (
            self.NAVIGATION_INTENTS[
                intention_type
            ]
        )

        if (
            intention_type
            == "visit_recipient"
        ):
            target = (
                intention.target
            )

            if not isinstance(
                target,
                CatVisitRecipientTarget,
            ):
                return self._record(
                    CatIntentionNavigationFailedResult(
                        cat=cat.name,
                        intention=
                            intention_type,
                        body_intent=
                            body_intent,
                        reason=(
                            "invalid_visit_recipient_target"
                        ),
                    )
                )

            if target.recipient_id is None:
                return self._record(
                    CatIntentionNavigationFailedResult(
                        cat=cat.name,
                        intention=
                            intention_type,
                        body_intent=
                            body_intent,
                        reason=(
                            "missing_recipient_id"
                        ),
                    )
                )

            cat.navigation_target = (
                target.recipient_id
            )

        previous_suggestion = (
            cat.suggested_intent
        )

        cat.suggested_intent = (
            body_intent
        )

        offer = (
            self.cats_layer
            .offer_navigation_for_suggested_intent(
                cat=cat,
                cronenbergs=
                    cronenbergs,
                step_size=
                    step_size,
            )
        )

        if isinstance(
            offer,
            CatNavigationNotOfferedResult,
        ):
            return self._record(
                CatIntentionNavigationFailedResult(
                    cat=cat.name,
                    intention=
                        intention_type,
                    body_intent=
                        body_intent,
                    reason=offer.reason,
                    navigation_offer=
                        offer,
                    previous_suggested_intent=
                        previous_suggestion,
                )
            )

        if not isinstance(
            offer,
            CatNavigationOfferedEvent,
        ):
            raise TypeError(
                "Cat navigation offer must "
                "return a navigation result object."
            )

        acceptance = (
            self.cats_layer
            .accept_navigation_offer(
                cat
            )
        )

        if isinstance(
            acceptance,
            CatNavigationOfferNotAcceptedResult,
        ):
            return self._record(
                CatIntentionNavigationFailedResult(
                    cat=cat.name,
                    intention=
                        intention_type,
                    body_intent=
                        body_intent,
                    reason=
                        acceptance.reason,
                    navigation_offer=
                        offer,
                    acceptance=
                        acceptance,
                    previous_suggested_intent=
                        previous_suggestion,
                )
            )

        if not isinstance(
            acceptance,
            CatNavigationOfferAcceptedEvent,
        ):
            raise TypeError(
                "Cat navigation acceptance must "
                "return a navigation result object."
            )

        cat.state = (
            "acting_on_own_intention"
        )

        event = (
            CatIntentionNavigationStartedEvent(
                cat=cat.name,
                intention=
                    intention_type,
                body_intent=
                    body_intent,
                target=
                    intention.target,
                route_id=
                    acceptance.route_id,
                destination=
                    acceptance.destination,
                navigation_offer=
                    offer,
                acceptance=
                    acceptance,
            )
        )

        mind = (
            cat.mind
        )

        mind.active_body_execution = (
            deepcopy(
                event
            )
        )

        return self._record(
            event
        )





    @staticmethod
    def _same_position(first, second, tolerance=1e-09):
        if not isinstance(first, SpatialVector3):
            return False
        if not isinstance(second, SpatialVector3):
            return False
        return first.is_close_to(second, tolerance=tolerance)

    def _execute_travel_through_known_quantum_box(self, cat, intention):
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

    def _execute_sense_quantum_counterpart(self, cat, intention):
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

    def _execute_explore_box(self, cat, intention, cronenbergs=None, step_size=None):
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







    def _execute_share_legend(self, cat, intention):
        target = intention.target

        if not isinstance(
            target,
            CatShareLegendTarget,
        ):
            return self._record({
                'name': (
                    'cat_legend_not_shared'
                ),
                'cat': cat.name,
                'reason': (
                    'invalid_share_legend_target'
                ),
                'executed': False,
            })

        target_name = (
            target.listener_name
        )
        listener = next(
            (
                candidate
                for candidate
                in self.cats_layer.cats
                if (
                    isinstance(
                        candidate,
                        Cat,
                    )
                    and candidate is not cat
                    and candidate.name
                    == target_name
                )
            ),
            None,
        )
        if listener is None:
            return self._record({'name': 'cat_legend_not_shared', 'cat': cat.name, 'listener': target_name, 'reason': 'listener_not_found', 'executed': False})
        result = CatKnowledge.share_legend(storyteller=cat, listener=listener, universe=self.universe)
        mind = cat.mind
        mind.previous_intention = deepcopy(intention)
        mind.current_intention = None
        event = {**result, 'cat': cat.name, 'intention': 'share_legend', 'decision_source': 'cat_mind', 'executed': True}
        mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _execute_exploration_pair_creation(
        self,
        cat,
        intention,
    ):
        target = intention.target

        if not isinstance(
            target,
            CatExplorationPairTarget,
        ):
            return self._record(
                CatExplorationPairCreationFailedResult(
                    cat=cat.name,
                    reason=(
                        "invalid_exploration_pair_target"
                    ),
                )
            )

        destination_layer = (
            target.layer
        )

        destination_position = (
            target.position
        )

        if (
            destination_layer is None
            or destination_position is None
        ):
            return self._record(
                CatExplorationPairCreationFailedResult(
                    cat=cat.name,
                    reason=(
                        "missing_exploration_destination"
                    ),
                )
            )

        transfer_system = getattr(
            self.universe,
            "cat_box_transfer",
            None,
        )

        if transfer_system is None:
            return self._record(
                CatExplorationPairCreationFailedResult(
                    cat=cat.name,
                    reason=(
                        "cat_box_transfer_unavailable"
                    ),
                )
            )

        creation = (
            transfer_system
            .create_exploration_pair(
                cat=cat,
                destination_layer=
                    destination_layer,
                destination_position=
                    destination_position,
            )
        )

        if not isinstance(
            creation,
            CAT_STABLE_EXPLORATION_PAIR_CREATION_RESULT_TYPES,
        ):
            raise TypeError(
                "Stable exploration pair creation "
                "must return a creation result object."
            )

        if not creation.created:
            return self._record(
                CatExplorationPairCreationFailedResult(
                    cat=cat.name,
                    reason=creation.reason,
                    creation_result=creation,
                )
            )

        if not isinstance(
            creation,
            CatStableExplorationPairCreatedResult,
        ):
            raise TypeError(
                "Successful stable pair creation "
                "must return "
                "CatStableExplorationPairCreatedResult."
            )

        source_box = (
            creation.source_box
        )

        target_box = (
            creation.target_box
        )

        transfer = (
            transfer_system.transfer_cat(
                cat=cat,
                source_box_id=
                    source_box.id,
                target_box_id=
                    target_box.id,
            )
        )

        if not isinstance(
            transfer,
            CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES,
        ):
            raise TypeError(
                "Cat quantum box transfer must "
                "return a transfer result object."
            )

        if not transfer.transferred:
            cat.state = (
                "exploration_pair_created_"
                "but_transfer_failed"
            )

            return self._record(
                CatExplorationPairTransferFailedResult(
                    cat=cat.name,
                    pair_id=
                        creation.pair_id,
                    source_box_id=
                        source_box.id,
                    target_box_id=
                        target_box.id,
                    reason=getattr(
                        transfer,
                        "reason",
                        "stable_pair_transfer_failed",
                    ),
                    transfer_result=
                        transfer,
                    pair_preserved=True,
                )
            )

        exploration_route = None

        if (
            cat.current_layer
            == "quantum_layer"
        ):
            exploration_route = (
                transfer_system
                .start_quantum_exploration_route(
                    cat=cat,
                    pair_id=
                        creation.pair_id,
                )
            )

        mind = cat.mind

        mind.previous_intention = (
            deepcopy(
                intention
            )
        )

        mind.current_intention = None

        event = (
            CatAutonomousExplorationPairStartedEvent(
                cat=cat.name,
                pair_id=
                    creation.pair_id,
                source_box_id=
                    source_box.id,
                target_box_id=
                    target_box.id,
                source_layer=
                    creation.source_layer,
                target_layer=
                    creation.target_layer,
                energy_cost_j=
                    creation.energy_cost_j,
                remaining_cat_energy=(
                    creation
                    .remaining_cat_energy
                ),
                transfer=transfer,
                exploration_route=
                    exploration_route,
            )
        )

        mind.active_body_execution = (
            deepcopy(
                event
            )
        )

        return self._record(
            event
        )

    def _execute_wander(
        self,
        cat,
        intention,
        step_size=None,
    ):
        position = cat.position

        if not isinstance(
            position,
            SpatialVector3,
        ):
            return self._record(
                CatWanderFailedResult(
                    cat=cat.name,
                    reason="missing_position",
                )
            )

        step = (
            1.0
            if step_size is None
            else max(
                0.0,
                float(step_size),
            )
        )

        phase = (
            int(
                getattr(
                    cat.needs,
                    "tick",
                    0,
                )
            )
            + sum(
                ord(character)
                for character
                in cat.name
            )
        )

        axis = (
            "x"
            if phase % 2 == 0
            else "y"
        )

        direction = (
            1.0
            if (
                phase // 2
            )
            % 2
            == 0
            else -1.0
        )

        previous = position
        delta = direction * step

        destination = (
            position.translated(
                dx=(
                    delta
                    if axis == "x"
                    else 0.0
                ),
                dy=(
                    delta
                    if axis == "y"
                    else 0.0
                ),
            )
        )

        cat.move_to(
            destination
        )

        cat.state = (
            "wandering_by_own_choice"
        )

        event = (
            CatWanderedEvent(
                cat=cat.name,
                from_position=
                    previous,
                position=
                    destination,
                axis=axis,
                step=delta,
            )
        )

        cat.mind.active_body_execution = (
            deepcopy(
                event
            )
        )

        return self._record(
            event
        )

    def _execute_rest(
        self,
        cat,
        intention,
    ):
        previous_state = (
            cat.state
        )

        cat.state = (
            "resting_by_own_choice"
        )

        cat.suggested_intent = None

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
            CatRestStartedEvent(
                cat=cat.name,
                previous_state=
                    previous_state,
                state=cat.state,
            )
        )

        cat.mind.active_body_execution = (
            deepcopy(
                event
            )
        )

        return self._record(
            event
        )

    def _execute_approach_cat(self, cat, intention, step_size=None):
        target = intention.target

        if not isinstance(
            target,
            CatApproachCatTarget,
        ):
            return self._record({
                'name': 'cat_approach_failed',
                'cat': cat.name,
                'reason': (
                    'invalid_approach_cat_target'
                ),
                'executed': False,
            })

        target_name = target.cat_name
        if not target_name:
            return self._record({'name': 'cat_approach_failed', 'cat': cat.name, 'reason': 'missing_target_cat', 'executed': False})
        target_cat = next((candidate for candidate in self.cats_layer.cats if isinstance(candidate, Cat) and candidate is not cat and (candidate.name == target_name)), None)
        if target_cat is None:
            return self._record({'name': 'cat_approach_failed', 'cat': cat.name, 'target': target_name, 'reason': 'target_cat_not_found', 'executed': False})
        if target_cat.current_layer != cat.current_layer:
            return self._record({'name': 'cat_approach_failed', 'cat': cat.name, 'target': target_name, 'reason': 'target_cat_in_other_layer', 'cat_layer': cat.current_layer, 'target_layer': target_cat.current_layer, 'executed': False})
        cat_position = cat.position
        target_position = target_cat.position
        if not isinstance(cat_position, SpatialVector3) or not isinstance(target_position, SpatialVector3):
            return self._record({'name': 'cat_approach_failed', 'cat': cat.name, 'target': target_name, 'reason': 'missing_position', 'executed': False})
        if self._same_position(cat_position, target_position):
            cat.state = 'near_target_cat'
            social_event = self.social_system.meet(cat, target_cat)
            event = {'name': 'cat_approach_completed', 'cat': cat.name, 'target': target_name, 'position': cat_position.to_dict(), 'arrived': True, 'decision_source': 'cat_mind', 'social': deepcopy(social_event), 'executed': True}
            cat.mind.active_body_execution = deepcopy(event)
            return self._record(event)
        quantum_space = getattr(self.universe, 'quantum_space', None)
        if quantum_space is None:
            self.universe.enable_quantum_layer()
            quantum_space = getattr(self.universe, 'quantum_space', None)
        if quantum_space is None:
            return self._record({'name': 'cat_approach_failed', 'cat': cat.name, 'target': target_name, 'reason': 'quantum_space_unavailable', 'executed': False})
        planned = quantum_space.plan_direct_cat_route(cat_id=cat.name, start_position=cat_position, destination_position=target_position, destination=f'cat:{target_name}', step_size=step_size)
        route = planned.route
        route.state = QuantumCatRouteState.READY
        cat.active_route_id = route.route_id
        cat.navigation_target = target_name
        cat.state = 'approaching_cat'
        event = {'name': 'cat_approach_started', 'cat': cat.name, 'target': target_name, 'route_id': route.route_id, 'destination': target_position.to_dict(), 'arrived': False, 'decision_source': 'cat_mind', 'executed': True}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _defer_intention(
        self,
        cat,
        intention,
    ):
        intention_type = (
            intention.type
        )

        required_system = (
            self.DEFERRED_INTENTS[
                intention_type
            ]
        )

        cat.state = (
            "intention_waiting_for_body_system"
        )

        event = (
            CatIntentionBodyActionDeferredEvent(
                cat=cat.name,
                intention=
                    intention_type,
                target=deepcopy(
                    intention.target
                ),
                required_system=
                    required_system,
            )
        )

        cat.mind.active_body_execution = (
            deepcopy(
                event
            )
        )

        return self._record(
            event
        )

    def _record(self, event):
        stored = deepcopy(event)
        self.history.append(stored)
        quantum_events = getattr(self.universe, 'quantum_events', None)
        if quantum_events is not None:
            quantum_events.append(deepcopy(stored))
        emit_event = getattr(self.cats_layer, 'emit_event', None)
        if emit_event is not None:
            emit_event(deepcopy(stored))
        return event
