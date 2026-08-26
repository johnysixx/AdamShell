from copy import deepcopy

from cats.cat import Cat
from cats.cat_family_system import (
    CatFamilySystem
)


class CatSiblingRivalrySystem:

    def __init__(
        self,
        cats_layer=None
    ):
        self.cats_layer = cats_layer

        self.family_system = (
            CatFamilySystem(
                cats_layer
            )
        )

    def compete(
        self,
        first,
        second,
        resource,
        intensity=0.5
    ):
        self._require_cat(first)
        self._require_cat(second)

        relation = (
            self.family_system.relation(
                first,
                second
            )
        )

        if relation not in {
            "sibling",
            "half_sibling",
            "sibling_littermate",
            "half_sibling_littermate"
        }:
            return {
                "name": "sibling_rivalry_denied",
                "first": first.name,
                "second": second.name,
                "reason": "not_siblings",
                "competed": False
            }

        intensity = self._clamp(
            intensity
        )

        first_relation = self._relationship(
            first,
            second
        )

        second_relation = self._relationship(
            second,
            first
        )

        bonded = bool(
            first.bonds.get(
                second.name,
                {}
            ).get(
                "active",
                False
            )
        )

        tension_gain = (
            0.12
            * intensity
            * (
                0.5
                if bonded
                else 1.0
            )
        )

        for relationship in (
            first_relation,
            second_relation
        ):
            relationship[
                "familiarity"
            ] = self._clamp(
                relationship[
                    "familiarity"
                ]
                + 0.02
            )

            relationship[
                "tension"
            ] = self._clamp(
                relationship[
                    "tension"
                ]
                + tension_gain
            )

            relationship[
                "affiliation"
            ] = self._clamp(
                relationship[
                    "affiliation"
                ]
                - 0.04 * intensity
            )

            relationship[
                "last_interaction"
            ] = "sibling_rivalry"

        tension = max(
            first_relation[
                "tension"
            ],
            second_relation[
                "tension"
            ]
        )

        if tension < 0.35:
            outcome = (
                "playful_competition"
            )
        elif tension < 0.70:
            outcome = (
                "warning_competition"
            )
        else:
            outcome = (
                "sibling_conflict"
            )

        event = {
            "name": "cat_sibling_rivalry",
            "first": first.name,
            "second": second.name,
            "relation": relation,
            "resource": resource,
            "intensity": intensity,
            "outcome": outcome,
            "bonded": bonded,
            "competed": True
        }

        self._record(
            first,
            second,
            resource,
            event
        )

        return event

    def reconcile(
        self,
        first,
        second
    ):
        self._require_cat(first)
        self._require_cat(second)

        relation = (
            self.family_system.relation(
                first,
                second
            )
        )

        if relation not in {
            "sibling",
            "half_sibling",
            "sibling_littermate",
            "half_sibling_littermate"
        }:
            return {
                "name": (
                    "sibling_reconciliation_denied"
                ),
                "reconciled": False
            }

        for cat, other in (
            (first, second),
            (second, first)
        ):
            relationship = (
                self._relationship(
                    cat,
                    other
                )
            )

            relationship[
                "tension"
            ] = self._clamp(
                relationship[
                    "tension"
                ]
                - 0.15
            )

            relationship[
                "affiliation"
            ] = self._clamp(
                relationship[
                    "affiliation"
                ]
                + 0.05
            )

        event = {
            "name": (
                "cat_siblings_reconciled"
            ),
            "first": first.name,
            "second": second.name,
            "reconciled": True
        }

        first.social_interactions.append(
            deepcopy(event)
        )

        second.social_interactions.append(
            deepcopy(event)
        )

        return event

    def _relationship(
        self,
        cat,
        other_cat
    ):
        relation = (
            cat.relationships.setdefault(
                other_cat.name,
                {}
            )
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

        return relation

    def _record(
        self,
        first,
        second,
        resource,
        event
    ):
        for cat, rival in (
            (first, second),
            (second, first)
        ):
            state = cat.sibling_rivalry

            state[
                "events"
            ] += 1

            state[
                "last_rival"
            ] = rival.name

            state[
                "last_resource"
            ] = resource

            rivals = state[
                "rivals"
            ]

            rivals[
                rival.name
            ] = int(
                rivals.get(
                    rival.name,
                    0
                )
            ) + 1

            cat.social_interactions.append(
                deepcopy(event)
            )

    def _clamp(
        self,
        value
    ):
        return max(
            0.0,
            min(
                1.0,
                float(value)
            )
        )

    def _require_cat(
        self,
        cat
    ):
        if not isinstance(cat, Cat):
            raise TypeError(
                "CatSiblingRivalrySystem "
                "requires Cat."
            )
