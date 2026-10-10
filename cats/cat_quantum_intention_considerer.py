from copy import deepcopy

from cats.cat_intellect import (
    CatIntellect,
)
from cats.cat_intention_state import (
    CatExploreBoxTarget,
    CatExplorationPairTarget,
    CatIntentionCandidate,
    CatQuantumBoxTravelTarget,
    CatQuantumCounterpartSenseTarget,
)
from cats.cat_quantum_observation_state import (
    CatQuantumCounterpartObservation,
)


class CatQuantumIntentionConsiderer:

    @staticmethod
    def _candidate(
        intention_type,
        score,
        reasons,
        target=None,
    ):
        return CatIntentionCandidate(
            type=intention_type,
            target=target,
            score=score,
            reasons=reasons,
        )

    @staticmethod
    def _travel_memory_score(
        cat,
    ):
        memory = cat.memory

        if memory is None:
            return 0.0

        successful = memory.recall(
            event_type=(
                "quantum_box_layer_transfer"
            )
        )

        failed = memory.recall(
            event_type=(
                "quantum_box_layer_transfer_failed"
            )
        )

        positive_bonus = min(
            0.2,
            len(successful)
            * 0.075,
        )

        negative_penalty = min(
            0.3,
            len(failed)
            * 0.1,
        )

        return (
            positive_bonus
            - negative_penalty
        )

    def candidates(
        self,
        cat,
        observations,
    ):
        traits = (
            cat.personality.traits
        )

        curiosity = float(
            traits.curiosity
        )

        courage = float(
            traits.courage
        )

        patience = float(
            traits.patience
        )

        candidates = []

        intellect = (
            CatIntellect
            .ensure_state(
                cat
            )
        )

        intellect_normalized = float(
            intellect.normalized
        )

        counterpart_observation = (
            cat
            .current_quantum_counterpart_observation
        )

        if (
            counterpart_observation
            is not None
            and not isinstance(
                counterpart_observation,
                CatQuantumCounterpartObservation,
            )
        ):
            raise TypeError(
                "Quantum counterpart observation "
                "must be "
                "CatQuantumCounterpartObservation."
            )

        if (
            isinstance(
                counterpart_observation,
                CatQuantumCounterpartObservation,
            )
            and (
                counterpart_observation
                .pair_currently_valid
            )
            and (
                counterpart_observation
                .temporary
            )
        ):
            source_box_id = (
                counterpart_observation
                .source_box_id
            )

            counterpart_box_id = (
                counterpart_observation
                .counterpart_box_id
            )

            if (
                source_box_id is not None
                and counterpart_box_id
                is not None
            ):
                quantum_memory_score = (
                    self
                    ._travel_memory_score(
                        cat
                    )
                )

                negative_quantum_memories = (
                    cat.memory.recall(
                        event_type=(
                            "quantum_box_layer_transfer_failed"
                        )
                    )
                )

                travel_score = (
                    0.3
                    + curiosity * 0.35
                    + courage * 0.2
                    + intellect_normalized
                    * 0.15
                    + quantum_memory_score
                )

                candidates.append(
                    self._candidate(
                        intention_type=(
                            "travel_through_known_quantum_box"
                        ),
                        score=
                            travel_score,
                        reasons=[
                            "quantum_counterpart_sensed",
                            "quantum_pair_currently_valid",
                            "curiosity",
                            "courage",
                            *(
                                [
                                    "negative_quantum_travel_memory"
                                ]
                                if (
                                    negative_quantum_memories
                                )
                                else []
                            ),
                        ],
                        target=(
                            CatQuantumBoxTravelTarget(
                                source_box_id=
                                    source_box_id,
                                counterpart_box_id=
                                    counterpart_box_id,
                                source_layer=(
                                    counterpart_observation
                                    .source_layer
                                ),
                                target_layer=(
                                    counterpart_observation
                                    .counterpart_layer
                                ),
                                target_position=
                                    deepcopy(
                                        counterpart_observation
                                        .counterpart_position
                                    ),
                            )
                        ),
                    )
                )

        for box_detail in (
            observations
            .visible_box_details
        ):
            if not box_detail.explored:
                continue

            if not (
                box_detail
                .recognized_as_quantum_box
            ):
                continue

            if not box_detail.paired:
                continue

            if (
                box_detail
                .counterpart_known
            ):
                continue

            if (
                float(
                    box_detail.distance
                )
                > 1e-09
            ):
                continue

            quantum_travel_memories = (
                cat.memory.recall(
                    event_type=(
                        "quantum_box_layer_transfer"
                    )
                )
            )

            quantum_travel_count = len(
                quantum_travel_memories
            )

            experienced_quantum_traveler = (
                quantum_travel_count > 0
            )

            quantum_experience_bonus = min(
                0.2,
                quantum_travel_count
                * 0.075,
            )

            resonance_score = (
                0.3
                + curiosity * 0.35
                + intellect_normalized
                * 0.3
                + quantum_experience_bonus
            )

            candidates.append(
                self._candidate(
                    intention_type=(
                        "sense_quantum_counterpart"
                    ),
                    score=
                        resonance_score,
                    reasons=[
                        "quantum_box_explored",
                        "quantum_pair_resonance_possible",
                        "curiosity",
                        "intellect",
                        *(
                            [
                                "experienced_quantum_traveler"
                            ]
                            if (
                                experienced_quantum_traveler
                            )
                            else []
                        ),
                    ],
                    target=(
                        CatQuantumCounterpartSenseTarget(
                            box_id=
                                box_detail.id,
                        )
                    ),
                )
            )

        boxes = (
            observations.unexplored_boxes
        )

        if boxes:
            explore_score = (
                0.25
                + curiosity * 0.55
                + courage * 0.1
            )

            candidates.append(
                self._candidate(
                    intention_type=(
                        "explore_box"
                    ),
                    score=
                        explore_score,
                    reasons=[
                        "unexplored_box_visible",
                        "curiosity",
                    ],
                    target=(
                        CatExploreBoxTarget(
                            box_id=
                                boxes[0],
                        )
                    ),
                )
            )

        if (
            not boxes
            and observations
            .can_create_exploration_pair
        ):
            exploration_plan = (
                observations
                .exploration_plan
            )

            exploration_reasons = set(
                exploration_plan.reasons
            )

            explicit_goal_bonus = (
                0.5
                if (
                    "explicit_exploration_goal"
                    in exploration_reasons
                )
                else 0.0
            )

            pair_score = (
                0.2
                + curiosity * 0.55
                + courage * 0.1
                + patience * 0.05
                + explicit_goal_bonus
            )

            reasons = [
                "no_usable_box_visible",
                "sufficient_energy",
                "curiosity",
                "quantum_pair_creation_possible",
            ]

            if explicit_goal_bonus > 0.0:
                reasons.append(
                    "explicit_exploration_goal"
                )

            candidates.append(
                self._candidate(
                    intention_type=(
                        "create_exploration_pair"
                    ),
                    score=
                        pair_score,
                    reasons=
                        reasons,
                    target=(
                        CatExplorationPairTarget(
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
                        )
                    ),
                )
            )

        return candidates
