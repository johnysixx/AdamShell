from copy import deepcopy

from cats.cat import Cat
from cats.cat_social_objects import (
    CatLegend,
    CatRelationship,
    CatRelationshipTrustEvent,
)
from cats.cat_knowledge_objects import (
    CatHeardLegend,
    CatKnowledgeState,
    CatVerifiedLegendRecord,
)
from cats.cat_legend_result_state import (
    CatLegendContradictionResult,
    CatLegendNotSharedResult,
    CatLegendSelectionResult,
    CatLegendSharedEvent,
    CatLegendSharingEvaluationResult,
)


class CatLegendKnowledgeSystem:

    @classmethod
    def ensure_cat_knowledge(
        cls,
        cat,
    ):
        if not isinstance(
            cat,
            Cat,
        ):
            raise TypeError(
                "Cat legend knowledge requires Cat."
            )

        if not isinstance(
            cat.knowledge,
            CatKnowledgeState,
        ):
            raise TypeError(
                "Cat knowledge must be "
                "CatKnowledgeState."
            )

        return cat.knowledge

    @classmethod
    def ensure_universe_legends(cls, universe):
        if not hasattr(universe, 'cat_legends'):
            universe.cat_legends = []
        return universe.cat_legends

    @classmethod
    def publish_legend(
        cls,
        universe,
        cat,
        place,
        claim_type='place_discovered',
    ):
        legends = cls.ensure_universe_legends(
            universe
        )

        place_id = place.place_id

        legend = next(
            (
                item
                for item in legends
                if getattr(
                    item,
                    'place_id',
                    None,
                ) == place_id
                and getattr(
                    item,
                    'claim_type',
                    None,
                ) == claim_type
            ),
            None,
        )

        cat_name = cat.name

        if legend is None:
            legend = CatLegend(
                legend_id=(
                    f'cat_legend_'
                    f'{len(legends) + 1:04d}'
                ),
                claim_type=claim_type,
                place_id=place_id,
                layer=place.layer,
                position=deepcopy(
                    place.position
                ),
                discoverer=cat_name,
                reported_by=[
                    cat_name
                ],
                verification_count=1,
                confidence=min(
                    1.0,
                    float(
                        place.confidence
                    ),
                ),
                safety=place.safety,
                active=True,
            )

            legends.append(
                legend
            )

        else:
            if not hasattr(
                legend,
                'reported_by',
            ):
                legend.reported_by = []

            reporters = legend.reported_by

            if cat_name not in reporters:
                reporters.append(
                    cat_name
                )

            legend.verification_count += 1

            legend.confidence = min(
                1.0,
                float(
                    getattr(
                        legend,
                        'confidence',
                        0.5,
                    )
                )
                + 0.08,
            )

            if place.safety is not None:
                previous_safety = getattr(
                    legend,
                    'safety',
                    None,
                )

                if previous_safety is None:
                    legend.safety = (
                        place.safety
                    )
                else:
                    legend.safety = (
                        previous_safety
                        + place.safety
                    ) / 2.0

        return deepcopy(legend)

    @classmethod
    def hear_legend(
        cls,
        listener,
        storyteller,
        legend,
    ):
        knowledge = (
            cls.ensure_cat_knowledge(
                listener
            )
        )

        if not isinstance(
            storyteller,
            Cat,
        ):
            raise TypeError(
                'Legend storyteller must be Cat.'
            )

        if not isinstance(
            listener,
            Cat,
        ):
            raise TypeError(
                'Legend listener must be Cat.'
            )

        storyteller_name = (
            storyteller.name
        )

        trust = cls._trust_in_cat(
            listener,
            storyteller_name,
        )

        intellect = float(
            listener.intellect.normalized
        )

        source_confidence = float(
            getattr(
                legend,
                'confidence',
                0.5,
            )
        )

        credibility = (
            source_confidence
            * 0.45
            + trust
            * 0.4
            + intellect
            * 0.15
        )

        legend_id = getattr(
            legend,
            'legend_id',
            None,
        )

        heard = next(
            (
                item
                for item
                in knowledge.heard_legends
                if item.legend_id
                == legend_id
                and item.storyteller
                == storyteller_name
            ),
            None,
        )

        if heard is None:
            heard = CatHeardLegend(
                legend_id=legend_id,
                claim_type=getattr(
                    legend,
                    'claim_type',
                    None,
                ),
                place_id=getattr(
                    legend,
                    'place_id',
                    None,
                ),
                layer=getattr(
                    legend,
                    'layer',
                    None,
                ),
                position=deepcopy(
                    getattr(
                        legend,
                        'position',
                        None,
                    )
                ),
                storyteller=(
                    storyteller_name
                ),
                trust_in_storyteller=(
                    trust
                ),
                source_confidence=(
                    source_confidence
                ),
                credibility=credibility,
            )

            knowledge.heard_legends.append(
                heard
            )

        else:
            heard.record_hearing(
                trust_in_storyteller=(
                    trust
                ),
                source_confidence=(
                    source_confidence
                ),
                credibility=credibility,
            )

        return deepcopy(
            heard
        )

    @classmethod
    def verify_heard_legend(
        cls,
        cat,
        place,
    ):
        knowledge = (
            cls.ensure_cat_knowledge(
                cat
            )
        )

        verified = []

        for heard in knowledge.heard_legends:
            if (
                heard.place_id
                != place.place_id
            ):
                continue

            if heard.verified:
                continue

            credibility_before = (
                heard.credibility
            )

            trust_change = (
                cls.adjust_storyteller_trust(
                    listener=cat,
                    storyteller_name=(
                        heard.storyteller
                    ),
                    delta=0.1,
                    reason=(
                        'legend_confirmed_by_'
                        'personal_observation'
                    ),
                    legend_id=(
                        heard.legend_id
                    ),
                )
            )

            heard.verify(
                trust_after=(
                    trust_change.current
                )
            )

            record = (
                CatVerifiedLegendRecord(
                    legend_id=(
                        heard.legend_id
                    ),
                    place_id=(
                        heard.place_id
                    ),
                    storyteller=(
                        heard.storyteller
                    ),
                    verified_by=cat.name,
                    credibility_before=(
                        credibility_before
                    ),
                    trust_change=deepcopy(
                        trust_change
                    ),
                )
            )

            knowledge.verified_legends.append(
                record
            )

            verified.append(
                deepcopy(
                    record
                )
            )

        return verified

    @classmethod
    def choose_legend_to_share(
        cls,
        storyteller,
        listener,
        universe,
    ):
        legends = (
            cls.ensure_universe_legends(
                universe
            )
        )

        storyteller_name = (
            storyteller.name
        )

        listener_name = (
            listener.name
        )

        knowledge = (
            cls.ensure_cat_knowledge(
                listener
            )
        )

        already_heard = {
            (
                item.legend_id,
                item.storyteller,
            )
            for item
            in knowledge.heard_legends
        }

        candidates = []

        for legend in legends:
            if not getattr(
                legend,
                "active",
                True,
            ):
                continue

            if (
                storyteller_name
                not in getattr(
                    legend,
                    "reported_by",
                    [],
                )
            ):
                continue

            if (
                getattr(
                    legend,
                    "legend_id",
                    None,
                ),
                storyteller_name,
            ) in already_heard:
                continue

            candidates.append(
                deepcopy(
                    legend
                )
            )

        if not candidates:
            return (
                CatLegendSelectionResult(
                    selected=False,
                    storyteller=
                        storyteller_name,
                    listener=
                        listener_name,
                    reason=(
                        "no_shareable_legend"
                    ),
                )
            )

        candidates.sort(
            key=lambda item: (
                float(
                    getattr(
                        item,
                        "confidence",
                        0.0,
                    )
                ),
                int(
                    getattr(
                        item,
                        "verification_count",
                        0,
                    )
                ),
            ),
            reverse=True,
        )

        return (
            CatLegendSelectionResult(
                selected=True,
                legend=
                    candidates[0],
                candidate_count=
                    len(candidates),
                storyteller=
                    storyteller_name,
                listener=
                    listener_name,
            )
        )


    @classmethod
    def evaluate_legend_sharing(
        cls,
        storyteller,
        listener,
        legend,
    ):
        listener_name = (
            listener.name
        )

        traits = (
            storyteller
            .personality
            .traits
        )

        curiosity = float(
            traits.curiosity
        )

        patience = float(
            traits.patience
        )

        intellect = float(
            storyteller
            .intellect
            .normalized
        )

        trust = (
            cls._trust_in_cat(
                storyteller,
                listener_name,
            )
        )

        confidence = float(
            getattr(
                legend,
                "confidence",
                0.5,
            )
        )

        verification_count = int(
            getattr(
                legend,
                "verification_count",
                1,
            )
        )

        information_value = min(
            1.0,
            confidence * 0.7
            + min(
                verification_count,
                5,
            ) * 0.06,
        )

        share_score = (
            0.1
            + trust * 0.3
            + curiosity * 0.2
            + patience * 0.1
            + intellect * 0.1
            + information_value
            * 0.2
        )

        share_score = max(
            0.0,
            min(
                1.0,
                share_score,
            ),
        )

        return (
            CatLegendSharingEvaluationResult(
                share=(
                    share_score
                    >= 0.55
                ),
                score=
                    share_score,
                trust_in_listener=
                    trust,
                information_value=
                    information_value,
                reasons=(
                    "relationship_to_listener",
                    "information_value",
                    "curiosity",
                    "patience",
                    "intellect",
                ),
            )
        )


    @classmethod
    def share_legend(
        cls,
        storyteller,
        listener,
        universe,
    ):
        selection = (
            cls.choose_legend_to_share(
                storyteller=
                    storyteller,
                listener=
                    listener,
                universe=
                    universe,
            )
        )

        if not isinstance(
            selection,
            CatLegendSelectionResult,
        ):
            raise TypeError(
                "Legend selection must return "
                "CatLegendSelectionResult."
            )

        if not selection.selected:
            return (
                CatLegendNotSharedResult(
                    storyteller=
                        storyteller.name,
                    listener=
                        listener.name,
                    reason=(
                        selection.reason
                        or
                        "no_shareable_legend"
                    ),
                )
            )

        legend = (
            selection.legend
        )

        evaluation = (
            cls.evaluate_legend_sharing(
                storyteller=
                    storyteller,
                listener=
                    listener,
                legend=
                    legend,
            )
        )

        if not isinstance(
            evaluation,
            CatLegendSharingEvaluationResult,
        ):
            raise TypeError(
                "Legend sharing evaluation must "
                "return "
                "CatLegendSharingEvaluationResult."
            )

        if not evaluation.share:
            return (
                CatLegendNotSharedResult(
                    storyteller=
                        storyteller.name,
                    listener=
                        listener.name,
                    legend_id=getattr(
                        legend,
                        "legend_id",
                        None,
                    ),
                    evaluation=
                        evaluation,
                    reason=(
                        "sharing_not_worthwhile"
                    ),
                )
            )

        heard = (
            cls.hear_legend(
                listener=
                    listener,
                storyteller=
                    storyteller,
                legend=
                    legend,
            )
        )

        return (
            CatLegendSharedEvent(
                storyteller=
                    storyteller.name,
                listener=
                    listener.name,
                legend_id=getattr(
                    legend,
                    "legend_id",
                    None,
                ),
                layer=getattr(
                    legend,
                    "layer",
                    None,
                ),
                position=deepcopy(
                    getattr(
                        legend,
                        "position",
                        None,
                    )
                ),
                evaluation=
                    evaluation,
                heard_legend=
                    heard,
            )
        )


    @classmethod
    def adjust_storyteller_trust(
        cls,
        listener,
        storyteller_name,
        delta,
        reason,
        legend_id=None,
    ):
        if not isinstance(
            listener,
            Cat,
        ):
            raise TypeError(
                'Trust listener must be Cat.'
            )

        relation = (
            listener
            .relationships
            .setdefault(
                storyteller_name,
                CatRelationship.create(),
            )
        )

        if not isinstance(
            relation,
            CatRelationship,
        ):
            raise TypeError(
                'Cat relationships must contain '
                'CatRelationship objects.'
            )

        previous = float(
            relation.trust
        )

        current = max(
            0.0,
            min(
                1.0,
                previous
                + float(delta),
            ),
        )

        relation.trust = current

        event = CatRelationshipTrustEvent(
            previous=previous,
            current=current,
            delta=current - previous,
            reason=reason,
            legend_id=legend_id,
        )

        relation.trust_history.append(
            event
        )

        return event

    @classmethod
    def contradict_heard_legend(
        cls,
        cat,
        legend_id,
        reason=(
            "personal_observation_"
            "contradicted"
        ),
    ):
        knowledge = (
            cls.ensure_cat_knowledge(
                cat
            )
        )

        heard = next(
            (
                item
                for item
                in knowledge.heard_legends
                if (
                    item.legend_id
                    == legend_id
                )
            ),
            None,
        )

        if heard is None:
            return (
                CatLegendContradictionResult(
                    contradicted=False,
                    reason=(
                        "legend_not_heard"
                    ),
                    legend_id=
                        legend_id,
                )
            )

        if heard.verified:
            return (
                CatLegendContradictionResult(
                    contradicted=False,
                    reason=(
                        "legend_already_verified"
                    ),
                    legend_id=
                        legend_id,
                    storyteller=
                        heard.storyteller,
                )
            )

        storyteller = (
            heard.storyteller
        )

        trust_change = (
            cls.adjust_storyteller_trust(
                listener=cat,
                storyteller_name=
                    storyteller,
                delta=-0.15,
                reason=reason,
                legend_id=
                    legend_id,
            )
        )

        heard.contradict(
            trust_after=(
                trust_change.current
            )
        )

        return (
            CatLegendContradictionResult(
                contradicted=True,
                legend_id=
                    legend_id,
                storyteller=
                    storyteller,
                trust_change=
                    trust_change,
            )
        )


    @staticmethod
    def _trust_in_cat(
        listener,
        storyteller_name,
    ):
        if not isinstance(
            listener,
            Cat,
        ):
            raise TypeError(
                'Trust listener must be Cat.'
            )

        relation = (
            listener
            .relationships
            .get(
                storyteller_name
            )
        )

        if relation is None:
            return 0.5

        if not isinstance(
            relation,
            CatRelationship,
        ):
            raise TypeError(
                'Cat relationships must contain '
                'CatRelationship objects.'
            )

        return max(
            0.0,
            min(
                1.0,
                float(
                    relation.trust
                ),
            ),
        )
