from copy import deepcopy

from cats.cat_group_bonding_system import (
    CatGroupBondingSystem
)
from cats.cat_group_hierarchy_system import (
    CatGroupHierarchySystem
)
from cats.cat_group_memory_system import (
    CatGroupMemorySystem
)


class CatGroupConflictSystem:

    def __init__(
        self,
        group_system
    ):
        self.group_system = group_system

        self.bonding = (
            CatGroupBondingSystem(
                group_system
            )
        )

        self.hierarchy = (
            CatGroupHierarchySystem(
                group_system
            )
        )

        self.memory = (
            CatGroupMemorySystem(
                group_system
            )
        )

    def encounter(
        self,
        first_group_id,
        second_group_id,
        cats,
        resource=None
    ):
        first = self.group_system._group(
            first_group_id
        )

        second = self.group_system._group(
            second_group_id
        )

        if first_group_id == second_group_id:
            raise ValueError(
                "Group cannot conflict with itself."
            )

        shared_territories = set(
            first.get(
                "territories",
                {}
            )
        ).intersection(
            second.get(
                "territories",
                {}
            )
        )

        same_place = bool(
            first.get(
                "current_layer"
            )
            == second.get(
                "current_layer"
            )
            and first.get(
                "current_location"
            )
            == second.get(
                "current_location"
            )
        )

        conflict_possible = bool(
            shared_territories
            or same_place
            or resource is not None
        )

        if not conflict_possible:
            return {
                "name": "cat_group_encounter_peaceful",
                "first_group": first_group_id,
                "second_group": second_group_id,
                "conflict": False
            }

        return self.resolve(
            first_group_id,
            second_group_id,
            cats,
            resource=resource,
            shared_territories=list(
                shared_territories
            )
        )

    def resolve(
        self,
        first_group_id,
        second_group_id,
        cats,
        resource=None,
        shared_territories=None
    ):
        first = self.group_system._group(
            first_group_id
        )

        second = self.group_system._group(
            second_group_id
        )

        first_strength = self._strength(
            first_group_id,
            cats
        )

        second_strength = self._strength(
            second_group_id,
            cats
        )

        difference = abs(
            first_strength
            - second_strength
        )

        if difference < 0.10:
            winner = None
            loser = None
            outcome = "standoff"

        elif first_strength > second_strength:
            winner = first_group_id
            loser = second_group_id
            outcome = "first_group_prevailed"

        else:
            winner = second_group_id
            loser = first_group_id
            outcome = "second_group_prevailed"

        first[
            "conflict_count"
        ] += 1

        second[
            "conflict_count"
        ] += 1

        first_members = (
            self.group_system
            ._member_objects(
                first,
                cats
            )
        )

        second_members = (
            self.group_system
            ._member_objects(
                second,
                cats
            )
        )

        self._apply_group_tension(
            first_members,
            0.08
        )

        self._apply_group_tension(
            second_members,
            0.08
        )

        if loser is not None:
            loser_group = (
                first
                if loser == first_group_id
                else second
            )

            loser_group[
                "state"
            ] = "strained"

        event = {
            "name": "cat_inter_group_conflict",
            "first_group": first_group_id,
            "second_group": second_group_id,
            "resource": resource,
            "shared_territories": (
                shared_territories or []
            ),
            "first_strength": first_strength,
            "second_strength": second_strength,
            "winner": winner,
            "loser": loser,
            "outcome": outcome,
            "conflict": True
        }

        first[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        second[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        for cat in (
            first_members
            + second_members
        ):
            cat.social_interactions.append(
                deepcopy(
                    event
                )
            )

        self.memory.remember_encounter(
            first_group_id,
            second_group_id,
            event
        )

        return event

    def _strength(
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

        if not members:
            return 0.0

        cohesion = (
            self.bonding.evaluate(
                group_id,
                cats
            )[
                "cohesion"
            ]
        )

        ranking = self.hierarchy.rank(
            group_id,
            cats
        )

        influence = (
            sum(
                item[
                    "influence"
                ]
                for item in ranking
            )
            / len(
                ranking
            )
            if ranking
            else 0.0
        )

        physical = (
            sum(
                float(
                    member.strength
                )
                for member in members
            )
            / len(
                members
            )
        )

        number_bonus = min(
            0.30,
            len(
                members
            ) * 0.05
        )

        score = (
            cohesion * 0.30
            + influence * 0.25
            + min(
                1.0,
                physical / 3.0
            ) * 0.30
            + number_bonus
        )

        return round(
            min(
                1.0,
                score
            ),
            4
        )

    def _apply_group_tension(
        self,
        members,
        amount
    ):
        for first in members:
            for second in members:
                if first is second:
                    continue

                relation = (
                    first.relationships.setdefault(
                        second.name,
                        {}
                    )
                )

                relation.setdefault(
                    "tension",
                    0.0
                )

                relation[
                    "tension"
                ] = min(
                    1.0,
                    float(
                        relation[
                            "tension"
                        ]
                    )
                    + amount
                )
