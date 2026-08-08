from cats.cat_intellect import CatIntellect
from copy import deepcopy


class CatMind:

    INTENTION_TYPES = (
        "visit_bar",
        "hunt_cronenberg",
        "explore_box",
        "create_exploration_pair",
        "approach_cat",
        "share_legend",
        "observe",
        "rest"
    )

    @classmethod
    def create_state(cls):
        return {
            "current_intention": None,
            "previous_intention": None,
            "candidates": [],
            "decision_count": 0,
            "history": []
        }

    @classmethod
    def ensure_state(
        cls,
        cat
    ):
        mind = cat.setdefault(
            "mind",
            cls.create_state()
        )

        mind.setdefault(
            "current_intention",
            None
        )

        mind.setdefault(
            "previous_intention",
            None
        )

        mind.setdefault(
            "candidates",
            []
        )

        mind.setdefault(
            "decision_count",
            0
        )

        mind.setdefault(
            "history",
            []
        )

        return mind

    @classmethod
    def consider(
        cls,
        cat,
        observations
    ):
        """
        Vytvoří možné úmysly.

        Nic nevykonává a nevybírá vítěze.
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

        aggression = float(
            traits.get(
                "aggression",
                0.5
            )
        )

        empathy = float(
            traits.get(
                "empathy",
                0.5
            )
        )

        patience = float(
            traits.get(
                "patience",
                0.5
            )
        )

        candidates = []

        if observations.get(
            "bar_known",
            False
        ):
            bar_score = 0.45

            if observations.get(
                "bar_visible",
                False
            ):
                bar_score += 0.10

            bar_score += (
                cls._bar_memory_score(
                    cat
                )
            )

            candidates.append(
                cls._candidate(
                    intention_type="visit_bar",
                    score=bar_score,
                    reasons=[
                        "bar_known",
                        *(
                            ["bar_visible"]
                            if observations.get(
                                "bar_visible",
                                False
                            )
                            else []
                        ),
                        *(
                            ["positive_bar_memory"]
                            if cls._bar_memory_score(
                                cat
                            ) > 0
                            else []
                        )
                    ]
                )
            )

        huntable = observations.get(
            "huntable_cronenbergs",
            []
        )

        if huntable:
            danger = float(
                observations.get(
                    "cronenberg_danger",
                    0.5
                )
            )

            hunt_score = (
                0.25
                + courage * 0.30
                + aggression * 0.25
                + curiosity * 0.10
                - danger * 0.20
            )

            candidates.append(
                cls._candidate(
                    intention_type=(
                        "hunt_cronenberg"
                    ),
                    score=hunt_score,
                    reasons=[
                        "huntable_cronenberg_visible",
                        "courage",
                        "aggression"
                    ],
                    target=(
                        huntable[0]
                    )
                )
            )

        boxes = observations.get(
            "unexplored_boxes",
            []
        )

        if boxes:
            explore_score = (
                0.25
                + curiosity * 0.55
                + courage * 0.10
            )

            candidates.append(
                cls._candidate(
                    intention_type="explore_box",
                    score=explore_score,
                    reasons=[
                        "unexplored_box_visible",
                        "curiosity"
                    ],
                    target=boxes[0]
                )
            )

        if (
            not boxes
            and observations.get(
                "can_create_exploration_pair",
                False
            )
        ):
            exploration_plan = (
                observations.get(
                    "exploration_plan",
                    {}
                )
            )

            exploration_reasons = set(
                exploration_plan.get(
                    "reasons",
                    []
                )
            )

            explicit_goal_bonus = (
                0.50
                if (
                    "explicit_exploration_goal"
                    in exploration_reasons
                )
                else 0.0
            )

            pair_score = (
                0.20
                + curiosity * 0.55
                + courage * 0.10
                + patience * 0.05
                + explicit_goal_bonus
            )

            reasons = [
                "no_usable_box_visible",
                "sufficient_energy",
                "curiosity",
                "quantum_pair_creation_possible"
            ]

            if explicit_goal_bonus > 0.0:
                reasons.append(
                    "explicit_exploration_goal"
                )

            candidates.append(
                cls._candidate(
                    intention_type=(
                        "create_exploration_pair"
                    ),
                    score=pair_score,
                    reasons=reasons,
                    target={
                        "layer": observations.get(
                            "exploration_destination_layer"
                        ),
                        "position": observations.get(
                            "exploration_destination_position"
                        ),
                        "energy_cost": observations.get(
                            "exploration_pair_energy_cost"
                        )
                    }
                )
            )

        nearby_cats = observations.get(
            "nearby_cats",
            []
        )

        if nearby_cats:
            legend_count = int(
                observations.get(
                    "shareable_legend_count",
                    0
                )
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
                            "shareable_knowledge_exists"
                        ],
                        target=nearby_cats[0]
                    )
                )

        if nearby_cats:
            social_score = (
                0.20
                + empathy * 0.50
                + curiosity * 0.10
            )

            candidates.append(
                cls._candidate(
                    intention_type="approach_cat",
                    score=social_score,
                    reasons=[
                        "nearby_cat",
                        "empathy"
                    ],
                    target=nearby_cats[0]
                )
            )

        if observations.get(
            "interesting_unknown",
            False
        ):
            candidates.append(
                cls._candidate(
                    intention_type="observe",
                    score=(
                        0.20
                        + curiosity * 0.40
                        + patience * 0.20
                    ),
                    reasons=[
                        "interesting_unknown",
                        "curiosity",
                        "patience"
                    ]
                )
            )

        # Odpočinek je vždy možný.
        candidates.append(
            cls._candidate(
                intention_type="rest",
                score=(
                    0.15
                    + patience * 0.25
                ),
                reasons=[
                    "rest_is_available"
                ]
            )
        )

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        mind = cls.ensure_state(
            cat
        )

        mind["candidates"] = deepcopy(
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
        top_count=None
    ):
        """
        Vybere vlastní úmysl kočky.

        Cat D20 zde neurčuje seznam možností.
        Pouze vybere mezi nejlepšími
        rozumnými kandidáty.
        """
        candidates = cls.consider(
            cat=cat,
            observations=observations
        )

        if not candidates:
            return {
                "name": (
                    "cat_intention_not_selected"
                ),
                "cat": cat.get("name"),
                "reason": "no_candidates",
                "selected": False
            }

        if top_count is None:
            top_count = (
                CatIntellect
                .decision_finalist_count(
                    cat=cat,
                    candidate_count=len(
                        candidates
                    )
                )
            )

        else:
            top_count = max(
                1,
                int(top_count)
            )

        finalists = candidates[
            :top_count
        ]

        if quantum_roll is None:
            winner_index = 0

        else:
            quantum_roll = int(
                quantum_roll
            )

            if not 1 <= quantum_roll <= 20:
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
                len(finalists) - 1
            )

        winner = deepcopy(
            finalists[winner_index]
        )

        mind = cls.ensure_state(
            cat
        )

        previous = mind.get(
            "current_intention"
        )

        mind["previous_intention"] = (
            deepcopy(previous)
        )

        mind["current_intention"] = (
            deepcopy(winner)
        )

        mind["decision_count"] += 1

        event = {
            "name": "cat_intention_selected",
            "cat": cat.get("name"),
            "intention": winner["type"],
            "target": winner.get(
                "target"
            ),
            "score": winner["score"],
            "reasons": list(
                winner["reasons"]
            ),
            "quantum_roll": quantum_roll,
            "intellect_score": (
                CatIntellect
                .ensure_state(
                    cat
                )[
                    "score"
                ]
            ),
            "intellect_category": (
                CatIntellect.category(
                    cat
                )
            ),
            "finalist_count": len(
                finalists
            ),
            "finalists": deepcopy(
                finalists
            ),
            "previous_intention": (
                deepcopy(previous)
            ),
            "selected": True
        }

        mind["history"].append(
            deepcopy(event)
        )

        return event

    @classmethod
    def clear_intention(
        cls,
        cat,
        reason
    ):
        mind = cls.ensure_state(
            cat
        )

        previous = mind.get(
            "current_intention"
        )

        mind["previous_intention"] = (
            deepcopy(previous)
        )

        mind["current_intention"] = None

        event = {
            "name": "cat_intention_cleared",
            "cat": cat.get("name"),
            "previous_intention": (
                deepcopy(previous)
            ),
            "reason": reason,
            "cleared": True
        }

        mind["history"].append(
            deepcopy(event)
        )

        return event

    @classmethod
    def _candidate(
        cls,
        intention_type,
        score,
        reasons,
        target=None
    ):
        if intention_type not in (
            cls.INTENTION_TYPES
        ):
            raise ValueError(
                "Unknown cat intention: "
                f"{intention_type}"
            )

        return {
            "type": intention_type,
            "target": target,
            "score": min(
                1.0,
                max(
                    0.0,
                    float(score)
                )
            ),
            "reasons": list(reasons)
        }

    @classmethod
    def _bar_memory_score(
        cls,
        cat
    ):
        memory = cat.get(
            "memory"
        )

        if memory is None:
            return 0.0

        events = getattr(
            memory,
            "events",
            []
        )

        positive_types = {
            "bar_entry",
            "cat_drank_milk_at_bar",
            "bouncer_petted_cat",
            "safe_at_bar"
        }

        positive_count = sum(
            1
            for event in events
            if event.get(
                "event_type"
            ) in positive_types
        )

        return min(
            0.30,
            positive_count * 0.06
        )