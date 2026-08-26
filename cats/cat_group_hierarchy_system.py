from copy import deepcopy

from cats.cat import Cat


class CatGroupHierarchySystem:
    """
    Situational influence inside a cat group.

    This is deliberately not an alpha/beta hierarchy.
    Influence can change with experience, relationships,
    defense and group participation.
    """

    def __init__(
        self,
        group_system
    ):
        self.group_system = group_system

    def rank(
        self,
        group_id,
        cats
    ):
        group = self.group_system._group(
            group_id
        )

        members = (
            self.group_system
            ._member_objects(
                group,
                cats
            )
        )

        ranking = []

        for cat in members:
            influence = self._influence(
                cat,
                members
            )

            cat.group[
                "influence"
            ] = influence

            ranking.append({
                "cat": cat.name,
                "influence": influence
            })

        ranking.sort(
            key=lambda item: (
                item["influence"],
                item["cat"]
            ),
            reverse=True
        )

        event = {
            "name": "cat_group_influence_ranked",
            "group_id": group_id,
            "ranking": deepcopy(
                ranking
            )
        }

        group[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        return ranking

    def most_influential(
        self,
        group_id,
        cats
    ):
        ranking = self.rank(
            group_id,
            cats
        )

        if not ranking:
            return None

        return ranking[0]

    def _influence(
        self,
        cat,
        members
    ):
        traits = cat.personality.get(
            "traits",
            {}
        )

        courage = self._number(
            traits.get(
                "courage",
                0.5
            )
        )

        intellect = self._number(
            cat.intellect.get(
                "normalized",
                0.5
            )
        )

        relationship_scores = []

        for other in members:
            if other is cat:
                continue

            relation = other.relationships.get(
                cat.name,
                {}
            )

            relationship_scores.append(
                self._number(
                    relation.get(
                        "trust",
                        0.5
                    )
                ) * 0.55
                + self._number(
                    relation.get(
                        "affiliation",
                        0.0
                    )
                ) * 0.30
                + self._number(
                    relation.get(
                        "familiarity",
                        0.0
                    )
                ) * 0.15
            )

        social_support = (
            sum(
                relationship_scores
            )
            / len(
                relationship_scores
            )
            if relationship_scores
            else 0.5
        )

        defense = min(
            1.0,
            int(
                cat.group.get(
                    "defense_events",
                    0
                )
            ) / 5.0
        )

        participation = min(
            1.0,
            int(
                cat.group.get(
                    "group_events",
                    0
                )
            ) / 20.0
        )

        influence = (
            social_support * 0.35
            + courage * 0.20
            + intellect * 0.15
            + defense * 0.15
            + participation * 0.15
        )

        return round(
            self._clamp(
                influence
            ),
            4
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
