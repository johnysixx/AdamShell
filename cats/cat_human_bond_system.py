from copy import deepcopy

from cats.cat import Cat


class CatHumanBondSystem:

    RIGHT_HUMAN_THRESHOLD = 0.72

    def __init__(
        self,
        cats_layer=None
    ):
        self.cats_layer = cats_layer

    def remember_interaction(
        self,
        cat,
        human,
        positive=True,
        significance=0.10
    ):
        self._require_cat(
            cat
        )

        human_name = self._name(
            human
        )

        if human_name is None:
            raise ValueError(
                "Human must have a name."
            )

        bond = cat.human_bonds.setdefault(
            human_name,
            self._new_bond(
                human_name
            )
        )

        significance = self._clamp(
            significance
        )

        bond[
            "encounters"
        ] += 1

        bond[
            "familiarity"
        ] = self._clamp(
            bond[
                "familiarity"
            ]
            + significance * 0.70
        )

        if positive:
            bond[
                "positive_interactions"
            ] += 1

            bond[
                "trust"
            ] = self._clamp(
                bond[
                    "trust"
                ]
                + significance
            )

            bond[
                "affection"
            ] = self._clamp(
                bond[
                    "affection"
                ]
                + significance * 0.80
            )

        else:
            bond[
                "negative_interactions"
            ] += 1

            bond[
                "trust"
            ] = self._clamp(
                bond[
                    "trust"
                ]
                - significance * 1.30
            )

            bond[
                "affection"
            ] = self._clamp(
                bond[
                    "affection"
                ]
                - significance
            )

        bond[
            "right_human_score"
        ] = self._score(
            cat,
            bond
        )

        event = {
            "name": "cat_human_interaction_remembered",
            "cat": cat.name,
            "human": human_name,
            "positive": bool(
                positive
            ),
            "right_human_score": bond[
                "right_human_score"
            ]
        }

        cat.social_interactions.append(
            deepcopy(
                event
            )
        )

        return event

    def evaluate(
        self,
        cat,
        human
    ):
        self._require_cat(
            cat
        )

        human_name = self._name(
            human
        )

        bond = cat.human_bonds.get(
            human_name
        )

        if bond is None:
            return {
                "cat": cat.name,
                "human": human_name,
                "score": 0.0,
                "right_human": False,
                "reason": "human_not_known"
            }

        score = self._score(
            cat,
            bond
        )

        bond[
            "right_human_score"
        ] = score

        right_human = bool(
            score
            >= self.RIGHT_HUMAN_THRESHOLD
            and bond[
                "negative_interactions"
            ] <= bond[
                "positive_interactions"
            ]
        )

        bond[
            "recognized_as_right_human"
        ] = right_human

        return {
            "cat": cat.name,
            "human": human_name,
            "score": score,
            "right_human": right_human,
            "trust": bond[
                "trust"
            ],
            "affection": bond[
                "affection"
            ],
            "familiarity": bond[
                "familiarity"
            ]
        }

    def _score(
        self,
        cat,
        bond
    ):
        personality = cat.personality.get(
            "traits",
            {}
        )

        sociability = self._number(
            personality.get(
                "sociability",
                personality.get(
                    "social",
                    0.5
                )
            )
        )

        score = (
            bond[
                "trust"
            ] * 0.40
            + bond[
                "affection"
            ] * 0.35
            + bond[
                "familiarity"
            ] * 0.20
            + sociability * 0.05
        )

        return round(
            self._clamp(
                score
            ),
            4
        )

    def _new_bond(
        self,
        human_name
    ):
        return {
            "human": human_name,
            "encounters": 0,
            "positive_interactions": 0,
            "negative_interactions": 0,
            "trust": 0.50,
            "affection": 0.0,
            "familiarity": 0.0,
            "right_human_score": 0.0,
            "recognized_as_right_human": False
        }

    def _name(
        self,
        entity
    ):
        if isinstance(
            entity,
            dict
        ):
            return entity.get(
                "name"
            )

        return getattr(
            entity,
            "name",
            None
        )

    def _number(
        self,
        value
    ):
        try:
            return float(
                value
            )
        except (
            TypeError,
            ValueError
        ):
            return 0.0

    def _clamp(
        self,
        value
    ):
        return max(
            0.0,
            min(
                1.0,
                float(
                    value
                )
            )
        )

    def _require_cat(
        self,
        cat
    ):
        if not isinstance(
            cat,
            Cat
        ):
            raise TypeError(
                "CatHumanBondSystem requires Cat."
            )
