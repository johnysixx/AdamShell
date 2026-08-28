from copy import deepcopy
from uuid import uuid4


class CatGroupNormSystem:

    def __init__(
        self,
        group_system
    ):
        self.group_system = group_system

    def define(
        self,
        group_id,
        name,
        category,
        rule,
        importance=0.5
    ):
        group = self.group_system._group(
            group_id
        )

        norm_id = (
            "cat_norm_"
            + uuid4().hex[:8]
        )

        norm = {
            "id": norm_id,
            "name": name,
            "category": category,
            "rule": deepcopy(
                rule
            ),
            "importance": self._clamp(
                importance
            ),
            "observances": 0,
            "violations": 0,
            "active": True
        }

        group[
            "norms"
        ][
            norm_id
        ] = norm

        event = {
            "name": "cat_group_norm_defined",
            "group_id": group_id,
            "norm_id": norm_id,
            "norm_name": name,
            "category": category,
            "defined": True
        }

        group[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        return event

    def observe(
        self,
        group_id,
        cat,
        norm_id
    ):
        group = self.group_system._group(
            group_id
        )

        norm = group[
            "norms"
        ].get(
            norm_id
        )

        if norm is None:
            return {
                "name": "cat_group_norm_observation_denied",
                "reason": "unknown_norm",
                "observed": False
            }

        norm[
            "observances"
        ] += 1

        return {
            "name": "cat_group_norm_observed",
            "group_id": group_id,
            "cat": cat.name,
            "norm_id": norm_id,
            "observed": True
        }

    def violate(
        self,
        group_id,
        cat,
        norm_id,
        context=None
    ):
        group = self.group_system._group(
            group_id
        )

        norm = group[
            "norms"
        ].get(
            norm_id
        )

        if norm is None:
            return {
                "name": "cat_group_norm_violation_denied",
                "reason": "unknown_norm",
                "violated": False
            }

        norm[
            "violations"
        ] += 1

        violation = {
            "name": "cat_group_norm_violated",
            "group_id": group_id,
            "cat": cat.name,
            "norm_id": norm_id,
            "norm_name": norm[
                "name"
            ],
            "importance": norm[
                "importance"
            ],
            "context": deepcopy(
                context
            ),
            "violated": True
        }

        group[
            "norm_violations"
        ].append(
            deepcopy(
                violation
            )
        )

        group[
            "history"
        ].append(
            deepcopy(
                violation
            )
        )

        cat.norms[
            "violations"
        ].append(
            deepcopy(
                violation
            )
        )

        return violation

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
