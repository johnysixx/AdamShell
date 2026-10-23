from copy import deepcopy

from cats.cat import Cat
from cats.cat_cultural_adoption_result_state import (
    CatCulturalExposureDeniedResult,
    CatCulturalPreferenceAdoptedResult,
    CatCulturalPreferenceAdoptionDeniedResult,
    CatCulturalTraditionEvaluatedEvent,
    CatCulturalTraditionEvaluationResult,
)
from cats.cat_cultural_preference_state import (
    CatCulturalPreferenceState,
)
from cats.cat_cultural_tradition_evaluation_state import (
    CatCulturalTraditionEvaluationState,
)
from cats.cat_cultural_tradition_state import (
    CatCulturalTraditionState,
)


class CatCulturalAdoptionSystem:

    def __init__(
        self,
        group_system,
    ):
        self.group_system = group_system

    def evaluate_tradition(
        self,
        cat,
        group_id,
        tradition_name,
    ):
        self._require_cat(
            cat
        )

        group = self.group_system._group(
            group_id
        )

        tradition = (
            group.culture.traditions.record(
                tradition_name
            )
        )

        if tradition is None:
            return (
                CatCulturalTraditionEvaluationResult(
                    tradition=tradition_name,
                    known=False,
                )
            )

        if not isinstance(
            tradition,
            CatCulturalTraditionState,
        ):
            raise TypeError(
                "Cat cultural tradition record "
                "must be "
                "CatCulturalTraditionState."
            )

        traits = cat.personality.traits

        curiosity = self._number(
            traits.curiosity
        )

        sociability = self._number(
            traits.sociability
        )

        courage = self._number(
            traits.courage
        )

        category = tradition.category

        category_affinity = {
            "exploration":
                curiosity,
            "social":
                sociability,
            "defense":
                courage,
            "knowledge":
                self._number(
                    cat.intellect.normalized
                ),
            "navigation":
                curiosity,
            "ritual":
                sociability,
            "hunting":
                courage
                * 0.6
                + curiosity
                * 0.4,
        }.get(
            category,
            0.5,
        )

        strength = self._number(
            tradition.strength
        )

        score = (
            category_affinity
            * 0.55
            + strength
            * 0.35
            + 0.1
        )

        score = round(
            score,
            4,
        )

        return (
            CatCulturalTraditionEvaluationResult(
                tradition=tradition_name,
                known=True,
                category=category,
                score=score,
                adopt=(
                    score
                    >= 0.5
                ),
            )
        )

    def expose_to_tradition(
        self,
        cat,
        group_id,
        tradition_name,
    ):
        evaluation = (
            self.evaluate_tradition(
                cat,
                group_id,
                tradition_name,
            )
        )

        if not evaluation.known:
            return (
                CatCulturalExposureDeniedResult(
                    reason="unknown_tradition",
                )
            )

        self._require_evaluation_records(
            cat
        )

        record = (
            CatCulturalTraditionEvaluationState(
                tradition=tradition_name,
                group_id=group_id,
                score=evaluation.score,
                category=evaluation.category,
            )
        )

        cat.culture.exposures += 1

        if evaluation.adopt:
            cat.culture.adopted_traditions.store(
                record
            )

            cat.culture.rejected_traditions.release(
                tradition_name
            )

            outcome = "adopted"

        else:
            cat.culture.rejected_traditions.store(
                record
            )

            outcome = "rejected"

        event = (
            CatCulturalTraditionEvaluatedEvent(
                cat=cat.name,
                group_id=group_id,
                tradition=tradition_name,
                score=evaluation.score,
                outcome=outcome,
                adopted=(
                    outcome
                    == "adopted"
                ),
            )
        )

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
        preference_name,
    ):
        self._require_cat(
            cat
        )

        group = self.group_system._group(
            group_id
        )

        preference = (
            group.culture.preferences.record(
                preference_name
            )
        )

        if preference is None:
            return (
                CatCulturalPreferenceAdoptionDeniedResult(
                    reason="unknown_preference",
                )
            )

        if not isinstance(
            preference,
            CatCulturalPreferenceState,
        ):
            raise TypeError(
                "Cat cultural preference record "
                "must be "
                "CatCulturalPreferenceState."
            )

        adopted_preference = deepcopy(
            preference
        )

        adopted_preference.name = (
            preference_name
        )

        cat.culture.preferences.store(
            adopted_preference
        )

        return (
            CatCulturalPreferenceAdoptedResult(
                cat=cat.name,
                preference=
                    preference_name,
                value=deepcopy(
                    preference.value
                ),
            )
        )

    def _require_evaluation_records(
        self,
        cat,
    ):
        registries = (
            cat.culture.adopted_traditions,
            cat.culture.rejected_traditions,
        )

        for registry in registries:
            for record in registry.records():
                if not isinstance(
                    record,
                    CatCulturalTraditionEvaluationState,
                ):
                    raise TypeError(
                        "Cat cultural tradition "
                        "evaluation record must be "
                        "CatCulturalTraditionEvaluationState."
                    )

    def _require_cat(
        self,
        cat,
    ):
        if not isinstance(
            cat,
            Cat,
        ):
            raise TypeError(
                "CatCulturalAdoptionSystem "
                "requires Cat."
            )

    def _number(
        self,
        value,
    ):
        try:
            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0.0
