from copy import deepcopy

from cats.cat import Cat


class CatCulturalAdoptionSystem:

    def __init__(
        self,
        group_system
    ):
        self.group_system = group_system

    def evaluate_tradition(
        self,
        cat,
        group_id,
        tradition_name
    ):
        self._require_cat(
            cat
        )

        group = self.group_system._group(
            group_id
        )

        tradition = group[
            "culture"
        ][
            "traditions"
        ].get(
            tradition_name
        )

        if tradition is None:
            return {
                "tradition": tradition_name,
                "known": False,
                "adopt": False
            }

        traits = cat.personality.get(
            "traits",
            {}
        )

        curiosity = self._number(
            traits.get(
                "curiosity",
                0.5
            )
        )

        sociability = self._number(
            traits.get(
                "sociability",
                traits.get(
                    "social",
                    0.5
                )
            )
        )

        courage = self._number(
            traits.get(
                "courage",
                0.5
            )
        )

        category = tradition.get(
            "category"
        )

        category_affinity = {
            "exploration": curiosity,
            "social": sociability,
            "defense": courage,
            "knowledge": (
                self._number(
                    cat.intellect.get(
                        "normalized",
                        0.5
                    )
                )
            ),
            "navigation": curiosity,
            "ritual": sociability,
            "hunting": (
                courage * 0.6
                + curiosity * 0.4
            )
        }.get(
            category,
            0.5
        )

        strength = self._number(
            tradition.get(
                "strength",
                0.0
            )
        )

        score = (
            category_affinity * 0.55
            + strength * 0.35
            + 0.10
        )

        return {
            "tradition": tradition_name,
            "known": True,
            "category": category,
            "score": round(
                score,
                4
            ),
            "adopt": (
                score >= 0.50
            )
        }

    def expose_to_tradition(
        self,
        cat,
        group_id,
        tradition_name
    ):
        evaluation = self.evaluate_tradition(
            cat,
            group_id,
            tradition_name
        )

        if not evaluation[
            "known"
        ]:
            return {
                "name": (
                    "cat_cultural_exposure_denied"
                ),
                "reason": "unknown_tradition",
                "adopted": False
            }

        cat.culture[
            "exposures"
        ] += 1

        if evaluation[
            "adopt"
        ]:
            cat.culture[
                "adopted_traditions"
            ][
                tradition_name
            ] = {
                "group_id": group_id,
                "score": evaluation[
                    "score"
                ],
                "category": evaluation[
                    "category"
                ]
            }

            cat.culture[
                "rejected_traditions"
            ].pop(
                tradition_name,
                None
            )

            outcome = "adopted"

        else:
            cat.culture[
                "rejected_traditions"
            ][
                tradition_name
            ] = {
                "group_id": group_id,
                "score": evaluation[
                    "score"
                ],
                "category": evaluation[
                    "category"
                ]
            }

            outcome = "rejected"

        event = {
            "name": "cat_cultural_tradition_evaluated",
            "cat": cat.name,
            "group_id": group_id,
            "tradition": tradition_name,
            "score": evaluation[
                "score"
            ],
            "outcome": outcome,
            "adopted": (
                outcome == "adopted"
            )
        }

        cat.social_interactions.append(
            deepcopy(
                event
            )
        )

        return event

    def adopt_preference(
        self,
        cat,
        group_id,
        preference_name
    ):
        self._require_cat(
            cat
        )

        group = self.group_system._group(
            group_id
        )

        preference = group[
            "culture"
        ][
            "preferences"
        ].get(
            preference_name
        )

        if preference is None:
            return {
                "name": (
                    "cat_cultural_preference_denied"
                ),
                "reason": "unknown_preference",
                "adopted": False
            }

        cat.culture[
            "preferences"
        ][
            preference_name
        ] = deepcopy(
            preference
        )

        return {
            "name": (
                "cat_cultural_preference_adopted"
            ),
            "cat": cat.name,
            "preference": preference_name,
            "value": preference.get(
                "value"
            ),
            "adopted": True
        }

    def _require_cat(
        self,
        cat
    ):
        if not isinstance(
            cat,
            Cat
        ):
            raise TypeError(
                "CatCulturalAdoptionSystem "
                "requires Cat."
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
