from copy import deepcopy


class CatGroupCulturalInheritanceSystem:

    def __init__(
        self,
        group_system
    ):
        self.group_system = group_system

    def inherit(
        self,
        parent_group_id,
        child_group_id,
        retention=0.70
    ):
        parent = self.group_system._group(
            parent_group_id
        )

        child = self.group_system._group(
            child_group_id
        )

        retention = self._clamp(
            retention
        )

        child[
            "cultural_parent_group"
        ] = parent_group_id

        if (
            child_group_id
            not in parent[
                "cultural_children"
            ]
        ):
            parent[
                "cultural_children"
            ].append(
                child_group_id
            )

        parent_culture = parent[
            "culture"
        ]

        child_culture = child[
            "culture"
        ]

        for trait, value in parent_culture[
            "traits"
        ].items():
            child_culture[
                "traits"
            ][
                trait
            ] = self._clamp(
                float(value)
                * retention
            )

        for name, tradition in parent_culture[
            "traditions"
        ].items():
            inherited = deepcopy(
                tradition
            )

            inherited[
                "strength"
            ] = self._clamp(
                float(
                    inherited.get(
                        "strength",
                        0.0
                    )
                )
                * retention
            )

            inherited[
                "inherited_from"
            ] = parent_group_id

            child_culture[
                "traditions"
            ][
                name
            ] = inherited

        for name, preference in parent_culture[
            "preferences"
        ].items():
            inherited = deepcopy(
                preference
            )

            inherited[
                "strength"
            ] = self._clamp(
                float(
                    inherited.get(
                        "strength",
                        0.0
                    )
                )
                * retention
            )

            inherited[
                "inherited_from"
            ] = parent_group_id

            child_culture[
                "preferences"
            ][
                name
            ] = inherited

        event = {
            "name": "cat_group_culture_inherited",
            "parent_group": parent_group_id,
            "child_group": child_group_id,
            "retention": retention,
            "inherited_traits": list(
                child_culture[
                    "traits"
                ]
            ),
            "inherited_traditions": list(
                child_culture[
                    "traditions"
                ]
            ),
            "inherited_preferences": list(
                child_culture[
                    "preferences"
                ]
            )
        }

        parent[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        child[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        return event

    def divergence(
        self,
        parent_group_id,
        child_group_id
    ):
        parent = self.group_system._group(
            parent_group_id
        )

        child = self.group_system._group(
            child_group_id
        )

        parent_traits = parent[
            "culture"
        ][
            "traits"
        ]

        child_traits = child[
            "culture"
        ][
            "traits"
        ]

        keys = set(
            parent_traits
        ) | set(
            child_traits
        )

        if not keys:
            return {
                "parent_group": parent_group_id,
                "child_group": child_group_id,
                "divergence": 0.0
            }

        difference = 0.0

        for key in keys:
            difference += abs(
                float(
                    parent_traits.get(
                        key,
                        0.0
                    )
                )
                - float(
                    child_traits.get(
                        key,
                        0.0
                    )
                )
            )

        divergence = min(
            1.0,
            difference
            / len(
                keys
            )
        )

        return {
            "parent_group": parent_group_id,
            "child_group": child_group_id,
            "divergence": round(
                divergence,
                4
            )
        }

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
