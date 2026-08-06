from copy import deepcopy


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
        current_layer = cat.get(
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
            if candidate["layer"] != current_layer
        ]

        if not candidates:
            return {
                "selected": False,
                "reason": "no_other_layer_known",
                "current_layer": current_layer,
                "candidates": []
            }

        scored = [
            cls._score_candidate(
                cat=cat,
                candidate=candidate
            )
            for candidate in candidates
        ]

        scored.sort(
            key=lambda item: (
                item["score"],
                item["layer"],
                repr(item["position"])
            ),
            reverse=True
        )

        winner = deepcopy(
            scored[0]
        )

        return {
            "selected": True,
            "layer": winner["layer"],
            "position": deepcopy(
                winner["position"]
            ),
            "score": winner["score"],
            "reasons": list(
                winner["reasons"]
            ),
            "candidate_count": len(
                scored
            ),
            "candidates": deepcopy(
                scored
            )
        }

    @classmethod
    def collect_candidates(
        cls,
        cat,
        universe
    ):
        candidates = []

        explicit_goal = cat.get(
            "exploration_goal"
        )

        if isinstance(
            explicit_goal,
            dict
        ):
            layer = explicit_goal.get(
                "layer"
            )

            position = explicit_goal.get(
                "position"
            )

            if layer is not None:
                candidates.append({
                    "layer": str(layer),
                    "position": cls._position(
                        position
                    ),
                    "source": "explicit_goal",
                    "known_visits": 0,
                    "positive_memories": 0,
                    "negative_memories": 0
                })

        for layer, position in (
            cls.DEFAULT_LAYER_POSITIONS.items()
        ):
            candidates.append({
                "layer": layer,
                "position": deepcopy(
                    position
                ),
                "source": "default_layer",
                "known_visits": 0,
                "positive_memories": 0,
                "negative_memories": 0
            })

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

            candidates.append({
                "layer": str(layer),
                "position": cls._position(
                    getattr(
                        box,
                        "position",
                        None
                    )
                ),
                "source": "known_quantum_box",
                "box_id": getattr(
                    box,
                    "id",
                    None
                ),
                "known_visits": 0,
                "positive_memories": 0,
                "negative_memories": 0
            })

        memory = cat.get(
            "memory"
        )

        for event in getattr(
            memory,
            "events",
            []
        ):
            details = event.get(
                "details",
                {}
            )

            event_type = event.get(
                "event_type"
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
                        str(value)
                    )

            location = event.get(
                "location"
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
                candidates.append({
                    "layer": layer,
                    "position": deepcopy(
                        position
                    ),
                    "source": "memory",
                    "memory_type": event_type,
                    "known_visits": 1,
                    "positive_memories": (
                        1
                        if event_type
                        in cls.POSITIVE_MEMORY_TYPES
                        else 0
                    ),
                    "negative_memories": (
                        1
                        if event_type
                        in cls.NEGATIVE_MEMORY_TYPES
                        else 0
                    )
                })

        return cls._merge_candidates(
            candidates
        )

    @classmethod
    def _score_candidate(
        cls,
        cat,
        candidate
    ):
        traits = cat.get(
            "personality",
            {}
        ).get(
            "traits",
            {}
        )

        curiosity = float(
            traits.get(
                "curiosity",
                0.5
            )
        )

        courage = float(
            traits.get(
                "courage",
                0.5
            )
        )

        patience = float(
            traits.get(
                "patience",
                0.5
            )
        )

        intellect = float(
            cat.get(
                "intellect",
                {}
            ).get(
                "normalized",
                0.5
            )
        )

        visits = int(
            candidate.get(
                "known_visits",
                0
            )
        )

        positive = int(
            candidate.get(
                "positive_memories",
                0
            )
        )

        negative = int(
            candidate.get(
                "negative_memories",
                0
            )
        )

        novelty = 1.0 / (
            1.0 + visits
        )

        score = (
            0.20
            + curiosity * novelty * 0.35
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
            candidate.get("source")
            == "explicit_goal"
        ):
            score += 0.35

            reasons.append(
                "explicit_exploration_goal"
            )

        return {
            **deepcopy(candidate),
            "score": max(
                0.0,
                min(
                    1.0,
                    score
                )
            ),
            "reasons": reasons
        }

    @classmethod
    def _merge_candidates(
        cls,
        candidates
    ):
        merged = {}

        for candidate in candidates:
            key = (
                candidate["layer"],
                tuple(
                    sorted(
                        candidate[
                            "position"
                        ].items()
                    )
                )
            )

            if key not in merged:
                merged[key] = deepcopy(
                    candidate
                )

                continue

            existing = merged[key]

            existing["known_visits"] += int(
                candidate.get(
                    "known_visits",
                    0
                )
            )

            existing[
                "positive_memories"
            ] += int(
                candidate.get(
                    "positive_memories",
                    0
                )
            )

            existing[
                "negative_memories"
            ] += int(
                candidate.get(
                    "negative_memories",
                    0
                )
            )

            if (
                candidate.get("source")
                == "explicit_goal"
            ):
                existing["source"] = (
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