from copy import deepcopy

from cats.cat_quantum_observation_state import (
    CatQuantumCounterpartObservation,
)
from cats.cat_knowledge import CatKnowledge
from cats.cat_olfaction import CatOlfaction
from cats.cat import Cat
from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatKnownScentTarget,
    CatScentSearchTarget,
    CatScentBoxTarget,
    CatQuantumBoxTravelTarget,
)
from cats.cat_scent_direction_state import (
    CatScentTrailDirection,
)
from cats.cat_scent_navigation_state import (
    CatKnownScentFollowState,
    CatScentSearchState,
    CatScentBoxFollowState,
)
from cats.cat_social_system import CatSocialSystem

from cats.cat_intention_state import CatQuantumBoxTravelTarget

from cats.cat_intention_state import CatQuantumCounterpartSenseTarget

from cats.cat_intention_state import CatExploreBoxTarget

from cats.cat_box_exploration_state import CatBoxExplorationState

from cats.cat_intention_state import CatExplorationPairTarget

from cats.cat_intention_state import CatVisitRecipientTarget

from cats.cat_intention_state import CatApproachCatTarget

class CatIntentionExecutor:
    NAVIGATION_INTENTS = {'visit_bar': 'return_to_bar', 'visit_recipient': 'follow_entity', 'hunt_cronenberg': 'hunt_nearest_cronenberg', 'track_cronenberg_scent': 'hunt_nearest_cronenberg', 'avoid_cronenberg_scent': 'return_to_bar'}
    DEFERRED_INTENTS = {'observe': 'cat_observation_body_system'}

    def __init__(self, cats_layer):
        self.cats_layer = cats_layer
        self.universe = cats_layer.universe
        self.history = []
        self.social_system = CatSocialSystem(cats_layer)

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
            return self._execute_follow_scent_through_box(cat=cat, intention=intention, cronenbergs=cronenbergs, step_size=step_size)
        if intention_type == 'sense_quantum_counterpart':
            return self._execute_sense_quantum_counterpart(cat=cat, intention=intention)
        if intention_type == 'travel_through_known_quantum_box':
            return self._execute_travel_through_known_quantum_box(cat=cat, intention=intention)
        if intention_type == 'explore_box':
            return self._execute_explore_box(cat=cat, intention=intention, cronenbergs=cronenbergs, step_size=step_size)
        if intention_type == 'search_for_scent':
            return self._execute_search_for_scent(cat=cat, intention=intention, cronenbergs=cronenbergs, step_size=step_size)
        if intention_type == 'follow_known_scent':
            return self._execute_follow_known_scent(cat=cat, intention=intention, cronenbergs=cronenbergs, step_size=step_size)
        if intention_type == 'share_legend':
            return self._execute_share_legend(cat=cat, intention=intention)
        if intention_type == 'create_exploration_pair':
            return self._execute_exploration_pair_creation(cat=cat, intention=intention)
        if intention_type == 'approach_cat':
            return self._execute_approach_cat(cat=cat, intention=intention, step_size=step_size)
        if intention_type in self.DEFERRED_INTENTS:
            return self._defer_intention(cat=cat, intention=intention)
        return self._record({'name': 'cat_intention_execution_failed', 'cat': cat.name, 'intention': intention_type, 'reason': 'unsupported_intention', 'executed': False})

    def _execute_navigation(self, cat, intention, cronenbergs, step_size):
        intention_type = intention.type
        body_intent = self.NAVIGATION_INTENTS[intention_type]
        if intention_type == 'visit_recipient':
            target = intention.target

            if not isinstance(
                target,
                CatVisitRecipientTarget,
            ):
                return self._record({
                    'name': (
                        'cat_intention_body_action_failed'
                    ),
                    'cat': cat.name,
                    'intention': intention_type,
                    'body_intent': body_intent,
                    'reason': (
                        'invalid_visit_recipient_target'
                    ),
                    'executed': False,
                })

            if target.recipient_id is None:
                return self._record({
                    'name': (
                        'cat_intention_body_action_failed'
                    ),
                    'cat': cat.name,
                    'intention': intention_type,
                    'body_intent': body_intent,
                    'reason': (
                        'missing_recipient_id'
                    ),
                    'executed': False,
                })

            cat.navigation_target = (
                target.recipient_id
            )
        previous_suggestion = cat.suggested_intent
        cat.suggested_intent = body_intent
        offer = self.cats_layer.offer_navigation_for_suggested_intent(cat=cat, cronenbergs=cronenbergs, step_size=step_size)
        if not offer.get('offered', False):
            event = {'name': 'cat_intention_body_action_failed', 'cat': cat.name, 'intention': intention_type, 'body_intent': body_intent, 'reason': offer.get('result', 'navigation_not_offered'), 'navigation_offer': offer, 'previous_suggested_intent': previous_suggestion, 'executed': False}
            return self._record(event)
        acceptance = self.cats_layer.accept_navigation_offer(cat)
        if not acceptance.get('accepted', False):
            return self._record({'name': 'cat_intention_body_action_failed', 'cat': cat.name, 'intention': intention_type, 'body_intent': body_intent, 'reason': acceptance.get('result', 'navigation_not_accepted'), 'navigation_offer': offer, 'acceptance': acceptance, 'executed': False})
        cat.state = 'acting_on_own_intention'
        event = {'name': 'cat_intention_navigation_started', 'cat': cat.name, 'intention': intention_type, 'body_intent': body_intent, 'target': intention.target, 'route_id': acceptance.get('route_id'), 'destination': acceptance.get('destination'), 'decision_source': 'cat_mind', 'navigation_offer': {key: value for key, value in offer.items() if key not in {'route', 'plan'}}, 'executed': True}
        mind = cat.mind
        mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _execute_follow_scent_through_box(self, cat, intention, cronenbergs=None, step_size=None):
        target = intention.target

        if not isinstance(
            target,
            CatScentBoxTarget,
        ):
            return self._record({
                'name': (
                    'cat_scent_box_transfer_failed'
                ),
                'cat': cat.name,
                'reason': (
                    'invalid_scent_box_target'
                ),
                'executed': False,
            })

        source_box_id = target.box_id
        target_box_id = (
            target.counterpart_box_id
        )
        if source_box_id is None or target_box_id is None:
            return self._record({'name': 'cat_scent_box_transfer_failed', 'cat': cat.name, 'reason': 'missing_box_pair', 'executed': False})
        transfer_system = getattr(self.universe, 'cat_box_transfer', None)
        if transfer_system is None:
            return self._record({'name': 'cat_scent_box_transfer_failed', 'cat': cat.name, 'reason': 'cat_box_transfer_unavailable', 'executed': False})
        source_box = next((box for box in getattr(self.universe, 'quantum_boxes', []) if getattr(box, 'id', None) == source_box_id), None)
        if source_box is None:
            return self._finish_scent_box_follow(cat=cat, intention=intention, event={'name': 'cat_scent_box_transfer_failed', 'cat': cat.name, 'identity': target.identity, 'source_box_id': source_box_id, 'target_box_id': target_box_id, 'reason': 'source_box_not_found', 'executed': False})
        if getattr(source_box, 'current_layer', None) != cat.current_layer:
            return self._finish_scent_box_follow(cat=cat, intention=intention, event={'name': 'cat_scent_box_transfer_failed', 'cat': cat.name, 'identity': target.identity, 'source_box_id': source_box_id, 'target_box_id': target_box_id, 'reason': 'source_box_not_in_cat_layer', 'executed': False})
        follow = cat.scent_box_follow

        if (
            follow is not None
            and not isinstance(
                follow,
                CatScentBoxFollowState,
            )
        ):
            raise TypeError(
                'Cat scent box follow state '
                'must be '
                'CatScentBoxFollowState.'
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
            return self._advance_scent_box_follow(
                cat=cat,
                intention=intention,
                cronenbergs=cronenbergs,
            )
        cat_position = cat.position
        source_position = getattr(source_box, 'position', None)
        if not isinstance(cat_position, dict) or not isinstance(source_position, dict):
            return self._record({'name': 'cat_scent_box_transfer_failed', 'cat': cat.name, 'reason': 'missing_position', 'executed': False})
        if self._same_position(cat_position, source_position):
            return self._transfer_scent_box_follow(cat=cat, intention=intention, source_box_id=source_box_id, target_box_id=target_box_id)
        quantum_space = getattr(self.universe, 'quantum_space', None)
        if quantum_space is None:
            return self._record({'name': 'cat_scent_box_transfer_failed', 'cat': cat.name, 'reason': 'quantum_space_unavailable', 'executed': False})
        planned = quantum_space.plan_direct_cat_route(cat_id=cat.name, start_position=dict(cat_position), destination_position=dict(source_position), destination=f'scent_box:{source_box_id}', step_size=step_size)
        route = planned['route']
        route.state = 'ready'
        cat.active_route_id = route.route_id
        cat.scent_box_follow = (
            CatScentBoxFollowState(
                active=True,
                arrived_at_box=False,
                route_id=route.route_id,
                source_box_id=source_box_id,
                target_box_id=target_box_id,
                identity=target.identity,
                destination=dict(
                    source_position
                ),
            )
        )
        cat.state = 'following_scent_to_quantum_box'
        event = {'name': 'cat_following_scent_to_box', 'cat': cat.name, 'identity': target.identity, 'source_box_id': source_box_id, 'target_box_id': target_box_id, 'route_id': route.route_id, 'destination': dict(source_position), 'arrived_at_box': False, 'decision_source': 'cat_mind', 'executed': True}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _advance_scent_box_follow(self, cat, intention, cronenbergs=None):
        follow = cat.scent_box_follow

        if not isinstance(
            follow,
            CatScentBoxFollowState,
        ):
            raise TypeError(
                'Cat scent box follow state '
                'must be '
                'CatScentBoxFollowState.'
            )

        result = self.universe.quantum_space.advance_cat_route(cat=cat, cronenbergs=cronenbergs if cronenbergs is not None else getattr(self.universe, 'cronenbergs', []), encounter_system=self.universe.cat_cronenberg_encounter, universe=self.universe)
        position = result.get('position')
        if position is not None:
            cat.position = dict(position)
        if result.get('arrived', False):
            follow.arrived_at_box = True
            follow.active = False
            return self._transfer_scent_box_follow(cat=cat, intention=intention, source_box_id=follow.source_box_id, target_box_id=follow.target_box_id)
        event = {'name': 'cat_following_scent_to_box', 'cat': cat.name, 'identity': follow.identity, 'source_box_id': follow.source_box_id, 'target_box_id': follow.target_box_id, 'route_id': follow.route_id, 'position': dict(position) if position is not None else None, 'route_result': result.get('result'), 'arrived_at_box': False, 'decision_source': 'cat_mind', 'executed': result.get('result') != 'no_active_route'}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _transfer_scent_box_follow(self, cat, intention, source_box_id, target_box_id):
        target = intention.target

        if not isinstance(
            target,
            CatScentBoxTarget,
        ):
            raise TypeError(
                'Scent box target must be '
                'CatScentBoxTarget.'
            )
        result = self.universe.cat_box_transfer.transfer_cat(cat=cat, source_box_id=source_box_id, target_box_id=target_box_id)
        event = {'name': 'cat_followed_scent_through_box' if result.get('transferred', False) else 'cat_scent_box_transfer_failed', 'cat': cat.name, 'identity': target.identity, 'source_box_id': source_box_id, 'target_box_id': target_box_id, 'source_layer': target.source_layer, 'target_layer': target.target_layer, 'transfer': result, 'arrived_at_box': True, 'decision_source': 'cat_mind', 'executed': result.get('transferred', False)}
        return self._finish_scent_box_follow(cat=cat, intention=intention, event=event)

    def _finish_scent_box_follow(self, cat, intention, event):
        mind = cat.mind
        mind.previous_intention = deepcopy(intention)
        mind.current_intention = None
        mind.active_body_execution = deepcopy(event)
        if hasattr(cat, 'active_route_id'):
            del cat.active_route_id
        follow = cat.scent_box_follow

        if (
            follow is not None
            and not isinstance(
                follow,
                CatScentBoxFollowState,
            )
        ):
            raise TypeError(
                'Cat scent box follow state '
                'must be '
                'CatScentBoxFollowState.'
            )

        if isinstance(
            follow,
            CatScentBoxFollowState,
        ):
            follow.active = False
        return self._record(event)

    @staticmethod
    def _same_position(first, second, tolerance=1e-09):
        return all((abs(float(first.get(axis, 0.0)) - float(second.get(axis, 0.0))) <= tolerance for axis in ('x', 'y', 'z')))

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
        cat_possition = cat.position
        if not isinstance(source_position, dict):
            return self._record({'name': 'cat_quantum_box_travel_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'counterpart_box_id': counterpart_box_id, 'reason': 'missing_position', 'executed': False})
        if not self._same_position(cat_possition, source_position):
            return self._record({'name': 'cat_quantum_box_travel_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'counterpart_box_id': counterpart_box_id, 'reason': 'cat_not_at_source_box', 'executed': False})
        transfer_system = getattr(self.universe, 'cat_box_transfer', None)
        if transfer_system is None:
            return self._record({'name': 'cat_quantum_box_travel_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'counterpart_box_id': counterpart_box_id, 'reason': 'cat_box_tranfer_unavaible', 'executed': False})
        result = transfer_system.transfer_cat(cat=cat, source_box_id=source_box_id, target_box_id=counterpart_box_id)
        transferred = result.get('transferred', False)
        event = {'name': 'cat_traveled_through_known_quantum_box' if transferred else 'cat_quantum_box_travel_failed', 'cat': cat.name, 'source_box_id': source_box_id, 'counterpart_box_id': counterpart_box_id, 'source_layer': target.source_layer, 'transfer': deepcopy(result), 'decision_source': 'cat_mind', 'executed': transferred}
        mind = cat.mind
        mind.previous_intention = deepcopy(intention)
        mind.current_intention = None
        if transferred:
            mind.active_body_execution = deepcopy(event)
            cat.current_quantum_counterpart_observation = None
            return self._record(event)
        failure_reason = result.get('reason', 'quantum_transfer_failed')
        cronenberg = self.universe.create_cronenberg_from_quantum_error(error=RuntimeError(f'Cat quantum box transfer failed: {failure_reason}'), source_component='cat_intention_executor', source_operation='quantum_box_travel_failed')
        memory = cat.memory.remember(event_type='quantum_box_layer_transfer_failed', universe_tick=self.universe.quantum_state.tick_count, location=deepcopy(cat.position), participants=[source_box_id, counterpart_box_id], details={'source_layer': target.source_layer, 'target_layer': target.target_layer, 'reason': failure_reason, 'cronenberg_id': cronenberg.id})
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
        if not isinstance(source_position, dict) or not self._same_position(cat.position or {}, source_position):
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
                counterpart_position=deepcopy(
                    getattr(
                        counterpart,
                        'position',
                        {},
                    )
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
        event = {'name': 'cat_sensed_quantum_counterpart', 'cat': cat.name, 'observation': observation.to_dict(), 'decision_source': 'cat_mind', 'executed': True}
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
        cat_position = cat.position or {}
        box_position = getattr(box, 'position', None)
        if not isinstance(box_position, dict):
            return self._record({'name': 'cat_box_exploration_failed', 'cat': cat.name, 'box_id': box_id, 'reason': 'box_position_missing', 'executed': False})
        if self._same_position(cat_position, box_position):
            return self._finish_box_exploration(cat=cat, intention=intention, box=box)
        quantum_space = getattr(self.universe, 'quantum_space', None)
        if quantum_space is None:
            return self._record({'name': 'cat_box_exploration_failed', 'cat': cat.name, 'box_id': box_id, 'reason': 'quantum_space_unavailable', 'executed': False})
        planned = quantum_space.plan_direct_cat_route(cat_id=cat.name, start_position=dict(cat_position), destination_position=dict(box_position), destination=f'explore_box:{box_id}', step_size=step_size)
        route = planned['route']
        route.state = 'ready'
        cat.active_route_id = route.route_id
        cat.box_exploration = (
            CatBoxExplorationState(
                active=True,
                arrived=False,
                box_id=box_id,
                route_id=route.route_id,
                destination=dict(
                    box_position
                ),
                observed=False,
            )
        )
        event = {'name': 'cat_approaching_box_to_explore', 'cat': cat.name, 'box_id': box_id, 'route_id': route.route_id, 'destination': dict(box_position), 'arrived': False, 'decision_source': 'cat_mind', 'executed': True}
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
        position = result.get('position')
        if position is not None:
            cat.position = dict(position)
        if result.get('arrived', False):
            box = next((candidate for candidate in getattr(self.universe, 'quantum_boxes', []) if getattr(candidate, 'id', None) == exploration.box_id), None)
            if box is None:
                return self._record({'name': 'cat_box_exploration_failed', 'cat': cat.name, 'reason': 'box_disappeared', 'executed': False})
            return self._finish_box_exploration(cat=cat, intention=intention, box=box)
        event = {'name': 'cat_approaching_box_to_explore', 'cat': cat.name, 'box_id': exploration.box_id, 'route_id': exploration.route_id, 'position': dict(position) if position is not None else None, 'destination': dict(exploration.destination), 'arrived': False, 'decision_source': 'cat_mind', 'executed': result.get('result') != 'no_active_route'}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _finish_box_exploration(self, cat, intention, box):
        box_id = getattr(box, 'id', None)
        observation = box.cat_observation_state(cat) if callable(getattr(box, 'cat_observation_state', None)) else {}
        memory = cat.memory
        remembered = None
        if memory is not None:
            remembered = memory.remember(event_type='quantum_box_observed', universe_tick=getattr(self.universe, 'universe_tick', None), location=cat.current_layer, participants=[box_id], details={'box_id': box_id, 'position': deepcopy(getattr(box, 'position', {})), 'observation': deepcopy(observation)})
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
        event = {'name': 'cat_explored_quantum_box', 'cat': cat.name, 'box_id': box_id, 'position': deepcopy(getattr(box, 'position', {})), 'observation': deepcopy(observation), 'memory': deepcopy(remembered), 'arrived': True, 'decision_source': 'cat_mind', 'executed': True}
        mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _execute_search_for_scent(self, cat, intention, cronenbergs=None, step_size=None):
        target = intention.target

        if not isinstance(
            target,
            CatScentSearchTarget,
        ):
            return self._record({
                'name': 'cat_scent_search_failed',
                'cat': cat.name,
                'reason': 'invalid_search_target',
                'executed': False,
            })

        identity = target.identity
        direction = target.trail_direction

        if not isinstance(
            direction,
            CatScentTrailDirection,
        ):
            return self._record({
                'name': 'cat_scent_search_failed',
                'cat': cat.name,
                'reason': (
                    'invalid_search_direction'
                ),
                'executed': False,
            })

        unit_vector = direction.unit_vector

        if identity is None or not isinstance(unit_vector, dict):
            return self._record({'name': 'cat_scent_search_failed', 'cat': cat.name, 'reason': 'invalid_search_direction', 'executed': False})
        search = cat.scent_search
        if (
            search is not None
            and not isinstance(
                search,
                CatScentSearchState,
            )
        ):
            raise TypeError(
                'Cat scent search state must be '
                'CatScentSearchState.'
            )
        if (
            isinstance(search, CatScentSearchState)
            and search.active
            and search.identity == identity
        ):
            return self._advance_scent_search(cat=cat, intention=intention, cronenbergs=cronenbergs)
        start = cat.position or {}
        distance = float(target.search_distance)
        destination = {axis: float(start.get(axis, 0.0)) + float(unit_vector.get(axis, 0.0)) * distance for axis in ('x', 'y', 'z')}
        quantum_space = getattr(self.universe, 'quantum_space', None)
        if quantum_space is None:
            return self._record({'name': 'cat_scent_search_failed', 'cat': cat.name, 'reason': 'quantum_space_unavailable', 'executed': False})
        planned = quantum_space.plan_direct_cat_route(cat_id=cat.name, start_position=dict(start), destination_position=dict(destination), destination=f'scent_search:{identity}', step_size=step_size)
        route = planned['route']
        route.state = 'ready'
        cat.active_route_id = route.route_id
        cat.scent_search = CatScentSearchState(
            active=True,
            identity=identity,
            layer=cat.current_layer,
            route_id=route.route_id,
            attempts=int(target.attempt) - 1,
            current_attempt=int(target.attempt),
            max_attempts=int(target.max_attempts),
            start_position=dict(start),
            destination=dict(destination),
            trail_direction=deepcopy(direction),
            arrived=False,
        )
        event = {'name': 'cat_searching_for_scent', 'cat': cat.name, 'identity': identity, 'attempt': target.attempt, 'max_attempts': target.max_attempts, 'route_id': route.route_id, 'start_position': dict(start), 'destination': dict(destination), 'arrived': False, 'decision_source': 'cat_mind', 'executed': True}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _advance_scent_search(self, cat, intention, cronenbergs=None):
        search = cat.scent_search
        if not isinstance(search, CatScentSearchState):
            raise TypeError(
                'Cat scent search state must be '
                'CatScentSearchState.'
            )
        result = self.universe.quantum_space.advance_cat_route(cat=cat, cronenbergs=cronenbergs if cronenbergs is not None else getattr(self.universe, 'cronenbergs', []), encounter_system=self.universe.cat_cronenberg_encounter, universe=self.universe)
        position = result.get('position')
        if position is not None:
            cat.position = dict(position)
        olfaction = CatOlfaction.sniff(cat=cat, universe=self.universe)
        reacquired = next(
            (
                item
                for item in olfaction.detected_aromas
                if item.recognition.recognized
                and item.recognition.identity
                == search.identity
            ),
            None,
        )
        if reacquired is not None:
            CatKnowledge.remember_olfaction(cat=cat, olfaction=olfaction, current_layer=cat.current_layer or 'unknown', universe_tick=getattr(self.universe, 'universe_tick', None))
            route = self.universe.quantum_space.find_cat_route(cat.name)
            if route is not None:
                route.stop_observation()
            search.active = False
            search.arrived = False
            search.reacquired = True
            search.reacquired_at = dict(cat.position or {})
            search.reacquired_source_id = reacquired.entity_id
            if hasattr(cat, 'active_route_id'):
                del cat.active_route_id
            mind = cat.mind
            mind.previous_intention = deepcopy(intention)
            mind.current_intention = None
            event = {'name': 'cat_reacquired_scent_during_search', 'cat': cat.name, 'identity': search.identity, 'source_id': reacquired.entity_id, 'position': dict(cat.position or {}), 'olfaction': deepcopy(olfaction), 'search_interrupted': True, 'decision_source': 'cat_mind', 'executed': True}
            mind.active_body_execution = deepcopy(event)
            return self._record(event)
        if result.get('arrived', False):
            return self._finish_scent_search(cat=cat, intention=intention)
        event = {'name': 'cat_searching_for_scent', 'cat': cat.name, 'identity': search.identity, 'attempt': search.current_attempt, 'max_attempts': search.max_attempts, 'route_id': search.route_id, 'position': dict(position) if position is not None else None, 'destination': dict(search.destination), 'arrived': False, 'decision_source': 'cat_mind', 'executed': result.get('result') != 'no_active_route'}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _finish_scent_search(self, cat, intention):
        search = cat.scent_search
        if not isinstance(search, CatScentSearchState):
            raise TypeError(
                'Cat scent search state must be '
                'CatScentSearchState.'
            )
        search.active = False
        search.arrived = True
        search.attempts = int((search.current_attempt or 1))
        if hasattr(cat, 'active_route_id'):
            del cat.active_route_id
        mind = cat.mind
        mind.previous_intention = deepcopy(intention)
        mind.current_intention = None
        event = {'name': 'cat_completed_scent_search_step', 'cat': cat.name, 'identity': search.identity, 'attempt': search.attempts, 'max_attempts': search.max_attempts, 'position': dict(cat.position or {}), 'trail_direction': deepcopy(search.trail_direction), 'arrived': True, 'decision_source': 'cat_mind', 'executed': True}
        mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _execute_follow_known_scent(self, cat, intention, cronenbergs=None, step_size=None):
        target = intention.target
        if not isinstance(
            target,
            CatKnownScentTarget,
        ):
            return self._record({
                'name': 'cat_known_scent_follow_failed',
                'cat': cat.name,
                'reason': 'invalid_scent_target',
                'executed': False,
            })
        layer = target.layer
        position = target.position
        if layer is None or not isinstance(position, dict):
            return self._record({'name': 'cat_known_scent_follow_failed', 'cat': cat.name, 'reason': 'invalid_scent_target', 'executed': False})
        if layer != cat.current_layer:
            return self._record({'name': 'cat_known_scent_follow_failed', 'cat': cat.name, 'identity': target.identity, 'reason': 'cross_layer_scent_navigation_not_available_yet', 'executed': False})
        follow = cat.known_scent_follow
        if (
            follow is not None
            and not isinstance(
                follow,
                CatKnownScentFollowState,
            )
        ):
            raise TypeError(
                'Cat known scent follow state '
                'must be '
                'CatKnownScentFollowState.'
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
            return self._advance_known_scent_follow(cat=cat, intention=intention, cronenbergs=cronenbergs)
        cat_position = cat.position or {}
        already_there = all((abs(float(cat_position.get(axis, 0.0)) - float(position.get(axis, 0.0))) <= 1e-09 for axis in ('x', 'y', 'z')))
        if already_there:
            return self._finish_known_scent_follow(cat=cat, intention=intention, position=position)
        quantum_space = getattr(self.universe, 'quantum_space', None)
        if quantum_space is None:
            return self._record({'name': 'cat_known_scent_follow_failed', 'cat': cat.name, 'reason': 'quantum_space_unavailable', 'executed': False})
        planned = quantum_space.plan_direct_cat_route(cat_id=cat.name, start_position=dict(cat_position), destination_position=dict(position), destination=f"known_scent:{target.identity}", step_size=step_size)
        route = planned['route']
        route.state = 'ready'
        cat.active_route_id = route.route_id
        cat.known_scent_follow = (
            CatKnownScentFollowState(
                active=True,
                arrived=False,
                route_id=route.route_id,
                identity=target.identity,
                source_id=target.source_id,
                destination=dict(
                    position
                ),
                trail_direction=deepcopy(
                    target.trail_direction
                ),
            )
        )
        event = {'name': 'cat_following_known_scent', 'cat': cat.name, 'identity': target.identity, 'layer': layer, 'destination': dict(position), 'route_id': route.route_id, 'arrived': False, 'decision_source': 'cat_mind', 'executed': True}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _advance_known_scent_follow(self, cat, intention, cronenbergs=None):
        follow = cat.known_scent_follow
        result = self.universe.quantum_space.advance_cat_route(cat=cat, cronenbergs=cronenbergs if cronenbergs is not None else getattr(self.universe, 'cronenbergs', []), encounter_system=self.universe.cat_cronenberg_encounter, universe=self.universe)
        position = result.get('position')
        if position is not None:
            cat.position = dict(position)
        if result.get('arrived', False):
            return self._finish_known_scent_follow(cat=cat, intention=intention, position=cat.position)
        event = {'name': 'cat_following_known_scent', 'cat': cat.name, 'identity': follow.identity, 'layer': cat.current_layer, 'destination': dict(follow.destination), 'route_id': follow.route_id, 'position': dict(position) if position is not None else None, 'arrived': False, 'decision_source': 'cat_mind', 'executed': result.get('result') != 'no_active_route'}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _finish_known_scent_follow(self, cat, intention, position):
        target = intention.target
        follow = cat.known_scent_follow

        if follow is None:
            follow = (
                CatKnownScentFollowState()
            )
            cat.known_scent_follow = follow
        elif not isinstance(
            follow,
            CatKnownScentFollowState,
        ):
            raise TypeError(
                'Cat known scent follow state '
                'must be '
                'CatKnownScentFollowState.'
            )

        follow.active = False
        follow.arrived = True
        follow.identity = target.identity
        follow.source_id = target.source_id
        follow.destination = dict(
            position
        )
        follow.trail_direction = deepcopy(
            target.trail_direction
        )
        if hasattr(cat, 'active_route_id'):
            del cat.active_route_id
        mind = cat.mind
        mind.previous_intention = deepcopy(intention)
        mind.current_intention = None
        event = {'name': 'cat_reached_known_scent', 'cat': cat.name, 'identity': target.identity, 'layer': cat.current_layer, 'destination': dict(position), 'trail_direction': deepcopy(target.trail_direction), 'arrived': True, 'decision_source': 'cat_mind', 'executed': True}
        mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _execute_share_legend(self, cat, intention):
        target = intention.target
        listener = None
        if isinstance(target, dict):
            target_name = target.get('name') or target.get('id')
        else:
            target_name = target
        for candidate in getattr(self.universe, 'entities', []):
            if not isinstance(candidate, dict):
                continue
            if candidate.get('name') == target_name:
                listener = candidate
                break
        if listener is None:
            return self._record({'name': 'cat_legend_not_shared', 'cat': cat.name, 'listener': target_name, 'reason': 'listener_not_found', 'executed': False})
        result = CatKnowledge.share_legend(storyteller=cat, listener=listener, universe=self.universe)
        mind = cat.mind
        mind.previous_intention = deepcopy(intention)
        mind.current_intention = None
        event = {**result, 'cat': cat.name, 'intention': 'share_legend', 'decision_source': 'cat_mind', 'executed': True}
        mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _execute_exploration_pair_creation(self, cat, intention):
        """
        Ko?ka vytvo?? stabiln? pr?zkumn? p?r
        a ihned jej pou?ije.

        Rozhodnut? u? prob?hlo v CatMind.
        Executor pouze vytvo?? t?lesnou cestu
        a zah?j? p?enos.
        """
        target = intention.target

        if not isinstance(
            target,
            CatExplorationPairTarget,
        ):
            return self._record({
                'name': (
                    'cat_exploration_pair_creation_failed'
                ),
                'cat': cat.name,
                'intention': (
                    'create_exploration_pair'
                ),
                'reason': (
                    'invalid_exploration_pair_target'
                ),
                'executed': False,
            })

        destination_layer = target.layer
        destination_position = target.position
        if destination_layer is None or destination_position is None:
            return self._record({'name': 'cat_exploration_pair_creation_failed', 'cat': cat.name, 'intention': 'create_exploration_pair', 'reason': 'missing_exploration_destination', 'executed': False})
        transfer_system = getattr(self.universe, 'cat_box_transfer', None)
        if transfer_system is None:
            return self._record({'name': 'cat_exploration_pair_creation_failed', 'cat': cat.name, 'intention': 'create_exploration_pair', 'reason': 'cat_box_transfer_unavailable', 'executed': False})
        creation = transfer_system.create_exploration_pair(cat=cat, destination_layer=destination_layer, destination_position=destination_position)
        if not creation.get('created', False):
            return self._record({'name': 'cat_exploration_pair_creation_failed', 'cat': cat.name, 'intention': 'create_exploration_pair', 'reason': creation.get('reason', 'pair_creation_failed'), 'creation_result': creation, 'executed': False})
        source_box = creation.get('source_box')
        target_box = creation.get('target_box')
        if source_box is None or target_box is None:
            return self._record({'name': 'cat_exploration_pair_transfer_failed', 'cat': cat.name, 'intention': 'create_exploration_pair', 'pair_id': creation.get('pair_id'), 'reason': 'created_pair_boxes_missing', 'creation_result': creation, 'executed': False})
        transfer = transfer_system.transfer_cat(cat=cat, source_box_id=source_box.id, target_box_id=target_box.id)
        if not transfer.get('transferred', False):
            cat.state = 'exploration_pair_created_but_transfer_failed'
            return self._record({'name': 'cat_exploration_pair_transfer_failed', 'cat': cat.name, 'intention': 'create_exploration_pair', 'pair_id': creation['pair_id'], 'source_box_id': source_box.id, 'target_box_id': target_box.id, 'reason': transfer.get('reason', 'stable_pair_transfer_failed'), 'creation_result': creation, 'transfer_result': transfer, 'pair_preserved': True, 'executed': False})
        exploration_route = None
        if cat.current_layer == 'quantum_layer':
            exploration_route = transfer_system.start_quantum_exploration_route(cat=cat, pair_id=creation['pair_id'])
        mind = cat.mind
        mind.previous_intention = deepcopy(intention)
        mind.current_intention = None
        event = {'name': 'cat_started_autonomous_exploration_through_new_pair', 'cat': cat.name, 'intention': 'create_exploration_pair', 'pair_id': creation['pair_id'], 'source_box_id': source_box.id, 'target_box_id': target_box.id, 'source_layer': creation['source_layer'], 'target_layer': creation['target_layer'], 'energy_cost_j': creation['energy_cost_j'], 'remaining_cat_energy': creation['remaining_cat_energy'], 'creation': {'created': True, 'stable': creation.get('stable', True), 'available_to_other_cats': creation.get('available_to_other_cats', True)}, 'transfer': {'transferred': True, 'pair_remains_stable': transfer.get('pair_remains_stable', False), 'target_box_consumed': transfer.get('target_box_consumed'), 'destination_layer': transfer.get('target_layer'), 'trail': transfer.get('trail')}, 'exploration_route': exploration_route, 'decision_source': 'cat_mind', 'executed': True}
        mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _execute_wander(self, cat, intention, step_size=None):
        position = cat.position
        if not isinstance(position, dict):
            return self._record({'name': 'cat_wander_failed', 'cat': cat.name, 'reason': 'missing_position', 'executed': False})
        step = 1.0 if step_size is None else max(0.0, float(step_size))
        phase = int(getattr(cat.needs, 'tick', 0)) + sum((ord(ch) for ch in cat.name))
        axis = 'x' if phase % 2 == 0 else 'y'
        direction = 1.0 if phase // 2 % 2 == 0 else -1.0
        previous = deepcopy(position)
        position.setdefault('x', 0.0)
        position.setdefault('y', 0.0)
        position.setdefault('z', 0.0)
        position[axis] = float(position[axis]) + direction * step
        cat.state = 'wandering_by_own_choice'
        event = {'name': 'cat_wandered', 'cat': cat.name, 'from_position': previous, 'position': deepcopy(position), 'axis': axis, 'step': direction * step, 'decision_source': 'cat_mind', 'executed': True}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _execute_rest(self, cat, intention):
        previous_state = cat.state
        cat.state = 'resting_by_own_choice'
        cat.suggested_intent = None
        if hasattr(cat, 'intent'):
            del cat.intent
        if hasattr(cat, 'active_route_id'):
            del cat.active_route_id
        event = {'name': 'cat_intention_rest_started', 'cat': cat.name, 'intention': 'rest', 'previous_state': previous_state, 'state': cat.state, 'decision_source': 'cat_mind', 'executed': True}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

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
        if not isinstance(cat_position, dict) or not isinstance(target_position, dict):
            return self._record({'name': 'cat_approach_failed', 'cat': cat.name, 'target': target_name, 'reason': 'missing_position', 'executed': False})
        if self._same_position(cat_position, target_position):
            cat.state = 'near_target_cat'
            social_event = self.social_system.meet(cat, target_cat)
            event = {'name': 'cat_approach_completed', 'cat': cat.name, 'target': target_name, 'position': deepcopy(cat_position), 'arrived': True, 'decision_source': 'cat_mind', 'social': deepcopy(social_event), 'executed': True}
            cat.mind.active_body_execution = deepcopy(event)
            return self._record(event)
        quantum_space = getattr(self.universe, 'quantum_space', None)
        if quantum_space is None:
            self.universe.enable_quantum_layer()
            quantum_space = getattr(self.universe, 'quantum_space', None)
        if quantum_space is None:
            return self._record({'name': 'cat_approach_failed', 'cat': cat.name, 'target': target_name, 'reason': 'quantum_space_unavailable', 'executed': False})
        planned = quantum_space.plan_direct_cat_route(cat_id=cat.name, start_position=dict(cat_position), destination_position=dict(target_position), destination=f'cat:{target_name}', step_size=step_size)
        route = planned.get('route')
        if route is None:
            return self._record({'name': 'cat_approach_failed', 'cat': cat.name, 'target': target_name, 'reason': planned.get('result', 'route_not_planned'), 'executed': False})
        route.state = 'ready'
        cat.active_route_id = route.route_id
        cat.navigation_target = target_name
        cat.state = 'approaching_cat'
        event = {'name': 'cat_approach_started', 'cat': cat.name, 'target': target_name, 'route_id': route.route_id, 'destination': deepcopy(target_position), 'arrived': False, 'decision_source': 'cat_mind', 'executed': True}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

    def _defer_intention(self, cat, intention):
        intention_type = intention.type
        required_system = self.DEFERRED_INTENTS[intention_type]
        cat.state = 'intention_waiting_for_body_system'
        event = {'name': 'cat_intention_body_action_deferred', 'cat': cat.name, 'intention': intention_type, 'target': intention.target, 'required_system': required_system, 'decision_preserved': True, 'executed': False, 'deferred': True}
        cat.mind.active_body_execution = deepcopy(event)
        return self._record(event)

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
