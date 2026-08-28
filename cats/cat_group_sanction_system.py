from copy import deepcopy


class CatGroupSanctionSystem:

    def __init__(
        self,
        group_system
    ):
        self.group_system = group_system

    def sanction(
        self,
        group_id,
        cat,
        violation
    ):
        group = self.group_system._group(
            group_id
        )

        severity = float(
            violation.get(
                "severity",
                violation.get(
                    "importance",
                    0.5
                )
            )
        )

        previous = len(
            cat.norms[
                "sanctions"
            ]
        )

        effective = min(
            1.0,
            severity
            + previous * 0.08
        )

        if effective < 0.25:
            sanction_type = "warning"

        elif effective < 0.50:
            sanction_type = "social_avoidance"

        elif effective < 0.75:
            sanction_type = "trust_loss"

        elif effective < 0.90:
            sanction_type = "role_suspension"

        else:
            sanction_type = (
                "expulsion_recommended"
            )

        event = {
            "name": "cat_group_sanction",
            "group_id": group_id,
            "cat": cat.name,
            "sanction": sanction_type,
            "severity": round(
                effective,
                4
            ),
            "source_violation": deepcopy(
                violation
            )
        }

        self._apply(
            group,
            cat,
            sanction_type,
            effective
        )

        group[
            "sanction_history"
        ].append(
            deepcopy(
                event
            )
        )

        cat.norms[
            "sanctions"
        ].append(
            deepcopy(
                event
            )
        )

        return event

    def _apply(
        self,
        group,
        cat,
        sanction_type,
        severity
    ):
        if sanction_type == "warning":
            cat.norms[
                "warnings"
            ] += 1

        elif sanction_type == "social_avoidance":
            for member_name in group[
                "members"
            ]:
                if member_name == cat.name:
                    continue

                relation = cat.relationships.setdefault(
                    member_name,
                    {}
                )

                relation[
                    "affiliation"
                ] = max(
                    0.0,
                    float(
                        relation.get(
                            "affiliation",
                            0.0
                        )
                    )
                    - 0.05
                )

        elif sanction_type == "trust_loss":
            penalty = (
                0.15
                + severity * 0.15
            )

            cat.norms[
                "trust_penalties"
            ] += penalty

            for member_name in group[
                "members"
            ]:
                if member_name == cat.name:
                    continue

                relation = cat.relationships.setdefault(
                    member_name,
                    {}
                )

                relation[
                    "trust"
                ] = max(
                    0.0,
                    float(
                        relation.get(
                            "trust",
                            0.5
                        )
                    )
                    - penalty
                )

        elif sanction_type == "role_suspension":
            for role in list(
                cat.group_roles[
                    "active"
                ]
            ):
                holders = group[
                    "roles"
                ].get(
                    role,
                    []
                )

                if cat.name in holders:
                    holders.remove(
                        cat.name
                    )

                cat.group_roles[
                    "active"
                ].pop(
                    role,
                    None
                )

        elif sanction_type == (
            "expulsion_recommended"
        ):
            cat.state = (
                "group_expulsion_recommended"
            )
