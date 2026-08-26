from copy import deepcopy

from cats.cat import Cat


class CatSocialSystem:
    """
    Natural cat-to-cat social interaction.

    A meeting is not automatically friendly.
    Both cats assess the encounter before
    deciding how much contact they tolerate.
    """

    def __init__(
        self,
        cats_layer=None
    ):
        self.cats_layer = cats_layer

    def meet(
        self,
        cat,
        other_cat
    ):
        self._require_cat(
            cat
        )

        self._require_cat(
            other_cat
        )

        if cat is other_cat:
            raise ValueError(
                "Cat cannot socially meet itself."
            )

        if (
            cat.current_layer
            != other_cat.current_layer
        ):
            return {
                "name": "cat_social_meeting_failed",
                "cat": cat.name,
                "other_cat": other_cat.name,
                "reason": "different_layers",
                "socialized": False
            }

        if not self._same_position(
            cat.position,
            other_cat.position
        ):
            return {
                "name": "cat_social_meeting_failed",
                "cat": cat.name,
                "other_cat": other_cat.name,
                "reason": "cats_not_near",
                "socialized": False
            }

        previous = self._last_meeting(
            cat
        )

        if (
            previous is not None
            and previous.get(
                "other_cat"
            ) == other_cat.name
            and cat.state
            == "near_target_cat"
        ):
            return {
                "name": "cat_social_meeting_skipped",
                "cat": cat.name,
                "other_cat": other_cat.name,
                "reason": (
                    "already_greeted_while_near"
                ),
                "socialized": False
            }

        cat_assessment = self.assess(
            cat,
            other_cat
        )

        other_assessment = self.assess(
            other_cat,
            cat
        )

        attitude = self._combined_attitude(
            cat_assessment,
            other_assessment
        )

        steps = []

        sniff_event = self.sniff(
            cat,
            other_cat
        )

        steps.append(
            sniff_event
        )

        if attitude == "friendly":
            outcome_steps = (
                self._friendly_greeting(
                    cat,
                    other_cat
                )
            )

        elif attitude == "hostile":
            outcome_steps = (
                self._hostile_greeting(
                    cat,
                    other_cat,
                    cat_assessment,
                    other_assessment
                )
            )

        else:
            outcome_steps = (
                self._uncertain_greeting(
                    cat,
                    other_cat
                )
            )

        steps.extend(
            outcome_steps
        )

        outcome = self._outcome_from_steps(
            attitude,
            outcome_steps
        )

        self._update_relationships(
            cat,
            other_cat,
            attitude=attitude,
            outcome=outcome
        )

        event = {
            "name": "cat_social_meeting",
            "cat": cat.name,
            "other_cat": other_cat.name,
            "attitude": attitude,
            "cat_assessment": deepcopy(
                cat_assessment
            ),
            "other_cat_assessment": deepcopy(
                other_assessment
            ),
            "steps": deepcopy(
                steps
            ),
            "outcome": outcome,
            "socialized": True
        }

        self._record_both(
            cat,
            other_cat,
            event
        )

        cat.state = (
            "near_target_cat"
        )

        return event

    def assess(
        self,
        cat,
        other_cat
    ):
        self._require_cat(
            cat
        )

        self._require_cat(
            other_cat
        )

        known_before = (
            other_cat.name
            in cat.relationships
        )

        relation = self._relation(
            cat,
            other_cat
        )

        familiarity = self._number(
            relation.get(
                "familiarity",
                0.0
            )
        )

        trust = self._number(
            relation.get(
                "trust",
                0.5
            )
        )

        affiliation = self._number(
            relation.get(
                "affiliation",
                0.0
            )
        )

        tension = self._number(
            relation.get(
                "tension",
                0.0
            )
        )

        traits = (
            cat.personality.get(
                "traits",
                {}
            )
            if isinstance(
                cat.personality,
                dict
            )
            else {}
        )

        empathy = self._trait(
            traits,
            "empathy",
            0.5
        )

        sociability = self._trait(
            traits,
            "sociability",
            0.5
        )

        courage = self._trait(
            traits,
            "courage",
            0.5
        )

        aggression = self._trait(
            traits,
            "aggression",
            0.0
        )

        friendly_score = (
            trust * 0.30
            + affiliation * 0.20
            + familiarity * 0.15
            + empathy * 0.15
            + sociability * 0.15
            + courage * 0.05
            - tension * 0.35
            - aggression * 0.15
        )

        if (
            tension >= 0.65
            or trust <= 0.20
            or (
                aggression >= 0.80
                and tension >= 0.30
            )
        ):
            attitude = "hostile"

        elif (
            known_before
            and friendly_score >= 0.48
            and trust >= 0.50
            and tension < 0.40
        ):
            attitude = "friendly"

        else:
            attitude = "uncertain"

        return {
            "cat": cat.name,
            "other_cat": other_cat.name,
            "known": known_before,
            "attitude": attitude,
            "friendly_score": round(
                friendly_score,
                4
            ),
            "familiarity": familiarity,
            "trust": trust,
            "affiliation": affiliation,
            "tension": tension,
            "empathy": empathy,
            "sociability": sociability,
            "courage": courage,
            "aggression": aggression
        }

    def sniff(
        self,
        cat,
        other_cat
    ):
        event = {
            "name": "cat_sniffed_cat",
            "cat": cat.name,
            "other_cat": other_cat.name,
            "contact": "scent_inspection"
        }

        self._record_both(
            cat,
            other_cat,
            event
        )

        return event

    def _friendly_greeting(
        self,
        cat,
        other_cat
    ):
        steps = []

        relation_a = self._relation(
            cat,
            other_cat
        )

        relation_b = self._relation(
            other_cat,
            cat
        )

        familiarity = (
            self._number(
                relation_a.get(
                    "familiarity",
                    0.0
                )
            )
            + self._number(
                relation_b.get(
                    "familiarity",
                    0.0
                )
            )
        ) / 2.0

        affiliation = (
            self._number(
                relation_a.get(
                    "affiliation",
                    0.0
                )
            )
            + self._number(
                relation_b.get(
                    "affiliation",
                    0.0
                )
            )
        ) / 2.0

        nose_touch = {
            "name": "cat_nose_touch",
            "cat": cat.name,
            "other_cat": other_cat.name,
            "contact": True
        }

        self._record_both(
            cat,
            other_cat,
            nose_touch
        )

        steps.append(
            nose_touch
        )

        slow_blink = {
            "name": "cat_slow_blink",
            "cat": cat.name,
            "other_cat": other_cat.name,
            "signal": "friendly"
        }

        self._record_both(
            cat,
            other_cat,
            slow_blink
        )

        steps.append(
            slow_blink
        )

        if (
            familiarity >= 0.40
            or affiliation >= 0.30
        ):
            head_bunt = {
                "name": "cat_head_bunt",
                "cat": cat.name,
                "other_cat": other_cat.name,
                "shared_scent": True
            }

            self._record_both(
                cat,
                other_cat,
                head_bunt
            )

            steps.append(
                head_bunt
            )

        if affiliation >= 0.70:
            body_rub = {
                "name": "cat_body_rub",
                "cat": cat.name,
                "other_cat": other_cat.name,
                "shared_scent": True
            }

            self._record_both(
                cat,
                other_cat,
                body_rub
            )

            steps.append(
                body_rub
            )

        return steps

    def _uncertain_greeting(
        self,
        cat,
        other_cat
    ):
        event = {
            "name": "cat_kept_social_distance",
            "cat": cat.name,
            "other_cat": other_cat.name,
            "signal": "uncertain",
            "escalated": False
        }

        self._record_both(
            cat,
            other_cat,
            event
        )

        return [
            event
        ]

    def _hostile_greeting(
        self,
        cat,
        other_cat,
        cat_assessment,
        other_assessment
    ):
        steps = []

        hiss = {
            "name": "cat_hissed_at_cat",
            "cat": cat.name,
            "other_cat": other_cat.name,
            "warning": True
        }

        self._record_both(
            cat,
            other_cat,
            hiss
        )

        steps.append(
            hiss
        )

        tension = max(
            self._number(
                cat_assessment.get(
                    "tension",
                    0.0
                )
            ),
            self._number(
                other_assessment.get(
                    "tension",
                    0.0
                )
            )
        )

        aggression = max(
            self._number(
                cat_assessment.get(
                    "aggression",
                    0.0
                )
            ),
            self._number(
                other_assessment.get(
                    "aggression",
                    0.0
                )
            )
        )

        if (
            tension >= 0.75
            or aggression >= 0.75
        ):
            swat = {
                "name": "cat_warning_swat",
                "cat": cat.name,
                "other_cat": other_cat.name,
                "warning": True,
                "injury": False
            }

            self._record_both(
                cat,
                other_cat,
                swat
            )

            steps.append(
                swat
            )

        if (
            tension >= 0.95
            and aggression >= 0.85
        ):
            fight = {
                "name": "cat_fight_started",
                "cat": cat.name,
                "other_cat": other_cat.name,
                "escalated": True
            }

            self._record_both(
                cat,
                other_cat,
                fight
            )

            steps.append(
                fight
            )

        return steps

    def _update_relationships(
        self,
        cat,
        other_cat,
        attitude,
        outcome
    ):
        relation_a = self._relation(
            cat,
            other_cat
        )

        relation_b = self._relation(
            other_cat,
            cat
        )

        for relation in (
            relation_a,
            relation_b
        ):
            relation[
                "meet_count"
            ] = int(
                relation.get(
                    "meet_count",
                    0
                )
            ) + 1

            relation[
                "familiarity"
            ] = self._clamp(
                self._number(
                    relation.get(
                        "familiarity",
                        0.0
                    )
                )
                + 0.10
            )

            if attitude == "friendly":
                relation[
                    "trust"
                ] = self._clamp(
                    self._number(
                        relation.get(
                            "trust",
                            0.5
                        )
                    )
                    + 0.08
                )

                relation[
                    "affiliation"
                ] = self._clamp(
                    self._number(
                        relation.get(
                            "affiliation",
                            0.0
                        )
                    )
                    + 0.10
                )

                relation[
                    "tension"
                ] = self._clamp(
                    self._number(
                        relation.get(
                            "tension",
                            0.0
                        )
                    )
                    - 0.10
                )

                if outcome in (
                    "head_bunt",
                    "body_rub"
                ):
                    relation[
                        "shared_scent"
                    ] = self._clamp(
                        self._number(
                            relation.get(
                                "shared_scent",
                                0.0
                            )
                        )
                        + (
                            0.20
                            if outcome
                            == "body_rub"
                            else 0.10
                        )
                    )

            elif attitude == "hostile":
                relation[
                    "trust"
                ] = self._clamp(
                    self._number(
                        relation.get(
                            "trust",
                            0.5
                        )
                    )
                    - 0.15
                )

                relation[
                    "affiliation"
                ] = self._clamp(
                    self._number(
                        relation.get(
                            "affiliation",
                            0.0
                        )
                    )
                    - 0.08
                )

                relation[
                    "tension"
                ] = self._clamp(
                    self._number(
                        relation.get(
                            "tension",
                            0.0
                        )
                    )
                    + 0.20
                )

            else:
                relation[
                    "trust"
                ] = self._clamp(
                    self._number(
                        relation.get(
                            "trust",
                            0.5
                        )
                    )
                    + 0.01
                )

            relation[
                "last_interaction"
            ] = outcome

    def _combined_attitude(
        self,
        assessment_a,
        assessment_b
    ):
        attitudes = {
            assessment_a[
                "attitude"
            ],
            assessment_b[
                "attitude"
            ]
        }

        if "hostile" in attitudes:
            return "hostile"

        if attitudes == {
            "friendly"
        }:
            return "friendly"

        return "uncertain"

    def _outcome_from_steps(
        self,
        attitude,
        steps
    ):
        names = [
            step.get(
                "name"
            )
            for step in steps
        ]

        if "cat_fight_started" in names:
            return "fight"

        if "cat_warning_swat" in names:
            return "warning_swat"

        if "cat_hissed_at_cat" in names:
            return "hiss"

        if "cat_body_rub" in names:
            return "body_rub"

        if "cat_head_bunt" in names:
            return "head_bunt"

        if "cat_nose_touch" in names:
            return "nose_touch"

        if attitude == "uncertain":
            return "kept_distance"

        return attitude

    def _relation(
        self,
        cat,
        other_cat
    ):
        relation = cat.relationships.setdefault(
            other_cat.name,
            {}
        )

        relation.setdefault(
            "familiarity",
            0.0
        )

        relation.setdefault(
            "trust",
            0.5
        )

        relation.setdefault(
            "affiliation",
            0.0
        )

        relation.setdefault(
            "tension",
            0.0
        )

        relation.setdefault(
            "shared_scent",
            0.0
        )

        relation.setdefault(
            "meet_count",
            0
        )

        relation.setdefault(
            "last_interaction",
            None
        )

        return relation

    def _record_both(
        self,
        cat,
        other_cat,
        event
    ):
        stored = deepcopy(
            event
        )

        cat.social_interactions.append(
            deepcopy(
                stored
            )
        )

        other_cat.social_interactions.append(
            deepcopy(
                stored
            )
        )

        emit_event = getattr(
            self.cats_layer,
            "emit_event",
            None
        )

        if callable(
            emit_event
        ):
            emit_event(
                deepcopy(
                    stored
                )
            )

    def _last_meeting(
        self,
        cat
    ):
        for event in reversed(
            cat.social_interactions
        ):
            if (
                event.get(
                    "name"
                )
                == "cat_social_meeting"
            ):
                return event

        return None

    def _same_position(
        self,
        first,
        second
    ):
        if (
            not isinstance(
                first,
                dict
            )
            or not isinstance(
                second,
                dict
            )
        ):
            return False

        return (
            self._number(
                first.get(
                    "x",
                    0.0
                )
            )
            == self._number(
                second.get(
                    "x",
                    0.0
                )
            )
            and self._number(
                first.get(
                    "y",
                    0.0
                )
            )
            == self._number(
                second.get(
                    "y",
                    0.0
                )
            )
            and self._number(
                first.get(
                    "z",
                    0.0
                )
            )
            == self._number(
                second.get(
                    "z",
                    0.0
                )
            )
        )

    def _trait(
        self,
        traits,
        name,
        default
    ):
        return self._clamp(
            self._number(
                traits.get(
                    name,
                    default
                )
            )
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
                "CatSocialSystem requires Cat."
            )
