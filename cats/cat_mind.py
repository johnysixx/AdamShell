from cats.cat_components import CatMindState
from cats.cat_intellect import CatIntellect
from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatKnownScentTarget,
    CatScentSearchTarget,
    CatScentBoxTarget,
    CatQuantumBoxTravelTarget,
)
from cats.cat_knowledge import CatKnowledge
from cats.cat_perception_state import (
    CatPerceptionState
)
from cats.cat_scent_direction_state import (
    CatScentTrailDirection,
)
from cats.cat_scent_navigation_state import (
    CatKnownScentFollowState,
    CatScentSearchState,
)
from copy import deepcopy

from cats.cat_quantum_observation_state import (
    CatQuantumCounterpartObservation,
)

from cats.cat_intention_state import CatQuantumBoxTravelTarget

from cats.cat_perception_state import CatScentTransferCandidate

from cats.cat_intention_state import CatQuantumCounterpartSenseTarget

from cats.cat_intention_state import CatExploreBoxTarget

from cats.cat_intention_state import CatExplorationPairTarget

from cats.cat_intention_state import CatVisitRecipientTarget

from cats.cat_intention_state import CatApproachCatTarget

from cats.cat_intention_state import CatShareLegendTarget

class CatMind:
    INTENTION_TYPES = ('visit_bar', 'visit_recipient', 'hunt_cronenberg', 'track_cronenberg_scent', 'follow_known_scent', 'search_for_scent', 'follow_scent_through_box', 'avoid_cronenberg_scent', 'explore_box', 'sense_quantum_counterpart', 'travel_through_known_quantum_box', 'travel_trough_known_quantum_box', 'create_exploration_pair', 'approach_cat', 'share_legend', 'observe', 'wander', 'rest')

    @classmethod
    def create_state(cls):
        return CatMindState(
            current_intention=None,
            previous_intention=None,
            candidates=[],
            decision_count=0,
            history=[],
            observation_history=[],
        )

    @classmethod
    def ensure_state(cls, cat):
        mind = cat.mind
        if not hasattr(mind, 'current_intention'):
            mind.current_intention = None
        if not hasattr(mind, 'previous_intention'):
            mind.previous_intention = None
        if not hasattr(mind, 'candidates'):
            mind.candidates = []
        if not hasattr(mind, 'decision_count'):
            mind.decision_count = 0
        if not hasattr(mind, 'history'):
            mind.history = []
        return mind

    @classmethod
    def consider(cls, cat, observations):
        if not isinstance(
            observations,
            CatPerceptionState,
        ):
            raise TypeError(
                "CatMind observations must be "
                "CatPerceptionState."
            )

        """
        VytvoĹ™Ă\xad moĹľnĂ© Ăşmysly.

        Nic nevykonĂˇvĂˇ a nevybĂ\xadrĂˇ vĂ\xadtÄ›ze.
        """
        traits = cat.personality.traits
        curiosity = float(traits.curiosity)
        courage = float(traits.courage)
        aggression = float(traits.aggression)
        empathy = float(traits.empathy)
        patience = float(traits.patience)
        candidates = []
        if observations.bar_known:
            bar_score = 0.45
            if observations.bar_visible:
                bar_score += 0.1
            bar_score += cls._bar_memory_score(cat)
            quantum_failure_bar_score = cls._quantum_failure_bar_score(cat)
            bar_score += quantum_failure_bar_score
            candidates.append(cls._candidate(intention_type='visit_bar', score=bar_score, reasons=['bar_known', *(['bar_visible'] if observations.bar_visible else []), *(['positive_bar_memory'] if cls._bar_memory_score(cat) > 0 else []), *(['seeking_safety_after_quantum_failure'] if quantum_failure_bar_score > 0 else [])]))
        recipient = cat.recipient
        if recipient is not None:
            recipient_score = 0.25 + empathy * 0.3 + curiosity * 0.1 + patience * 0.05
            candidates.append(cls._candidate(intention_type='visit_recipient', score=recipient_score, reasons=['assigned_recipient', 'empathy', 'curiosity'], target=CatVisitRecipientTarget(recipient_id=recipient)))
        huntable = observations.huntable_cronenbergs
        if huntable:
            danger = float(observations.cronenberg_danger)
            hunt_score = 0.25 + courage * 0.3 + aggression * 0.25 + curiosity * 0.1 - danger * 0.2
            candidates.append(cls._candidate(intention_type='hunt_cronenberg', score=hunt_score, reasons=['huntable_cronenberg_visible', 'courage', 'aggression'], target=huntable[0]))
        if observations.cronenberg_scent_recognized and (not observations.visible_cronenbergs):
            scent_track_score = 0.15 + courage * 0.35 + aggression * 0.3 + curiosity * 0.2
            scent_avoid_score = 0.15 + (1.0 - courage) * 0.45 + patience * 0.25 + (1.0 - aggression) * 0.15
            candidates.append(cls._candidate(intention_type='track_cronenberg_scent', score=scent_track_score, reasons=['recognized_cronenberg_scent', 'cronenberg_not_visible', 'courage', 'aggression', 'curiosity']))
            if observations.bar_known:
                candidates.append(cls._candidate(intention_type='avoid_cronenberg_scent', score=scent_avoid_score, reasons=['recognized_cronenberg_scent', 'cronenberg_not_visible', 'low_courage', 'patience', 'known_safe_bar']))
        scent_places = cat.knowledge.known_scent_places
        current_layer = cat.current_layer
        knowledge = cat.knowledge
        current_tick = knowledge.scent_clock_tick
        local_scent_places = []
        for place in scent_places:
            if place.layer != current_layer:
                continue
            last_seen_tick = place.last_seen_tick
            if current_tick is None or last_seen_tick is None:
                age_ticks = 0
            else:
                age_ticks = max(0, int(current_tick) - int(last_seen_tick))
            freshness = 0.5 ** (age_ticks / 50.0)
            if freshness < 0.05:
                continue
            local_scent_places.append({
                'memory': place,
                'age_ticks': age_ticks,
                'freshness': freshness,
            })
        reached_scent = cat.known_scent_follow
        if (
            reached_scent is not None
            and not isinstance(
                reached_scent,
                CatKnownScentFollowState,
            )
        ):
            raise TypeError(
                'Cat known scent follow state '
                'must be '
                'CatKnownScentFollowState.'
            )
        currently_smelt_identities = {
            item.recognition.identity
            for item in observations.olfaction.detected_aromas
            if item.recognition.recognized
        }
        if (
            isinstance(
                reached_scent,
                CatKnownScentFollowState,
            )
            and reached_scent.arrived
            and (
                reached_scent.identity
                not in currently_smelt_identities
            )
        ):
            local_scent_places = []
        if local_scent_places:
            strongest = max(
                local_scent_places,
                key=lambda item: (
                    float(
                        item[
                            'memory'
                        ].confidence
                    )
                    + min(
                        1.0,
                        float(
                            item[
                                'memory'
                            ].last_intensity
                        ),
                    )
                )
                * float(
                    item[
                        'freshness'
                    ]
                ),
            )
            memory = strongest[
                'memory'
            ]
            identity = memory.identity
            if identity not in (None, 'unknown_aroma', 'cronenberg'):
                scent_direction = CatKnowledge.infer_scent_direction(cat=cat, identity=identity, layer=current_layer)
                candidates.append(
                    cls._candidate(
                        intention_type=(
                            'follow_known_scent'
                        ),
                        score=(
                            0.15
                            + curiosity * 0.25
                            + courage * 0.1
                            + float(
                                memory.confidence
                            ) * 0.25
                        ),
                        reasons=[
                            'known_scent_place',
                            'recognized_identity',
                            'curiosity',
                        ],
                        target=CatKnownScentTarget(
                            identity=identity,
                            layer=memory.layer,
                            position=deepcopy(
                                memory.position
                            ),
                            source_id=(
                                memory.source_id
                            ),
                            age_ticks=strongest[
                                'age_ticks'
                            ],
                            freshness=strongest[
                                'freshness'
                            ],
                            trail_direction=deepcopy(
                                scent_direction
                            ),
                        ),
                    )
                )
        scent_transfers = (
            observations.scent_transfer_candidates
        )

        for scent_transfer in scent_transfers:
            if not isinstance(
                scent_transfer,
                CatScentTransferCandidate,
            ):
                raise TypeError(
                    'Scent transfer candidate '
                    'must be '
                    'CatScentTransferCandidate.'
                )

        if scent_transfers:
            best_scent_transfer = max(
                scent_transfers,
                key=lambda item: float(
                    item.similarity
                ),
            )

            identity = (
                best_scent_transfer.identity
            )

            scent_score = (
                0.2
                + curiosity * 0.3
                + courage * 0.2
                + float(
                    best_scent_transfer.similarity
                ) * 0.25
            )

            if identity == 'cronenberg':
                scent_score += (
                    aggression * 0.15
                )

            candidates.append(
                cls._candidate(
                    intention_type=(
                        'follow_scent_through_box'
                    ),
                    score=scent_score,
                    reasons=[
                        'recognized_scent_on_box',
                        'paired_quantum_box',
                        'scent_continues_cross_layer',
                        'curiosity',
                    ],
                    target=CatScentBoxTarget(
                        identity=identity,
                        box_id=(
                            best_scent_transfer
                            .box_id
                        ),
                        counterpart_box_id=(
                            best_scent_transfer
                            .counterpart_box_id
                        ),
                        source_layer=(
                            best_scent_transfer
                            .source_layer
                        ),
                        target_layer=(
                            best_scent_transfer
                            .target_layer
                        ),
                    ),
                )
            )

        intellect = CatIntellect.ensure_state(cat)
        intellect_normalized = float(intellect.normalized)
        counterpart_observation = (
            cat.current_quantum_counterpart_observation
        )

        if (
            counterpart_observation is not None
            and not isinstance(
                counterpart_observation,
                CatQuantumCounterpartObservation,
            )
        ):
            raise TypeError(
                'Quantum counterpart observation '
                'must be '
                'CatQuantumCounterpartObservation.'
            )

        if (
            isinstance(
                counterpart_observation,
                CatQuantumCounterpartObservation,
            )
            and counterpart_observation
            .pair_currently_valid
            and counterpart_observation.temporary
        ):
            source_box_id = (
                counterpart_observation
                .source_box_id
            )
            counterpart_box_id = (
                counterpart_observation
                .counterpart_box_id
            )
            if source_box_id is not None and counterpart_box_id is not None:
                quantum_memory_score = cls._quantum_travel_memory_score(cat)
                negative_quantum_memories = cat.memory.recall(event_type='quantum_box_layer_transfer_failed')
                travel_score = 0.3 + curiosity * 0.35 + courage * 0.2 + intellect_normalized * 0.15 + quantum_memory_score
                candidates.append(
                    cls._candidate(
                        intention_type=(
                            'travel_through_known_quantum_box'
                        ),
                        score=travel_score,
                        reasons=[
                            'quantum_counterpart_sensed',
                            'quantum_pair_currently_valid',
                            'curiosity',
                            'courage',
                            *(
                                [
                                    'negative_quantum_travel_memory'
                                ]
                                if negative_quantum_memories
                                else []
                            ),
                        ],
                        target=CatQuantumBoxTravelTarget(
                            source_box_id=source_box_id,
                            counterpart_box_id=(
                                counterpart_box_id
                            ),
                            source_layer=(
                                counterpart_observation
                                .source_layer
                            ),
                            target_layer=(
                                counterpart_observation
                                .counterpart_layer
                            ),
                            target_position=deepcopy(
                                counterpart_observation
                                .counterpart_position
                                or {}
                            ),
                        ),
                    )
                )
        for box_detail in observations.visible_box_details:
            if not box_detail.explored:
                continue
            if not box_detail.recognized_as_quantum_box:
                continue
            if not box_detail.paired:
                continue
            if box_detail.counterpart_known:
                continue
            if float(box_detail.distance) > 1e-09:
                continue
            quantum_travel_memories = cat.memory.recall(event_type='quantum_box_layer_transfer')
            quantum_travel_count = len(quantum_travel_memories)
            experienced_quantum_traveler = quantum_travel_count > 0
            quantum_experience_bonus = min(0.2, quantum_travel_count * 0.075)
            resonance_score = 0.3 + curiosity * 0.35 + intellect_normalized * 0.3 + quantum_experience_bonus
            candidates.append(
                cls._candidate(
                    intention_type=(
                        'sense_quantum_counterpart'
                    ),
                    score=resonance_score,
                    reasons=[
                        'quantum_box_explored',
                        'quantum_pair_resonance_possible',
                        'curiosity',
                        'intellect',
                        *(
                            [
                                'experienced_quantum_traveler'
                            ]
                            if experienced_quantum_traveler
                            else []
                        ),
                    ],
                    target=(
                        CatQuantumCounterpartSenseTarget(
                            box_id=box_detail.id,
                        )
                    ),
                )
            )
        boxes = observations.unexplored_boxes
        if boxes:
            explore_score = 0.25 + curiosity * 0.55 + courage * 0.1
            candidates.append(cls._candidate(intention_type='explore_box', score=explore_score, reasons=['unexplored_box_visible', 'curiosity'], target=CatExploreBoxTarget(box_id=boxes[0])))
        if not boxes and observations.can_create_exploration_pair:
            exploration_plan = observations.exploration_plan
            exploration_reasons = set(exploration_plan.reasons)
            explicit_goal_bonus = 0.5 if 'explicit_exploration_goal' in exploration_reasons else 0.0
            pair_score = 0.2 + curiosity * 0.55 + courage * 0.1 + patience * 0.05 + explicit_goal_bonus
            reasons = ['no_usable_box_visible', 'sufficient_energy', 'curiosity', 'quantum_pair_creation_possible']
            if explicit_goal_bonus > 0.0:
                reasons.append('explicit_exploration_goal')
            candidates.append(cls._candidate(intention_type='create_exploration_pair', score=pair_score, reasons=reasons, target=CatExplorationPairTarget(
                layer=(
                    observations
                    .exploration_destination_layer
                ),
                position=(
                    observations
                    .exploration_destination_position
                ),
                energy_cost=(
                    observations
                    .exploration_pair_energy_cost
                ),
            )))
        nearby_cats = observations.nearby_cats
        if nearby_cats:
            legend_count = int(observations.shareable_legend_count)
            if legend_count > 0:
                candidates.append(cls._candidate(intention_type='share_legend', score=0.25 + patience * 0.15 + curiosity * 0.15, reasons=['another_cat_nearby', 'shareable_knowledge_exists'], target=CatShareLegendTarget(listener_name=nearby_cats[0])))
        if nearby_cats:
            social_score = 0.2 + empathy * 0.5 + curiosity * 0.1
            candidates.append(cls._candidate(intention_type='approach_cat', score=social_score, reasons=['nearby_cat', 'empathy'], target=CatApproachCatTarget(cat_name=nearby_cats[0])))
        if observations.interesting_unknown:
            candidates.append(cls._candidate(intention_type='observe', score=0.2 + curiosity * 0.4 + patience * 0.2, reasons=['interesting_unknown', 'curiosity', 'patience']))
        needs = getattr(cat, 'needs', {})
        fatigue_need = float(getattr(needs, 'fatigue', 0.0))
        social_need = float(getattr(needs, 'social', 0.0))
        curiosity_need = float(getattr(needs, 'curiosity', 0.0))
        if nearby_cats and social_need > 0.0:
            candidates.append(cls._candidate(intention_type='approach_cat', score=0.18 + social_need * 0.72 + empathy * 0.1, reasons=['social_need', 'nearby_cat'], target=CatApproachCatTarget(cat_name=nearby_cats[0])))
        if getattr(cat, 'position', None) is not None:
            candidates.append(cls._candidate(intention_type='wander', score=0.12 + curiosity_need * 0.68 + curiosity * 0.12, reasons=['curiosity_need', 'autonomous_movement']))
        candidates.append(cls._candidate(intention_type='rest', score=0.15 + patience * 0.25 + fatigue_need * 0.65, reasons=['rest_is_available']))
        reached_scent = cat.known_scent_follow
        if (
            reached_scent is not None
            and not isinstance(
                reached_scent,
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
                reached_scent,
                CatKnownScentFollowState,
            )
            and reached_scent.arrived
        ):
            identity = reached_scent.identity
            direction = (
                reached_scent.trail_direction
            )

            if (
                direction is not None
                and not isinstance(
                    direction,
                    CatScentTrailDirection,
                )
            ):
                raise TypeError(
                    'Cat scent trail direction '
                    'must be '
                    'CatScentTrailDirection.'
                )

            target_smelt_now = any(
                item.recognition.recognized
                and item.recognition.identity == identity
                for item in observations.olfaction.detected_aromas
            )
            if (
                identity is not None
                and not target_smelt_now
                and isinstance(
                    direction,
                    CatScentTrailDirection,
                )
                and direction.inferred
            ):
                traits = cat.personality.traits
                curiosity = float(traits.curiosity)
                courage = float(traits.courage)
                previous_search = cat.scent_search

                if (
                    previous_search is not None
                    and not isinstance(
                        previous_search,
                        CatScentSearchState,
                    )
                ):
                    raise TypeError(
                        'Cat scent search state '
                        'must be '
                        'CatScentSearchState.'
                    )

                if (
                    isinstance(
                        previous_search,
                        CatScentSearchState,
                    )
                    and previous_search.identity
                    == identity
                    and previous_search.layer
                    == cat.current_layer
                ):
                    attempts = int(
                        previous_search.attempts
                    )
                else:
                    attempts = 0
                max_attempts = max(1, min(3, 1 + int(round(curiosity * 2.0))))
                if attempts < max_attempts:
                    direction_confidence = float(direction.confidence or 0.0)
                    search_distance = 1.0 + curiosity + courage * 0.5
                    search_score = 0.38 + curiosity * 0.18 + courage * 0.08 + direction_confidence * 0.2 - attempts * 0.08
                    candidates.append(
                        cls._candidate(
                            intention_type=(
                                'search_for_scent'
                            ),
                            score=search_score,
                            reasons=[
                                'last_known_scent_reached',
                                'target_scent_not_detected',
                                'trail_direction_inferred',
                                'local_search',
                            ],
                            target=CatScentSearchTarget(
                                identity=identity,
                                layer=cat.current_layer,
                                from_position=cat.position,
                                trail_direction=deepcopy(
                                    direction
                                ),
                                attempt=attempts + 1,
                                max_attempts=max_attempts,
                                search_distance=(
                                    search_distance
                                ),
                            ),
                        )
                    )
        candidates.sort(
            key=lambda item: item.score,
            reverse=True,
        )
        mind = cls.ensure_state(cat)
        mind.candidates = deepcopy(candidates)
        return deepcopy(candidates)

    @classmethod
    def decide(cls, cat, observations, quantum_roll=None, top_count=None):
        """
        Vybere vlastnĂ\xad Ăşmysl koÄŤky.

        Cat D20 zde neurÄŤuje seznam moĹľnostĂ\xad.
        Pouze vybere mezi nejlepĹˇĂ\xadmi
        rozumnĂ˝mi kandidĂˇty.
        """
        candidates = cls.consider(cat=cat, observations=observations)
        if not candidates:
            return {'name': 'cat_intention_not_selected', 'cat': cat.name, 'reason': 'no_candidates', 'selected': False}
        if top_count is None:
            top_count = CatIntellect.decision_finalist_count(cat=cat, candidate_count=len(candidates))
        else:
            top_count = max(1, int(top_count))
        finalists = candidates[:top_count]
        if quantum_roll is None:
            winner_index = 0
        else:
            quantum_roll = int(quantum_roll)
            if not 1 <= quantum_roll <= 20:
                raise ValueError('Cat quantum decision roll must be between 1 and 20.')
            winner_index = (quantum_roll - 1) * len(finalists) // 20
            winner_index = min(winner_index, len(finalists) - 1)
        winner = deepcopy(finalists[winner_index])
        mind = cls.ensure_state(cat)
        previous = mind.current_intention
        mind.previous_intention = deepcopy(previous)
        mind.current_intention = deepcopy(winner)
        mind.decision_count += 1
        event = {'name': 'cat_intention_selected', 'cat': cat.name, 'intention': winner.type, 'target': winner.target, 'score': winner.score, 'reasons': list(winner.reasons), 'quantum_roll': quantum_roll, 'intellect_score': CatIntellect.ensure_state(cat).score, 'intellect_category': CatIntellect.category(cat), 'finalist_count': len(finalists), 'finalists': deepcopy(finalists), 'previous_intention': deepcopy(previous), 'selected': True}
        mind.history.append(deepcopy(event))
        return event

    @classmethod
    def clear_intention(cls, cat, reason):
        mind = cls.ensure_state(cat)
        previous = mind.current_intention
        mind.previous_intention = deepcopy(previous)
        mind.current_intention = None
        event = {'name': 'cat_intention_cleared', 'cat': cat.name, 'previous_intention': deepcopy(previous), 'reason': reason, 'cleared': True}
        mind.history.append(deepcopy(event))
        return event

    @classmethod
    def _candidate(cls, intention_type, score, reasons, target=None):
        if intention_type not in cls.INTENTION_TYPES:
            raise ValueError(f'Unknown cat intention: {intention_type}')
        return CatIntentionCandidate(
            type=intention_type,
            target=target,
            score=score,
            reasons=reasons,
        )

    @classmethod
    def _quantum_failure_bar_score(cls, cat):
        memory = cat.memory
        if memory is None:
            return 0.0
        failures = memory.recall(event_type='quantum_box_layer_transfer_failed')
        return min(0.3, len(failures) * 0.1)

    @classmethod
    def _quantum_travel_memory_score(cls, cat):
        memory = cat.memory
        if memory is None:
            return 0.0
        successful = memory.recall(event_type='quantum_box_layer_transfer')
        failed = memory.recall(event_type='quantum_box_layer_transfer_failed')
        positive_bonus = min(0.2, len(successful) * 0.075)
        negative_penalty = min(0.3, len(failed) * 0.1)
        return positive_bonus - negative_penalty

    @classmethod
    def _bar_memory_score(cls, cat):
        memory = cat.memory
        if memory is None:
            return 0.0
        events = memory.records()
        positive_types = {'bar_entry', 'cat_drank_milk_at_bar', 'bouncer_petted_cat', 'safe_at_bar'}
        positive_count = sum((1 for event in events if event.event_type in positive_types))
        return min(0.3, positive_count * 0.06)
