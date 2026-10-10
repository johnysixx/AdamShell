from copy import deepcopy
from core.entity.components import SpatialVector3
from core.entity.quantum_cat_route_state import (
    QuantumCatRouteState,
)
from cats.cat_knowledge import CatKnowledge
from cats.cat import Cat
from cats.cat_intention_state import (
    CatIntentionCandidate,
)
from cats.cat_social_system import CatSocialSystem
from cats.cat_basic_intention_result_state import (
    CatIntentionBodyActionDeferredEvent,
    CatRestStartedEvent,
    CatWanderedEvent,
    CatWanderFailedResult,
)


from cats.cat_intention_state import CatVisitRecipientTarget

from cats.cat_intention_state import CatApproachCatTarget

from cats.cat_intention_state import CatShareLegendTarget
from cats.cat_quantum_box_intention_handler import (
    CatQuantumBoxIntentionHandler,
)
from cats.cat_exploration_pair_intention_handler import (
    CatExplorationPairIntentionHandler,
)
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
        self.quantum_box_intentions = (
            CatQuantumBoxIntentionHandler(
                universe=self.universe,
                recorder=self._record,
                same_position=self._same_position,
            )
        )

        self.exploration_pair_intentions = (
            CatExplorationPairIntentionHandler(
                universe=self.universe,
                recorder=self._record,
            )
        )
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
            return self.quantum_box_intentions.sense(cat=cat, intention=intention)
        if intention_type == 'travel_through_known_quantum_box':
            return self.quantum_box_intentions.travel(cat=cat, intention=intention)
        if intention_type == 'explore_box':
            return self.quantum_box_intentions.explore(cat=cat, intention=intention, cronenbergs=cronenbergs, step_size=step_size)
        if intention_type == 'search_for_scent':
            return self.scent_search_intentions.execute(cat=cat, intention=intention, cronenbergs=cronenbergs, step_size=step_size)
        if intention_type == 'follow_known_scent':
            return self.known_scent_intentions.execute(cat=cat, intention=intention, cronenbergs=cronenbergs, step_size=step_size)
        if intention_type == 'share_legend':
            return self._execute_share_legend(cat=cat, intention=intention)
        if intention_type == 'create_exploration_pair':
            return self.exploration_pair_intentions.execute(cat=cat, intention=intention)
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
