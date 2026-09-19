from copy import deepcopy

from .cat_exploration_state import (
    CatAfterArrivalCandidate,
    CatAfterArrivalDecision,
    CatContinuationCandidate,
    CatContinuationPlan,
    CatExplorationCandidate,
    CatExplorationPlan,
    CatScentDestinationCandidate,
    CatScentDestinationPlan,
)


from .cat_exploration_goal import CatExplorationGoal

class CatExplorationPlanner:

    POSITIVE_MEMORY_TYPES = {
        "safe_at_bar",
        "bar_entry",
        "cat_drank_milk_at_bar",
        "box_explored",
        "quantum_box_layer_transfer",
        "stable_quantum_box_layer_transfer",
        "successful_exploration"
    }

    NEGATIVE_MEMORY_TYPES = {
        "dangerous_location",
        "cronenberg_attack",
        "failed_exploration",
        "quantum_transfer_interrupted"
    }

    DEFAULT_LAYER_POSITIONS = {
        "quantum_layer": {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        },
        "meeting_place": {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        }
    }

    @classmethod
    def choose_destination(
        cls,
        cat,
        universe
    ):
        current_layer = getattr(
            cat,
            "current_layer",
            "quantum_layer"
        )

        candidates = cls.collect_candidates(
            cat=cat,
            universe=universe
        )

        candidates = [
            candidate
            for candidate in candidates
            if candidate.layer
            != current_layer
        ]

        if not candidates:
            return CatExplorationPlan(
                selected=False,
                reason="no_other_layer_known",
                current_layer=current_layer,
            )

        scored = [
            cls._score_candidate(
                cat=cat,
                candidate=candidate
            )
            for candidate in candidates
        ]

        scored.sort(
            key=lambda item: (
                item.score,
                item.layer,
                repr(
                    item.position
                )
            ),
            reverse=True
        )

        winner = scored[0]

        return CatExplorationPlan(
            selected=True,
            layer=winner.layer,
            position=deepcopy(
                winner.position
            ),
            score=winner.score,
            reasons=list(
                winner.reasons
            ),
            candidate_count=len(
                scored
            ),
            candidates=deepcopy(
                scored
            ),
        )

    @classmethod
    def choose_scent_destination(
        cls,
        cat,
        preferred_identity=None,
        avoid_identity=None
    ):
        knowledge = cat.knowledge

        scent_places = list(
            knowledge.known_scent_places
        )

        if not scent_places:
            return CatScentDestinationPlan(
                selected=False,
                reason="no_known_scent_places",
            )

        current_layer = getattr(
            cat,
            "current_layer",
            None
        )

        candidates = []

        for place in scent_places:
            identity = place.identity

            if (
                preferred_identity
                is not None
                and identity
                != preferred_identity
            ):
                continue

            score = (
                float(
                    place.confidence
                ) * 0.45
                + min(
                    1.0,
                    float(
                        place.last_intensity
                    )
                ) * 0.35
            )

            if (
                place.layer
                == current_layer
            ):
                score += 0.20

            if (
                avoid_identity
                is not None
                and identity
                == avoid_identity
            ):
                score *= -1.0

            candidates.append(
                CatScentDestinationCandidate(
                    identity=identity,
                    layer=place.layer,
                    position=cls._position(
                        place.position
                    ),
                    source_id=place.source_id,
                    confidence=place.confidence,
                    last_intensity=(
                        place.last_intensity
                    ),
                    score=score,
                )
            )

        if not candidates:
            return CatScentDestinationPlan(
                selected=False,
                reason="no_matching_scent_place",
            )

        candidates.sort(
            key=lambda item: item.score,
            reverse=True
        )

        winner = candidates[0]

        return CatScentDestinationPlan(
            selected=True,
            identity=winner.identity,
            layer=winner.layer,
            position=deepcopy(
                winner.position
            ),
            source_id=winner.source_id,
            score=winner.score,
            candidates=deepcopy(
                candidates
            ),
        )

    @classmethod
    def choose_after_arrival(
        cls,
        cat,
        pair=None,
        quantum_roll=None
    ):
        """
        Ko?ka po dosa?en? pr?zkumn?ho c?le
        sama rozhodne, co d?l.

        Cat D20 pouze rozli?? mezi nejlep??mi
        rozumn?mi mo?nostmi.
        """
        traits = cat.personality.traits

        curiosity = float(
            traits.curiosity
        )

        courage = float(
            traits.courage
        )

        patience = float(
            traits.patience
        )

        intellect = float(
            cat.intellect.normalized
        )

        continue_score = (
            0.15
            + curiosity * 0.50
            + courage * 0.20
            + intellect * 0.10
        )

        rest_score = (
            0.20
            + patience * 0.45
            + (1.0 - courage) * 0.10
        )

        return_score = (
            0.15
            + (1.0 - curiosity) * 0.35
            + patience * 0.20
            + (1.0 - courage) * 0.20
        )

        if pair is None:
            return_score = 0.0

        candidates = [
            CatAfterArrivalCandidate(
                action="continue_exploration",
                score=min(
                    1.0,
                    continue_score
                ),
                reasons=[
                    "curiosity",
                    "courage",
                    "intellect",
                ],
            ),
            CatAfterArrivalCandidate(
                action="rest_at_destination",
                score=min(
                    1.0,
                    rest_score
                ),
                reasons=[
                    "patience",
                    "destination_reached",
                ],
            ),
            CatAfterArrivalCandidate(
                action=(
                    "return_via_exploration_pair"
                ),
                score=min(
                    1.0,
                    return_score
                ),
                reasons=[
                    "known_return_path",
                    "patience",
                    "risk_evaluation",
                ],
            ),
        ]

        candidates.sort(
            key=lambda item: item.score,
            reverse=True
        )

        finalists = candidates[:2]

        if quantum_roll is None:
            selected = finalists[0]

        else:
            roll = int(
                quantum_roll
            )

            if not 1 <= roll <= 20:
                raise ValueError(
                    "Cat quantum decision roll "
                    "must be between 1 and 20."
                )

            selected = (
                finalists[0]
                if roll <= 14
                else finalists[1]
            )

        return CatAfterArrivalDecision(
            selected=True,
            action=selected.action,
            score=selected.score,
            reasons=list(
                selected.reasons
            ),
            finalists=deepcopy(
                finalists
            ),
            quantum_roll=quantum_roll,
        )

    @classmethod
    def choose_continuation_destination(
        cls,
        cat,
        universe
    ):
        """
        Vybere dal?? bod pr?zkumu ve stejn?
        Quantum Layer.

        Nezakl?d? nov? mezivrstvov? p?r.
        """
        current = dict(
            getattr(
                cat,
                "position",
                {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            )
        )

        traits = cat.personality.traits

        curiosity = float(
            traits.curiosity
        )

        courage = float(
            traits.courage
        )

        intellect = float(
            cat.intellect.normalized
        )

        memory = cat.memory

        visited_positions = []

        for event in memory.records():
            if (
                event.event_type
                != "successful_exploration"
            ):
                continue

            details = event.details

            if details.get(
                "target_layer"
            ) != "quantum_layer":
                continue

            position = details.get(
                "position"
            )

            if isinstance(
                position,
                dict
            ):
                visited_positions.append(
                    cls._position(
                        position
                    )
                )

        # Vzd?lenost dal?? etapy je vlastnost
        # ko?ky, ne pevn? teleport.
        distance = (
            2.0
            + curiosity * 5.0
            + courage * 2.0
            + intellect * 1.0
        )

        directions = [
            (1.0, 0.0, 0.0),
            (-1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, -1.0, 0.0),
            (0.0, 0.0, 1.0),
            (0.0, 0.0, -1.0)
        ]

        candidates = []

        for index, direction in enumerate(
            directions
        ):
            position = {
                "x": (
                    float(
                        current.get(
                            "x",
                            0.0
                        )
                    )
                    + direction[0]
                    * distance
                ),
                "y": (
                    float(
                        current.get(
                            "y",
                            0.0
                        )
                    )
                    + direction[1]
                    * distance
                ),
                "z": (
                    float(
                        current.get(
                            "z",
                            0.0
                        )
                    )
                    + direction[2]
                    * distance
                )
            }

            revisit_penalty = 0.0

            for visited in visited_positions:
                difference = (
                    abs(
                        position["x"]
                        - visited["x"]
                    )
                    + abs(
                        position["y"]
                        - visited["y"]
                    )
                    + abs(
                        position["z"]
                        - visited["z"]
                    )
                )

                if difference < 1.0:
                    revisit_penalty += 0.40

            score = (
                0.30
                + curiosity * 0.40
                + courage * 0.15
                + intellect * 0.10
                - revisit_penalty
            )

            candidates.append(
                CatContinuationCandidate(
                    layer="quantum_layer",
                    position=position,
                    score=max(
                        0.0,
                        min(
                            1.0,
                            score
                        )
                    ),
                    direction_index=index,
                    revisit_penalty=(
                        revisit_penalty
                    ),
                )
            )

        candidates.sort(
            key=lambda item: (
                item.score,
                -item.direction_index
            ),
            reverse=True
        )

        winner = candidates[0]

        return CatContinuationPlan(
            selected=True,
            layer="quantum_layer",
            position=deepcopy(
                winner.position
            ),
            score=winner.score,
            reason=(
                "continue_quantum_exploration"
            ),
            candidates=deepcopy(
                candidates
            ),
        )

    @classmethod
    def collect_candidates(
        cls,
        cat,
        universe
    ):
        candidates = []

        explicit_goal = getattr(
            cat,
            "exploration_goal",
            None
        )

        if (
            explicit_goal is not None
            and not isinstance(
                explicit_goal,
                CatExplorationGoal,
            )
        ):
            raise TypeError(
                'Cat exploration goal '
                'must be CatExplorationGoal.'
            )

        if explicit_goal is not None:
            layer = explicit_goal.layer
            position = explicit_goal.position

            if layer is not None:
                candidates.append(
                    CatExplorationCandidate(
                        layer=str(
                            layer
                        ),
                        position=cls._position(
                            position
                        ),
                        source="explicit_goal",
                    )
                )

        for layer, position in (
            cls.DEFAULT_LAYER_POSITIONS.items()
        ):
            candidates.append(
                CatExplorationCandidate(
                    layer=layer,
                    position=deepcopy(
                        position
                    ),
                    source="default_layer",
                )
            )

        for box in getattr(
            universe,
            "quantum_boxes",
            []
        ):
            layer = getattr(
                box,
                "current_layer",
                None
            )

            if layer is None:
                continue

            candidates.append(
                CatExplorationCandidate(
                    layer=str(
                        layer
                    ),
                    position=cls._position(
                        getattr(
                            box,
                            "position",
                            None
                        )
                    ),
                    source="known_quantum_box",
                    box_id=getattr(
                        box,
                        "id",
                        None
                    ),
                )
            )

        memory = cat.memory

        for event in memory.records():
            details = event.details

            event_type = (
                event.event_type
            )

            layers = []

            for key in (
                "target_layer",
                "resolved_layer",
                "source_layer",
                "layer"
            ):
                value = details.get(
                    key
                )

                if value is not None:
                    layers.append(
                        str(
                            value
                        )
                    )

            location = (
                event.location
            )

            if isinstance(
                location,
                str
            ):
                layers.append(
                    location
                )

            position = cls._position(
                details.get(
                    "resolved_position",
                    details.get(
                        "position",
                        location
                    )
                )
            )

            for layer in layers:
                candidates.append(
                    CatExplorationCandidate(
                        layer=layer,
                        position=deepcopy(
                            position
                        ),
                        source="memory",
                        memory_type=event_type,
                        known_visits=1,
                        positive_memories=(
                            1
                            if event_type
                            in cls.POSITIVE_MEMORY_TYPES
                            else 0
                        ),
                        negative_memories=(
                            1
                            if event_type
                            in cls.NEGATIVE_MEMORY_TYPES
                            else 0
                        ),
                    )
                )

        knowledge = cat.knowledge

        for heard in knowledge.heard_legends:
            if heard.verified:
                continue

            if heard.contradicted:
                continue

            credibility = float(
                heard.credibility
            )

            if credibility < 0.35:
                continue

            layer = heard.layer
            position = heard.position

            if (
                layer is None
                or not isinstance(
                    position,
                    dict
                )
            ):
                continue

            candidates.append(
                CatExplorationCandidate(
                    layer=str(
                        layer
                    ),
                    position=cls._position(
                        position
                    ),
                    source="heard_legend",
                    legend_id=(
                        heard.legend_id
                    ),
                    storyteller=(
                        heard.storyteller
                    ),
                    legend_credibility=(
                        credibility
                    ),
                )
            )

        return cls._merge_candidates(
            candidates
        )

    @classmethod
    def _score_candidate(
        cls,
        cat,
        candidate
    ):
        if not isinstance(
            candidate,
            CatExplorationCandidate,
        ):
            raise TypeError(
                "Exploration candidate must be "
                "CatExplorationCandidate."
            )

        traits = cat.personality.traits

        curiosity = float(
            traits.curiosity
        )

        courage = float(
            traits.courage
        )

        patience = float(
            traits.patience
        )

        intellect = float(
            cat.intellect.normalized
        )

        visits = int(
            candidate.known_visits
        )

        positive = int(
            candidate.positive_memories
        )

        negative = int(
            candidate.negative_memories
        )

        novelty = 1.0 / (
            1.0 + visits
        )

        score = (
            0.20
            + curiosity
            * novelty
            * 0.35
            + courage * 0.15
            + patience * 0.05
            + intellect * 0.10
            + positive * 0.10
            - negative * (
                0.20
                - courage * 0.10
            )
        )

        reasons = [
            "exploration_possible",
            "curiosity",
            "courage",
            "intellect"
        ]

        if visits == 0:
            reasons.append(
                "unknown_layer"
            )
        else:
            reasons.append(
                "known_from_memory"
            )

        if positive:
            reasons.append(
                "positive_memory"
            )

        if negative:
            reasons.append(
                "dangerous_memory"
            )

        if (
            candidate.source
            == "heard_legend"
        ):
            credibility = float(
                candidate.legend_credibility
                or 0.0
            )

            score += (
                credibility * 0.20
            )

            reasons.append(
                "heard_cat_legend"
            )

            reasons.append(
                "legend_credibility"
            )

        if (
            candidate.source
            == "explicit_goal"
        ):
            score += 0.35

            reasons.append(
                "explicit_exploration_goal"
            )

        scored = deepcopy(
            candidate
        )

        scored.score = max(
            0.0,
            min(
                1.0,
                score
            )
        )

        scored.reasons = reasons

        return scored

    @classmethod
    def _merge_candidates(
        cls,
        candidates
    ):
        merged = {}

        for candidate in candidates:
            if not isinstance(
                candidate,
                CatExplorationCandidate,
            ):
                raise TypeError(
                    "Exploration candidates must be "
                    "CatExplorationCandidate objects."
                )

            key = (
                candidate.layer,
                tuple(
                    sorted(
                        candidate
                        .position
                        .items()
                    )
                )
            )

            if key not in merged:
                merged[key] = deepcopy(
                    candidate
                )

                continue

            existing = merged[key]

            existing.known_visits += int(
                candidate.known_visits
            )

            existing.positive_memories += int(
                candidate.positive_memories
            )

            existing.negative_memories += int(
                candidate.negative_memories
            )

            if (
                candidate.source
                == "explicit_goal"
            ):
                existing.source = (
                    "explicit_goal"
                )

        return list(
            merged.values()
        )

    @staticmethod
    def _position(
        value
    ):
        if not isinstance(
            value,
            dict
        ):
            return {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }

        return {
            "x": float(
                value.get(
                    "x",
                    0.0
                )
            ),
            "y": float(
                value.get(
                    "y",
                    0.0
                )
            ),
            "z": float(
                value.get(
                    "z",
                    0.0
                )
            )
        }
