from copy import deepcopy

from cats.cat_components import CatMindState
from cats.cat_intellect import CatIntellect
from cats.cat_intention_state import (
    CatApproachCatTarget,
    CatIntentionCandidate,
    CatShareLegendTarget,
    CatVisitRecipientTarget,
)
from cats.cat_perception_state import (
    CatPerceptionState,
)
from cats.cat_quantum_intention_considerer import (
    CatQuantumIntentionConsiderer,
)
from cats.cat_scent_intention_considerer import (
    CatScentIntentionConsiderer,
)

from cats.cat_mind_result_state import (
    CatIntentionNotSelectedResult,
    CatIntentionSelectedEvent,
)

class CatMind:
    INTENTION_TYPES = ('visit_bar', 'visit_recipient', 'hunt_cronenberg', 'track_cronenberg_scent', 'follow_known_scent', 'search_for_scent', 'follow_scent_through_box', 'avoid_cronenberg_scent', 'explore_box', 'sense_quantum_counterpart', 'travel_through_known_quantum_box', 'travel_trough_known_quantum_box', 'create_exploration_pair', 'approach_cat', 'share_legend', 'observe', 'wander', 'rest')

    SCENT_CONSIDERER = (
        CatScentIntentionConsiderer()
    )

    QUANTUM_CONSIDERER = (
        CatQuantumIntentionConsiderer()
    )

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
    def consider(
        cls,
        cat,
        observations,
    ):
        """
        Create possible intentions.

        This phase does not execute an action
        and does not select a winner.
        """
        if not isinstance(
            observations,
            CatPerceptionState,
        ):
            raise TypeError(
                "CatMind observations must be "
                "CatPerceptionState."
            )

        traits = (
            cat.personality.traits
        )

        curiosity = float(
            traits.curiosity
        )

        courage = float(
            traits.courage
        )

        aggression = float(
            traits.aggression
        )

        empathy = float(
            traits.empathy
        )

        patience = float(
            traits.patience
        )

        candidates = []

        if observations.bar_known:
            bar_score = 0.45

            if observations.bar_visible:
                bar_score += 0.1

            bar_memory_score = (
                cls._bar_memory_score(
                    cat
                )
            )

            bar_score += (
                bar_memory_score
            )

            quantum_failure_bar_score = (
                cls
                ._quantum_failure_bar_score(
                    cat
                )
            )

            bar_score += (
                quantum_failure_bar_score
            )

            reasons = [
                "bar_known",
            ]

            if observations.bar_visible:
                reasons.append(
                    "bar_visible"
                )

            if bar_memory_score > 0:
                reasons.append(
                    "positive_bar_memory"
                )

            if (
                quantum_failure_bar_score
                > 0
            ):
                reasons.append(
                    "seeking_safety_after_quantum_failure"
                )

            candidates.append(
                cls._candidate(
                    intention_type=
                        "visit_bar",
                    score=
                        bar_score,
                    reasons=
                        reasons,
                )
            )

        recipient = cat.recipient

        if recipient is not None:
            recipient_score = (
                0.25
                + empathy * 0.3
                + curiosity * 0.1
                + patience * 0.05
            )

            candidates.append(
                cls._candidate(
                    intention_type=(
                        "visit_recipient"
                    ),
                    score=
                        recipient_score,
                    reasons=[
                        "assigned_recipient",
                        "empathy",
                        "curiosity",
                    ],
                    target=(
                        CatVisitRecipientTarget(
                            recipient_id=
                                recipient,
                        )
                    ),
                )
            )

        huntable = (
            observations
            .huntable_cronenbergs
        )

        if huntable:
            danger = float(
                observations
                .cronenberg_danger
            )

            hunt_score = (
                0.25
                + courage * 0.3
                + aggression * 0.25
                + curiosity * 0.1
                - danger * 0.2
            )

            candidates.append(
                cls._candidate(
                    intention_type=(
                        "hunt_cronenberg"
                    ),
                    score=
                        hunt_score,
                    reasons=[
                        "huntable_cronenberg_visible",
                        "courage",
                        "aggression",
                    ],
                    target=
                        huntable[0],
                )
            )

        candidates.extend(
            cls.SCENT_CONSIDERER
            .navigation_candidates(
                cat=cat,
                observations=
                    observations,
            )
        )

        candidates.extend(
            cls.QUANTUM_CONSIDERER
            .candidates(
                cat=cat,
                observations=
                    observations,
            )
        )

        nearby_cats = (
            observations.nearby_cats
        )

        if nearby_cats:
            legend_count = int(
                observations
                .shareable_legend_count
            )

            if legend_count > 0:
                candidates.append(
                    cls._candidate(
                        intention_type=(
                            "share_legend"
                        ),
                        score=(
                            0.25
                            + patience * 0.15
                            + curiosity * 0.15
                        ),
                        reasons=[
                            "another_cat_nearby",
                            "shareable_knowledge_exists",
                        ],
                        target=(
                            CatShareLegendTarget(
                                listener_name=
                                    nearby_cats[0],
                            )
                        ),
                    )
                )

        if nearby_cats:
            social_score = (
                0.2
                + empathy * 0.5
                + curiosity * 0.1
            )

            candidates.append(
                cls._candidate(
                    intention_type=(
                        "approach_cat"
                    ),
                    score=
                        social_score,
                    reasons=[
                        "nearby_cat",
                        "empathy",
                    ],
                    target=(
                        CatApproachCatTarget(
                            cat_name=
                                nearby_cats[0],
                        )
                    ),
                )
            )

        if observations.interesting_unknown:
            candidates.append(
                cls._candidate(
                    intention_type=
                        "observe",
                    score=(
                        0.2
                        + curiosity * 0.4
                        + patience * 0.2
                    ),
                    reasons=[
                        "interesting_unknown",
                        "curiosity",
                        "patience",
                    ],
                )
            )

        needs = cat.needs

        fatigue_need = float(
            getattr(
                needs,
                "fatigue",
                0.0,
            )
        )

        social_need = float(
            getattr(
                needs,
                "social",
                0.0,
            )
        )

        curiosity_need = float(
            getattr(
                needs,
                "curiosity",
                0.0,
            )
        )

        if (
            nearby_cats
            and social_need > 0.0
        ):
            candidates.append(
                cls._candidate(
                    intention_type=(
                        "approach_cat"
                    ),
                    score=(
                        0.18
                        + social_need
                        * 0.72
                        + empathy * 0.1
                    ),
                    reasons=[
                        "social_need",
                        "nearby_cat",
                    ],
                    target=(
                        CatApproachCatTarget(
                            cat_name=
                                nearby_cats[0],
                        )
                    ),
                )
            )

        if cat.position is not None:
            candidates.append(
                cls._candidate(
                    intention_type=
                        "wander",
                    score=(
                        0.12
                        + curiosity_need
                        * 0.68
                        + curiosity * 0.12
                    ),
                    reasons=[
                        "curiosity_need",
                        "autonomous_movement",
                    ],
                )
            )

        candidates.append(
            cls._candidate(
                intention_type=
                    "rest",
                score=(
                    0.15
                    + patience * 0.25
                    + fatigue_need * 0.65
                ),
                reasons=[
                    "rest_is_available",
                ],
            )
        )

        candidates.extend(
            cls.SCENT_CONSIDERER
            .search_candidates(
                cat=cat,
                observations=
                    observations,
            )
        )

        candidates.sort(
            key=lambda item: (
                item.score
            ),
            reverse=True,
        )

        mind = cls.ensure_state(
            cat
        )

        mind.candidates = deepcopy(
            candidates
        )

        return deepcopy(
            candidates
        )

    @classmethod
    def decide(
        cls,
        cat,
        observations,
        quantum_roll=None,
        top_count=None,
    ):
        candidates = cls.consider(
            cat=cat,
            observations=observations,
        )

        if not candidates:
            return (
                CatIntentionNotSelectedResult(
                    cat=cat.name,
                    reason="no_candidates",
                )
            )

        if top_count is None:
            top_count = (
                CatIntellect
                .decision_finalist_count(
                    cat=cat,
                    candidate_count=len(
                        candidates
                    ),
                )
            )

        else:
            top_count = max(
                1,
                int(
                    top_count
                ),
            )

        finalists = tuple(
            deepcopy(
                candidates[
                    :top_count
                ]
            )
        )

        if quantum_roll is None:
            winner_index = 0

        else:
            quantum_roll = int(
                quantum_roll
            )

            if not (
                1
                <= quantum_roll
                <= 20
            ):
                raise ValueError(
                    "Cat quantum decision roll "
                    "must be between 1 and 20."
                )

            winner_index = (
                (quantum_roll - 1)
                * len(finalists)
                // 20
            )

            winner_index = min(
                winner_index,
                len(finalists) - 1,
            )

        winner = deepcopy(
            finalists[
                winner_index
            ]
        )

        mind = cls.ensure_state(
            cat
        )

        previous = (
            mind.current_intention
        )

        mind.previous_intention = (
            deepcopy(
                previous
            )
        )

        mind.current_intention = (
            deepcopy(
                winner
            )
        )

        mind.decision_count += 1

        intellect = (
            CatIntellect
            .ensure_state(
                cat
            )
        )

        event = (
            CatIntentionSelectedEvent(
                cat=cat.name,
                intention=
                    winner.type,
                target=deepcopy(
                    winner.target
                ),
                score=
                    winner.score,
                reasons=tuple(
                    winner.reasons
                ),
                quantum_roll=
                    quantum_roll,
                intellect_score=
                    intellect.score,
                intellect_category=
                    CatIntellect.category(
                        cat
                    ),
                finalists=tuple(
                    deepcopy(
                        finalists
                    )
                ),
                previous_intention=
                    deepcopy(
                        previous
                    ),
            )
        )

        mind.history.append(
            deepcopy(
                event
            )
        )

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
    def _bar_memory_score(cls, cat):
        memory = cat.memory
        if memory is None:
            return 0.0
        events = memory.records()
        positive_types = {'bar_entry', 'cat_drank_milk_at_bar', 'bouncer_petted_cat', 'safe_at_bar'}
        positive_count = sum((1 for event in events if event.event_type in positive_types))
        return min(0.3, positive_count * 0.06)
