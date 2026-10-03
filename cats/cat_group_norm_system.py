from copy import deepcopy
from uuid import uuid4
from cats.cat_culture_objects import CatGroupNorm
from cats.cat_culture_objects import CatNormViolation
from cats.cat_group_norm_observation_state import (
    CatGroupNormObservationDeniedResult,
    CatGroupNormObservedResult,
)
from cats.cat_group_norm_definition_state import (
    CatGroupNormDefinedEvent,
)
from cats.cat_group_norm_violation_state import (
    CatGroupNormViolationDeniedResult,
)


class CatGroupNormSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def define(
        self,
        group_id,
        name,
        category,
        rule,
        importance=0.5,
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        norm_id = (
            "cat_norm_"
            + uuid4().hex[:8]
        )

        norm = CatGroupNorm(
            **{
                "id": norm_id,
                "name": name,
                "category": category,
                "rule": deepcopy(rule),
                "importance": self._clamp(
                    importance
                ),
                "observances": 0,
                "violations": 0,
                "active": True,
            }
        )

        group.norms[
            norm_id
        ] = norm

        event = (
            CatGroupNormDefinedEvent(
                group_id=group_id,
                norm_id=norm_id,
                norm_name=name,
                category=category,
            )
        )

        group.history.append(
            event.to_dict()
        )

        return event

    def observe(
        self,
        group_id,
        cat,
        norm_id,
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        norm = group.norms.get(
            norm_id
        )

        if norm is None:
            return (
                CatGroupNormObservationDeniedResult(
                    reason="unknown_norm",
                )
            )

        norm.observances += 1

        return (
            CatGroupNormObservedResult(
                group_id=group_id,
                cat=cat.name,
                norm_id=norm_id,
            )
        )

    def violate(
        self,
        group_id,
        cat,
        norm_id,
        context=None,
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        norm = group.norms.get(
            norm_id
        )

        if norm is None:
            return (
                CatGroupNormViolationDeniedResult(
                    reason="unknown_norm",
                )
            )

        norm.violations += 1
        violation = CatNormViolation(**{'name': 'cat_group_norm_violated', 'group_id': group_id, 'cat': cat.name, 'norm_id': norm_id, 'norm_name': norm.name, 'importance': norm.importance, 'context': deepcopy(context), 'violated': True})
        group.norm_violations.append(deepcopy(violation))
        group.history.append(deepcopy(violation))
        cat.norms.violations.append(deepcopy(violation))
        return violation

    def _clamp(self, value):
        return max(0.0, min(1.0, float(value)))
