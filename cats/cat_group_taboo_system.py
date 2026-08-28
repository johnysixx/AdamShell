from copy import deepcopy
from uuid import uuid4


class CatGroupTabooSystem:

    def __init__(
        self,
        group_system
    ):
        self.group_system = group_system

    def define(
        self,
        group_id,
        name,
        taboo_type,
        target,
        severity=0.8
    ):
        group = self.group_system._group(
            group_id
        )

        taboo_id = (
            "cat_taboo_"
            + uuid4().hex[:8]
        )

        taboo = {
            "id": taboo_id,
            "name": name,
            "type": taboo_type,
            "target": deepcopy(
                target
            ),
            "severity": self._clamp(
                severity
            ),
            "violations": 0,
            "active": True
        }

        group[
            "taboos"
        ][
            taboo_id
        ] = taboo

        return {
            "name": "cat_group_taboo_defined",
            "group_id": group_id,
            "taboo_id": taboo_id,
            "taboo_name": name,
            "defined": True
        }

    def violate(
        self,
        group_id,
        cat,
        taboo_id,
        context=None
    ):
        group = self.group_system._group(
            group_id
        )

        taboo = group[
            "taboos"
        ].get(
            taboo_id
        )

        if taboo is None:
            return {
                "name": "cat_group_taboo_violation_denied",
                "reason": "unknown_taboo",
                "violated": False
            }

        taboo[
            "violations"
        ] += 1

        event = {
            "name": "cat_group_taboo_violated",
            "group_id": group_id,
            "cat": cat.name,
            "taboo_id": taboo_id,
            "taboo_name": taboo[
                "name"
            ],
            "severity": taboo[
                "severity"
            ],
            "target": deepcopy(
                taboo[
                    "target"
                ]
            ),
            "context": deepcopy(
                context
            ),
            "violated": True
        }

        group[
            "norm_violations"
        ].append(
            deepcopy(
                event
            )
        )

        cat.norms[
            "violations"
        ].append(
            deepcopy(
                event
            )
        )

        return event

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
