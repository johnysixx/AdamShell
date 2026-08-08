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
            {
                "action": "continue_exploration",
                "score": min(
                    1.0,
                    continue_score
                ),
                "reasons": [
                    "curiosity",
                    "courage",
                    "intellect"
                ]
            },
            {
                "action": "rest_at_destination",
                "score": min(
                    1.0,
                    rest_score
                ),
                "reasons": [
                    "patience",
                    "destination_reached"
                ]
            },
            {
                "action": (
                    "return_via_exploration_pair"
                ),
                "score": min(
                    1.0,
                    return_score
                ),
                "reasons": [
                    "known_return_path",
                    "patience",
                    "risk_evaluation"
                ]
            }
        ]

        candidates.sort(
            key=lambda item: item["score"],
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

        return {
            "selected": True,
            "action": selected[
                "action"
            ],
            "score": selected[
                "score"
            ],
            "reasons": list(
                selected["reasons"]
            ),
            "finalists": deepcopy(
                finalists
            ),
            "quantum_roll": quantum_roll
        }

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
            cat.get(
                "position",
                {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            )
        )

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

        intellect = float(
            cat.get(
                "intellect",
                {}
            ).get(
                "normalized",
                0.5
            )
        )

        memory = cat.get(
            "memory"
        )

        visited_positions = []

        for event in getattr(
            memory,
            "events",
            []
        ):
            if event.get(
                "event_type"
            ) != "successful_exploration":
                continue

            details = event.get(
                "details",
                {}
            )

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

            candidates.append({
                "layer": "quantum_layer",
                "position": position,
                "score": max(
                    0.0,
                    min(
                        1.0,
                        score
                    )
                ),
                "direction_index": index,
                "revisit_penalty": (
                    revisit_penalty
                )
            })

        candidates.sort(
            key=lambda item: (
                item["score"],
                -item["direction_index"]
            ),
            reverse=True
        )

        winner = candidates[0]

        return {
            "selected": True,
            "layer": "quantum_layer",
            "position": deepcopy(
                winner["position"]
            ),
            "score": winner["score"],
            "reason": (
                "continue_quantum_exploration"
            ),
            "candidates": deepcopy(
                candidates
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

        knowledge = cat.get(
            "knowledge",
            {}
        )

        for heard in knowledge.get(
            "heard_legends",
            []
        ):
            if heard.get(
                "verified",
                False
            ):
                continue

            if heard.get(
                "contradicted",
                False
            ):
                continue

            credibility = float(
                heard.get(
                    "credibility",
                    0.0
                )
            )

            if credibility < 0.35:
                continue

            layer = heard.get(
                "layer"
            )

            position = heard.get(
                "position"
            )

            if (
                layer is None
                or not isinstance(
                    position,
                    dict
                )
            ):
                continue

            candidates.append({
                "layer": str(layer),
                "position": cls._position(
                    position
                ),
                "source": "heard_legend",
                "legend_id": heard.get(
                    "legend_id"
                ),
                "storyteller": heard.get(
                    "storyteller"
                ),
                "legend_credibility": (
                    credibility
                ),
                "known_visits": 0,
                "positive_memories": 0,
                "negative_memories": 0
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
            == "heard_legend"
        ):
            credibility = float(
                candidate.get(
                    "legend_credibility",
                    0.0
                )
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