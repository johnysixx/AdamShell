from copy import deepcopy

from cats.cat_group_role_system import (
    CatGroupRoleSystem
)


class CatGroupSuccessionSystem:

    def __init__(
        self,
        group_system
    ):
        self.group_system = group_system

        self.roles = CatGroupRoleSystem(
            group_system
        )

    def candidates(
        self,
        group_id,
        role,
        cats,
        exclude=None
    ):
        group = self.group_system._group(
            group_id
        )

        excluded = set(
            exclude or []
        )

        members = (
            self.group_system
            ._member_objects(
                group,
                cats
            )
        )

        ranked = []

        for cat in members:
            if cat.name in excluded:
                continue

            check = self.roles.suitability(
                group_id,
                cat,
                role
            )

            if not check[
                "eligible"
            ]:
                continue

            # Experience in the group and influence
            # slightly improve succession suitability.
            score = (
                float(
                    check[
                        "score"
                    ]
                )
                + min(
                    0.15,
                    int(
                        cat.group.get(
                            "group_events",
                            0
                        )
                    ) * 0.005
                )
                + float(
                    cat.group.get(
                        "influence",
                        0.0
                    )
                ) * 0.10
            )

            ranked.append({
                "cat": cat,
                "cat_name": cat.name,
                "score": round(
                    min(
                        1.0,
                        score
                    ),
                    4
                )
            })

        ranked.sort(
            key=lambda item: (
                item[
                    "score"
                ],
                item[
                    "cat_name"
                ]
            ),
            reverse=True
        )

        return ranked

    def succeed(
        self,
        group_id,
        vacated_cat,
        role,
        cats,
        reason="role_vacated"
    ):
        group = self.group_system._group(
            group_id
        )

        holders = group[
            "roles"
        ].get(
            role,
            []
        )

        was_holder = (
            vacated_cat.name
            in holders
        )

        if was_holder:
            self.roles.release(
                group_id,
                vacated_cat,
                role,
                reason=reason
            )

        ranked = self.candidates(
            group_id,
            role,
            cats,
            exclude=[
                vacated_cat.name
            ]
        )

        if not ranked:
            self._weaken_dependent_institutions(
                group,
                role,
                amount=0.20
            )

            event = {
                "name": (
                    "cat_group_role_became_vacant"
                ),
                "group_id": group_id,
                "role": role,
                "previous_holder": (
                    vacated_cat.name
                ),
                "reason": reason,
                "successor": None,
                "succeeded": False
            }

            group[
                "succession_history"
            ].append(
                deepcopy(
                    event
                )
            )

            group[
                "history"
            ].append(
                deepcopy(
                    event
                )
            )

            return event

        successor = ranked[0][
            "cat"
        ]

        assigned = self.roles.assign(
            group_id,
            successor,
            role
        )

        if not assigned.get(
            "assigned",
            False
        ):
            raise RuntimeError(
                "Selected succession candidate "
                "could not be assigned."
            )

        self._strengthen_dependent_institutions(
            group,
            role,
            amount=0.05
        )

        event = {
            "name": (
                "cat_group_role_succeeded"
            ),
            "group_id": group_id,
            "role": role,
            "previous_holder": (
                vacated_cat.name
            ),
            "successor": successor.name,
            "successor_score": (
                ranked[0][
                    "score"
                ]
            ),
            "reason": reason,
            "succeeded": True
        }

        group[
            "succession_history"
        ].append(
            deepcopy(
                event
            )
        )

        group[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        return event

    def handle_departure(
        self,
        group_id,
        cat,
        cats,
        reason="cat_left_group"
    ):
        group = self.group_system._group(
            group_id
        )

        roles = list(
            cat.group_roles[
                "active"
            ].keys()
        )

        succession_events = []

        for role in roles:
            succession_events.append(
                self.succeed(
                    group_id,
                    cat,
                    role,
                    cats,
                    reason=reason
                )
            )

        leave_result = (
            self.group_system
            .leave_group(
                group_id,
                cat
            )
        )

        return {
            "name": (
                "cat_group_departure_with_succession"
            ),
            "group_id": group_id,
            "cat": cat.name,
            "roles": roles,
            "successions": (
                succession_events
            ),
            "leave_result": leave_result,
            "departed": bool(
                leave_result.get(
                    "left",
                    False
                )
            )
        }

    def _weaken_dependent_institutions(
        self,
        group,
        role,
        amount
    ):
        for institution in group[
            "institutions"
        ].values():
            if (
                role
                not in institution.get(
                    "roles",
                    []
                )
            ):
                continue

            institution[
                "continuity"
            ] = max(
                0.0,
                float(
                    institution.get(
                        "continuity",
                        1.0
                    )
                )
                - amount
            )

            if institution[
                "continuity"
            ] <= 0.10:
                institution[
                    "active"
                ] = False

    def _strengthen_dependent_institutions(
        self,
        group,
        role,
        amount
    ):
        for institution in group[
            "institutions"
        ].values():
            if (
                role
                not in institution.get(
                    "roles",
                    []
                )
            ):
                continue

            institution[
                "continuity"
            ] = min(
                1.0,
                float(
                    institution.get(
                        "continuity",
                        1.0
                    )
                )
                + amount
            )
