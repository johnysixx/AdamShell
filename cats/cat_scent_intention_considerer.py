from copy import deepcopy
from dataclasses import dataclass

from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatKnownScentTarget,
    CatScentBoxTarget,
    CatScentSearchTarget,
)
from cats.cat_knowledge import CatKnowledge
from cats.cat_perception_state import (
    CatScentTransferCandidate,
)
from cats.cat_scent_direction_state import (
    CatScentTrailDirection,
)
from cats.cat_scent_navigation_state import (
    CatKnownScentFollowState,
    CatScentSearchState,
)


@dataclass(
    slots=True,
    frozen=True,
)
class CatKnownScentPlaceCandidate:
    memory: object
    age_ticks: int
    freshness: float


class CatScentIntentionConsiderer:

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

    def navigation_candidates(
        self,
        cat,
        observations,
    ):
        traits = cat.personality.traits

        curiosity = float(
            traits.curiosity
        )

        courage = float(
            traits.courage
        )

        aggression = float(
            traits.aggression
        )

        patience = float(
            traits.patience
        )

        candidates = []

        if (
            observations
            .cronenberg_scent_recognized
            and not observations
            .visible_cronenbergs
        ):
            scent_track_score = (
                0.15
                + courage * 0.35
                + aggression * 0.3
                + curiosity * 0.2
            )

            scent_avoid_score = (
                0.15
                + (1.0 - courage) * 0.45
                + patience * 0.25
                + (1.0 - aggression) * 0.15
            )

            candidates.append(
                self._candidate(
                    intention_type=(
                        "track_cronenberg_scent"
                    ),
                    score=
                        scent_track_score,
                    reasons=[
                        "recognized_cronenberg_scent",
                        "cronenberg_not_visible",
                        "courage",
                        "aggression",
                        "curiosity",
                    ],
                )
            )

            if observations.bar_known:
                candidates.append(
                    self._candidate(
                        intention_type=(
                            "avoid_cronenberg_scent"
                        ),
                        score=
                            scent_avoid_score,
                        reasons=[
                            "recognized_cronenberg_scent",
                            "cronenberg_not_visible",
                            "low_courage",
                            "patience",
                            "known_safe_bar",
                        ],
                    )
                )

        scent_places = (
            cat.knowledge
            .known_scent_places
        )

        current_layer = (
            cat.current_layer
        )

        knowledge = (
            cat.knowledge
        )

        current_tick = (
            knowledge.scent_clock_tick
        )

        local_scent_places = []

        for place in scent_places:
            if (
                place.layer
                != current_layer
            ):
                continue

            last_seen_tick = (
                place.last_seen_tick
            )

            if (
                current_tick is None
                or last_seen_tick is None
            ):
                age_ticks = 0

            else:
                age_ticks = max(
                    0,
                    int(current_tick)
                    - int(last_seen_tick),
                )

            freshness = (
                0.5
                ** (
                    age_ticks
                    / 50.0
                )
            )

            if freshness < 0.05:
                continue

            local_scent_places.append(
                CatKnownScentPlaceCandidate(
                    memory=place,
                    age_ticks=
                        age_ticks,
                    freshness=
                        freshness,
                )
            )

        reached_scent = (
            cat.known_scent_follow
        )

        if (
            reached_scent is not None
            and not isinstance(
                reached_scent,
                CatKnownScentFollowState,
            )
        ):
            raise TypeError(
                "Cat known scent follow state "
                "must be "
                "CatKnownScentFollowState."
            )

        currently_smelt_identities = {
            item.recognition.identity
            for item
            in (
                observations
                .olfaction
                .detected_aromas
            )
            if (
                item.recognition
                .recognized
            )
        }

        if (
            isinstance(
                reached_scent,
                CatKnownScentFollowState,
            )
            and reached_scent.arrived
            and (
                reached_scent.identity
                not in
                currently_smelt_identities
            )
        ):
            local_scent_places = []

        if local_scent_places:
            strongest = max(
                local_scent_places,
                key=lambda item: (
                    (
                        float(
                            item.memory
                            .confidence
                        )
                        + min(
                            1.0,
                            float(
                                item.memory
                                .last_intensity
                            ),
                        )
                    )
                    * float(
                        item.freshness
                    )
                ),
            )

            memory = (
                strongest.memory
            )

            identity = (
                memory.identity
            )

            if identity not in (
                None,
                "unknown_aroma",
                "cronenberg",
            ):
                scent_direction = (
                    CatKnowledge
                    .infer_scent_direction(
                        cat=cat,
                        identity=
                            identity,
                        layer=
                            current_layer,
                    )
                )

                candidates.append(
                    self._candidate(
                        intention_type=(
                            "follow_known_scent"
                        ),
                        score=(
                            0.15
                            + curiosity * 0.25
                            + courage * 0.1
                            + float(
                                memory
                                .confidence
                            ) * 0.25
                        ),
                        reasons=[
                            "known_scent_place",
                            "recognized_identity",
                            "curiosity",
                        ],
                        target=(
                            CatKnownScentTarget(
                                identity=
                                    identity,
                                layer=
                                    memory.layer,
                                position=
                                    deepcopy(
                                        memory
                                        .position
                                    ),
                                source_id=
                                    memory
                                    .source_id,
                                age_ticks=
                                    strongest
                                    .age_ticks,
                                freshness=
                                    strongest
                                    .freshness,
                                trail_direction=
                                    deepcopy(
                                        scent_direction
                                    ),
                            )
                        ),
                    )
                )

        scent_transfers = (
            observations
            .scent_transfer_candidates
        )

        for scent_transfer in (
            scent_transfers
        ):
            if not isinstance(
                scent_transfer,
                CatScentTransferCandidate,
            ):
                raise TypeError(
                    "Scent transfer candidate "
                    "must be "
                    "CatScentTransferCandidate."
                )

        if scent_transfers:
            best_scent_transfer = max(
                scent_transfers,
                key=lambda item: float(
                    item.similarity
                ),
            )

            identity = (
                best_scent_transfer
                .identity
            )

            scent_score = (
                0.2
                + curiosity * 0.3
                + courage * 0.2
                + float(
                    best_scent_transfer
                    .similarity
                ) * 0.25
            )

            if identity == "cronenberg":
                scent_score += (
                    aggression * 0.15
                )

            candidates.append(
                self._candidate(
                    intention_type=(
                        "follow_scent_through_box"
                    ),
                    score=
                        scent_score,
                    reasons=[
                        "recognized_scent_on_box",
                        "paired_quantum_box",
                        "scent_continues_cross_layer",
                        "curiosity",
                    ],
                    target=(
                        CatScentBoxTarget(
                            identity=
                                identity,
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
                        )
                    ),
                )
            )

        return candidates

    def search_candidates(
        self,
        cat,
        observations,
    ):
        reached_scent = (
            cat.known_scent_follow
        )

        if (
            reached_scent is not None
            and not isinstance(
                reached_scent,
                CatKnownScentFollowState,
            )
        ):
            raise TypeError(
                "Cat known scent follow state "
                "must be "
                "CatKnownScentFollowState."
            )

        if not (
            isinstance(
                reached_scent,
                CatKnownScentFollowState,
            )
            and reached_scent.arrived
        ):
            return []

        identity = (
            reached_scent.identity
        )

        direction = (
            reached_scent
            .trail_direction
        )

        if (
            direction is not None
            and not isinstance(
                direction,
                CatScentTrailDirection,
            )
        ):
            raise TypeError(
                "Cat scent trail direction "
                "must be "
                "CatScentTrailDirection."
            )

        target_smelt_now = any(
            (
                item.recognition
                .recognized
            )
            and (
                item.recognition
                .identity
                == identity
            )
            for item
            in (
                observations
                .olfaction
                .detected_aromas
            )
        )

        if not (
            identity is not None
            and not target_smelt_now
            and isinstance(
                direction,
                CatScentTrailDirection,
            )
            and direction.inferred
        ):
            return []

        traits = (
            cat.personality.traits
        )

        curiosity = float(
            traits.curiosity
        )

        courage = float(
            traits.courage
        )

        previous_search = (
            cat.scent_search
        )

        if (
            previous_search is not None
            and not isinstance(
                previous_search,
                CatScentSearchState,
            )
        ):
            raise TypeError(
                "Cat scent search state "
                "must be "
                "CatScentSearchState."
            )

        if (
            isinstance(
                previous_search,
                CatScentSearchState,
            )
            and (
                previous_search.identity
                == identity
            )
            and (
                previous_search.layer
                == cat.current_layer
            )
        ):
            attempts = int(
                previous_search
                .attempts
            )

        else:
            attempts = 0

        max_attempts = max(
            1,
            min(
                3,
                1
                + int(
                    round(
                        curiosity * 2.0
                    )
                ),
            ),
        )

        if attempts >= max_attempts:
            return []

        direction_confidence = float(
            direction.confidence
            or 0.0
        )

        search_distance = (
            1.0
            + curiosity
            + courage * 0.5
        )

        search_score = (
            0.38
            + curiosity * 0.18
            + courage * 0.08
            + direction_confidence * 0.2
            - attempts * 0.08
        )

        return [
            self._candidate(
                intention_type=(
                    "search_for_scent"
                ),
                score=
                    search_score,
                reasons=[
                    "last_known_scent_reached",
                    "target_scent_not_detected",
                    "trail_direction_inferred",
                    "local_search",
                ],
                target=(
                    CatScentSearchTarget(
                        identity=
                            identity,
                        layer=
                            cat.current_layer,
                        from_position=
                            cat.position,
                        trail_direction=
                            deepcopy(
                                direction
                            ),
                        attempt=
                            attempts + 1,
                        max_attempts=
                            max_attempts,
                        search_distance=
                            search_distance,
                    )
                ),
            )
        ]
