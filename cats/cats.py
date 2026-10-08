import random
from universe.logger import UniverseLogger
from .memory import CatMemory
from .reproduction import CatReproduction
from .genotype import CatGenotype
from .cat_learning import CatLearning
from .cat import Cat
from .cats_state import CatsState
from .cat_access_rules import CatAccessRules
from .cat_personality import CatPersonality
from .cat_mind import CatMind
from .cat_intellect import CatIntellect
from .cat_intention_executor import CatIntentionExecutor
from .cat_perception import CatPerception
from universe.aroma_profile import AromaProfile
from universe.aroma_foundations import AromaMixture
from core.entity.quantum_cat_route_state import (
    QuantumCatRouteState,
)
from .cat_knowledge import CatKnowledge
from .cat_need_system import CatNeedSystem

from .cat_quantum_return_state import CatQuantumReturnState

from .cat_quantum_exploration_state import CatQuantumExplorationState

from .cat_navigation_offer_state import CatNavigationOfferState

from .cat_navigation_decision_state import CatNavigationDecisionState
from .cat_navigation_decision import CatNavigationDecision
from .cat_navigation_result_state import (
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
from .cat_mind_result_state import (
    CatIntentionNotSelectedResult,
    CatIntentionSelectedEvent,
)
from .cat_overpopulation_activation_state import (
    CatOverpopulationActivatedEvent,
    CatOverpopulationActivationDeniedResult,
)

from quantum.cat_quantum_return_result_state import (
    CatQuantumReturnNotAdvancedResult,
)

class Cats:

    def __init__(self, universe):
        self.universe = universe
        self.universe.cats_layer = self
        self.cats_state = CatsState()
        self.state = self.cats_state
        self.intention_executor = CatIntentionExecutor(self)
        self.perception = CatPerception(self)
        self.write_to_world()
        UniverseLogger.boot('CATS CREATED')
        UniverseLogger.boot('CATS ACCESS: anywhere via boxes and cat doors')

    @property
    def cats(self):
        return self.cats_state.cats

    @property
    def events(self):
        return self.cats_state.events

    @property
    def tick_count(self):
        return self.cats_state.tick_count

    @tick_count.setter
    def tick_count(self, value):
        self.cats_state.tick_count = value

    @property
    def allowed_colors(self):
        return self.cats_state.allowed_colors

    @property
    def allowed_patterns(self):
        return self.cats_state.allowed_patterns

    @property
    def allowed_eye_colors(self):
        return self.cats_state.allowed_eye_colors

    @property
    def allowed_fur_lengths(self):
        return self.cats_state.allowed_fur_lengths

    @property
    def allowed_sexes(self):
        return self.cats_state.allowed_sexes

    @property
    def default_idea_energy(self):
        return self.cats_state.default_idea_energy

    @property
    def access_rules(self):
        access_rules = (
            self.cats_state.access_rules
        )

        if not isinstance(
            access_rules,
            CatAccessRules,
        ):
            raise TypeError(
                'Cat access rules must be '
                'CatAccessRules.'
            )

        return access_rules

    @property
    def public_state(self):
        return {
            'type': self.cats_state.layer_type,
            'state': self.cats_state.status,
            'allowed_colors': self.allowed_colors,
            'allowed_patterns': self.allowed_patterns,
            'allowed_eye_colors': self.allowed_eye_colors,
            'allowed_fur_lengths': self.allowed_fur_lengths,
            'allowed_sexes': self.allowed_sexes,
            'default_idea_energy': self.default_idea_energy,
            'access_rules': self.access_rules.to_dict(),
            'cats': self.cats,
            'cats_state': self.cats_state.to_dict(),
        }

    def write_to_world(self):
        self.universe.world['cats'] = self.public_state
        self.universe.world['cats_state'] = self.cats_state

    def create_cat(self, name, color, fur_length, pattern='solid', eye_color='green', sex='female', origin='manual_creation'):
        if color not in self.allowed_colors:
            UniverseLogger.event(f'CAT CREATION DENIED: invalid color {color}')
            return None
        if fur_length not in self.allowed_fur_lengths:
            UniverseLogger.event(f'CAT CREATION DENIED: invalid fur length {fur_length}')
            return None
        if pattern not in self.allowed_patterns:
            UniverseLogger.event(f'CAT CREATION DENIED: invalid pattern {pattern}')
            return None
        if eye_color not in self.allowed_eye_colors:
            UniverseLogger.event(f'CAT CREATION DENIED: invalid eye color {eye_color}')
            return None
        if sex not in self.allowed_sexes:
            UniverseLogger.event(f'CAT CREATION DENIED: invalid sex {sex}')
            return None
        cat = Cat(name=name, color=color, pattern=pattern, eye_color=eye_color, fur_length=fur_length, sex=sex, genotype=CatGenotype.create_founder(sex=sex), reproduction=CatReproduction.create_state(sex=sex, neutered=False), origin=origin, idea_energy=self.default_idea_energy, memory=CatMemory(name), access=self.access_rules, learning=CatLearning.create_complete_state(), personality=CatPersonality.create_state(), mind=CatMind.create_state(), intellect=CatIntellect.create_state(), aroma=AromaProfile(identity=f'cat:{name}', base_components={'cat': 1.0, 'fur': 0.8, f'individual_cat:{name}': 2.0}, base_intensity=1.0))
        self.cats.append(cat)
        self.write_to_world()
        UniverseLogger.event(f'CAT CREATED: {name}')
        return cat

    def learn_raspberry_rum_aroma(self, cat, meeting_place):
        raspberry_rum = getattr(meeting_place, 'raspberry_rum', None)
        if not isinstance(raspberry_rum, AromaMixture):
            raise TypeError(
                'meeting_place.raspberry_rum must be an AromaMixture object.'
            )
        return CatKnowledge.learn_aroma(cat=cat, identity='raspberry_rum', components=raspberry_rum.aroma_profile, source='direct_raspberry_rum_experience')

    def learn_cat_aroma(self, observer, observed_cat):
        aroma = observed_cat.aroma.current()
        return CatKnowledge.learn_aroma(cat=observer, identity=observed_cat.aroma.identity, components=aroma, source='direct_cat_contact')

    def learn_cronenberg_aroma(self, cat, cronenberg):
        aroma = cronenberg.aroma.current()
        return CatKnowledge.learn_aroma(cat=cat, identity='cronenberg', components=aroma, source='direct_cronenberg_encounter')

    def learn_aroma(self, cat, identity, components, source='direct_experience'):
        return CatKnowledge.learn_aroma(cat=cat, identity=identity, components=components, source=source)

    def add_surface_aroma(self, cat, source, components, intensity=1.0, decay_rate=0.03):
        return cat.aroma.add_surface(source=source, components=components, intensity=intensity, decay_rate=decay_rate)

    def current_aroma(self, cat):
        return cat.aroma.current()

    def decay_cat_aroma(self, cat, ticks=1):
        return cat.aroma.decay(ticks=ticks)

    def activate_for_cronenberg_overpopulation(
        self,
        cat,
        hunt_quota=10,
    ):
        if not isinstance(
            cat,
            Cat,
        ):
            return (
                CatOverpopulationActivationDeniedResult(
                    reason="invalid_cat",
                )
            )

        if cat.type != "cat":
            return (
                CatOverpopulationActivationDeniedResult(
                    reason="not_a_cat",
                    cat=cat.name,
                )
            )

        if not self.can_travel(
            cat,
            via="boxes",
        ):
            return (
                CatOverpopulationActivationDeniedResult(
                    reason="box_travel_unavailable",
                    cat=cat.name,
                )
            )

        eaten = int(
            cat.cronenbergs_eaten
        )

        hunt_quota = int(
            hunt_quota
        )

        if eaten < hunt_quota:
            intent = (
                "hunt_nearest_cronenberg"
            )
        else:
            intent = (
                "return_to_bar"
            )

        cat.state = (
            "aware_of_cronenberg_overpopulation"
        )

        cat.suggested_intent = intent
        cat.hunt_quota = hunt_quota

        cat.overpopulation_response_available = (
            True
        )

        event = (
            CatOverpopulationActivatedEvent(
                cat=cat.name,
                suggested_intent=intent,
                cronenbergs_eaten=eaten,
                hunt_quota=hunt_quota,
            )
        )

        self.emit_event(
            event
        )

        return event

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
                self.accept_navigation_offer(
                    cat
                )
            )

        else:
            result = (
                self.decline_navigation_offer(
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

    def observe_cat(self, cat, vision_radius=None):
        return self.perception.observe(cat=cat, vision_radius=vision_radius)

    def think_and_act(self, cat, quantum_roll=None, vision_radius=None, cronenbergs=None, step_size=None):
        from .cat_mind import CatMind
        observations = self.observe_cat(cat=cat, vision_radius=vision_radius)
        if not observations.observed:
            return {'name': 'cat_thought_cycle_failed', 'cat': getattr(cat, 'name', None), 'observation': observations, 'completed': False}
        decision = CatMind.decide(
            cat=cat,
            observations=observations,
            quantum_roll=quantum_roll,
        )

        if isinstance(
            decision,
            CatIntentionNotSelectedResult,
        ):
            return {
                'name': 'cat_thought_cycle_failed',
                'cat': cat.name,
                'observations': observations,
                'decision': decision,
                'completed': False,
            }

        if not isinstance(
            decision,
            CatIntentionSelectedEvent,
        ):
            raise TypeError(
                'Cat thought cycle requires '
                'a cat intention decision object.'
            )

        execution = self.execute_cat_intention(
            cat=cat,
            cronenbergs=cronenbergs,
            step_size=step_size,
        )
        event = {'name': 'cat_thought_cycle_completed', 'cat': cat.name, 'observations': observations, 'decision': decision, 'execution': execution, 'completed': True}
        self.emit_event(event)
        return event

    def advance_cat_quantum_exploration(self, cat, rng=None):
        transfer_system = getattr(self.universe, 'cat_box_transfer', None)
        if transfer_system is None:
            return {'name': 'cat_quantum_exploration_not_advanced', 'cat': cat.name, 'reason': 'cat_box_transfer_unavailable', 'advanced': False}
        return transfer_system.advance_quantum_exploration(cat=cat, rng=rng)

    def advance_cat_quantum_return(
        self,
        cat,
        rng=None,
    ):
        transfer_system = getattr(
            self.universe,
            "cat_box_transfer",
            None,
        )

        if transfer_system is None:
            return (
                CatQuantumReturnNotAdvancedResult(
                    cat=cat.name,
                    reason=(
                        "cat_box_transfer_unavailable"
                    ),
                )
            )

        return (
            transfer_system
            .advance_quantum_return(
                cat=cat,
                rng=rng,
            )
        )


    def execute_cat_intention(self, cat, cronenbergs=None, step_size=None):
        return self.intention_executor.execute_current_intention(cat=cat, cronenbergs=cronenbergs, step_size=step_size)

    def can_travel(self, cat, via):
        if cat.type != 'cat':
            return False
        access_rules = self.access_rules

        if not access_rules.can_access_anywhere:
            return False

        return via in access_rules.access_via

    def emit_event(self, event):
        self.events.append(event)
        self.write_to_world()
        UniverseLogger.event(f'CATS EVENT: {event}')

    def tick(self):
        self._clear_events()
        self.tick_count += 1
        report = {'name': 'cats_tick_completed', 'tick': self.tick_count, 'cats': [], 'groups': [], 'errors': [], 'cronenbergs_created': []}
        UniverseLogger.event(f'CATS TICK {self.tick_count}')
        for cat in list(self.cats):
            result = self._run_cat_tick_operation(cat=cat, operation=self._tick_cat_autonomously)
            report['cats'].append(result)
            if not result.get('ok', True):
                report['errors'].append(result)
                cronenberg_id = result.get('cronenberg_id')
                if cronenberg_id is not None:
                    report['cronenbergs_created'].append(cronenberg_id)
        group_results = self._tick_groups()
        report['groups'].extend(group_results)
        for result in group_results:
            if not result.get('ok', True):
                report['errors'].append(result)
                cronenberg_id = result.get('cronenberg_id')
                if cronenberg_id is not None:
                    report['cronenbergs_created'].append(cronenberg_id)
        report['ok'] = not report['errors']
        report['error_count'] = len(report['errors'])
        self.emit_event({'name': 'cats_tick_completed', 'tick': self.tick_count, 'cats_processed': len(report['cats']), 'groups_processed': len(report['groups']), 'error_count': report['error_count'], 'cronenbergs_created': list(report['cronenbergs_created'])})
        return report

    def _tick_cat_autonomously(self, cat):
        if not getattr(cat, 'active', True):
            return {'name': 'cat_autonomous_tick_skipped', 'cat': cat.name, 'reason': 'inactive', 'completed': False}
        quantum_return = getattr(cat, 'quantum_return', None)

        if (
            quantum_return is not None
            and not isinstance(
                quantum_return,
                CatQuantumReturnState,
            )
        ):
            raise TypeError(
                'Cat quantum return state '
                'must be CatQuantumReturnState.'
            )

        if (
            isinstance(
                quantum_return,
                CatQuantumReturnState,
            )
            and quantum_return.active
        ):
            result = self.advance_cat_quantum_return(cat)
            return {'name': 'cat_autonomous_tick_completed', 'cat': cat.name, 'mode': 'quantum_return', 'result': result, 'completed': True}
        quantum_exploration = getattr(cat, 'quantum_exploration', None)

        if (
            quantum_exploration is not None
            and not isinstance(
                quantum_exploration,
                CatQuantumExplorationState,
            )
        ):
            raise TypeError(
                'Cat quantum exploration state '
                'must be '
                'CatQuantumExplorationState.'
            )

        if (
            isinstance(
                quantum_exploration,
                CatQuantumExplorationState,
            )
            and quantum_exploration.active
        ):
            result = self.advance_cat_quantum_exploration(cat)
            return {'name': 'cat_autonomous_tick_completed', 'cat': cat.name, 'mode': 'quantum_exploration', 'result': result, 'completed': True}
        if getattr(cat, 'position', None) is None:
            return {'name': 'cat_autonomous_tick_skipped', 'cat': cat.name, 'reason': 'no_position', 'completed': False}
        needs_event = CatNeedSystem.advance(cat)
        thought = self.think_and_act(
            cat=cat,
            cronenbergs=getattr(
                self.universe,
                "cronenbergs",
                [],
            ),
        )

        decision = thought.get(
            "decision"
        )

        if isinstance(
            decision,
            CatIntentionSelectedEvent,
        ):
            intention_type = (
                decision.intention
            )

        elif isinstance(
            decision,
            CatIntentionNotSelectedResult,
        ):
            intention_type = None

        elif decision is None:
            intention_type = None

        else:
            raise TypeError(
                "Cat autonomous tick thought "
                "decision must be a cat mind "
                "decision result object."
            )

        if intention_type is None:
            current = (
                cat.mind.current_intention
            )

            intention_type = (
                current.type
                if current is not None
                else None
            )
        needs_after_action = CatNeedSystem.apply_action(cat, intention_type)
        return {'name': 'cat_autonomous_tick_completed', 'cat': cat.name, 'mode': 'thought_cycle', 'needs': needs_event, 'needs_after_action': needs_after_action, 'thought': thought, 'completed': bool(thought.get('completed', False))}

    def _tick_groups(self):
        group_system = getattr(self, 'group_system', None)
        if group_system is None:
            return []
        from .cat_group_lifecycle_system import CatGroupLifecycleSystem
        lifecycle = getattr(self, 'group_lifecycle_system', None)
        if lifecycle is None or lifecycle.group_system is not group_system:
            lifecycle = CatGroupLifecycleSystem(group_system)
            self.group_lifecycle_system = lifecycle
        results = []
        for group_id in list(group_system.groups):
            result = self._run_group_tick_operation(group_id=group_id, operation=lifecycle.advance)
            results.append(result)
        return results

    def _run_cat_tick_operation(self, cat, operation):
        try:
            value = operation(cat)
            return {'cat': cat.name, 'ok': True, 'result': value}
        except Exception as error:
            return self._cat_tick_error(error=error, source_component=f'cat:{cat.name}', source_operation='autonomous_tick', cat_name=cat.name)

    def _run_group_tick_operation(self, group_id, operation):
        try:
            value = operation(group_id, self.cats)
            return {'group_id': group_id, 'ok': True, 'result': value}
        except Exception as error:
            return self._cat_tick_error(error=error, source_component=f'cat_group:{group_id}', source_operation='lifecycle_advance', group_id=group_id)

    def _cat_tick_error(self, error, source_component, source_operation, **context):
        UniverseLogger.event(f'CATS TICK ERROR: SOURCE={source_component}.{source_operation} ERROR={type(error).__name__}: {error}')
        cronenberg = None
        create_cronenberg = getattr(self.universe, 'create_cronenberg_from_quantum_error', None)
        if callable(create_cronenberg):
            cronenberg = create_cronenberg(error=error, source_component=source_component, source_operation=source_operation)
        return {**context, 'ok': False, 'source_component': source_component, 'source_operation': source_operation, 'error_type': type(error).__name__, 'error_message': str(error), 'cronenberg_id': getattr(cronenberg, 'id', None)}

    def _clear_events(self):
        self.events.clear()
