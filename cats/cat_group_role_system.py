from copy import deepcopy


class CatGroupRoleSystem:

    ROLE_PROFILES = {
        "storyteller": {
            "traits": {
                "sociability": 0.45,
                "curiosity": 0.35
            },
            "knowledge_weight": 0.20
        },
        "scout": {
            "traits": {
                "curiosity": 0.55,
                "courage": 0.35
            },
            "knowledge_weight": 0.10
        },
        "guardian": {
            "traits": {
                "courage": 0.60
            },
            "influence_weight": 0.40
        },
        "kitten_teacher": {
            "traits": {
                "sociability": 0.40
            },
            "knowledge_weight": 0.35
        },
        "scent_keeper": {
            "traits": {
                "sociability": 0.30
            },
            "group_scent_weight": 0.50
        },
        "mediator": {
            "traits": {
                "sociability": 0.55
            },
            "influence_weight": 0.30
        }
    }

    def __init__(
        self,
        group_system
    ):
        self.group_system = group_system

    def suitability(
        self,
        group_id,
        cat,
        role
    ):
        group = self.group_system._group(
            group_id
        )

        if cat.name not in group[
            "members"
        ]:
            return {
                "role": role,
                "eligible": False,
                "score": 0.0,
                "reason": "not_group_member"
            }

        profile = self.ROLE_PROFILES.get(
            role
        )

        if profile is None:
            return {
                "role": role,
                "eligible": False,
                "score": 0.0,
                "reason": "unknown_role"
            }

        traits = cat.personality.get(
            "traits",
            {}
        )

        score = 0.0

        for trait, weight in profile.get(
            "traits",
            {}
        ).items():
            score += self._number(
                traits.get(
                    trait,
                    0.5
                )
            ) * weight

        score += self._number(
            cat.group.get(
                "influence",
                0.0
            )
        ) * profile.get(
            "influence_weight",
            0.0
        )

        score += min(
            1.0,
            len(
                cat.knowledge
            ) / 10.0
        ) * profile.get(
            "knowledge_weight",
            0.0
        )

        score += self._number(
            cat.group.get(
                "shared_scent",
                0.0
            )
        ) * profile.get(
            "group_scent_weight",
            0.0
        )

        score = min(
            1.0,
            score
        )

        return {
            "role": role,
            "eligible": (
                score >= 0.35
            ),
            "score": round(
                score,
                4
            )
        }

    def assign(
        self,
        group_id,
        cat,
        role
    ):
        check = self.suitability(
            group_id,
            cat,
            role
        )

        if not check[
            "eligible"
        ]:
            return {
                "name": "cat_group_role_denied",
                "group_id": group_id,
                "cat": cat.name,
                "role": role,
                "reason": check.get(
                    "reason",
                    "insufficient_suitability"
                ),
                "assigned": False
            }

        group = self.group_system._group(
            group_id
        )

        holders = group[
            "roles"
        ].setdefault(
            role,
            []
        )

        if cat.name not in holders:
            holders.append(
                cat.name
            )

        cat.group_roles[
            "active"
        ][
            role
        ] = {
            "group_id": group_id,
            "score": check[
                "score"
            ]
        }

        cat.group_roles[
            "role_events"
        ] += 1

        event = {
            "name": "cat_group_role_assigned",
            "group_id": group_id,
            "cat": cat.name,
            "role": role,
            "score": check[
                "score"
            ],
            "assigned": True
        }

        cat.group_roles[
            "history"
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

    def release(
        self,
        group_id,
        cat,
        role,
        reason="role_released"
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

        event = {
            "name": "cat_group_role_released",
            "group_id": group_id,
            "cat": cat.name,
            "role": role,
            "reason": reason,
            "released": True
        }

        cat.group_roles[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        return event

    def holders(
        self,
        group_id,
        role
    ):
        group = self.group_system._group(
            group_id
        )

        return list(
            group[
                "roles"
            ].get(
                role,
                []
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
