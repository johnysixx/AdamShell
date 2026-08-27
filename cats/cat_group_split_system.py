from cats.cat_group_cultural_inheritance_system import (
    CatGroupCulturalInheritanceSystem
)

from copy import deepcopy


class CatGroupSplitSystem:

    def __init__(
        self,
        group_system
    ):
        self.group_system = group_system

    def split(
        self,
        group_id,
        cats,
        departing_members,
        new_name=None,
        reason="internal_split"
    ):
        parent = self.group_system._group(
            group_id
        )

        if parent.get(
            "dissolved",
            False
        ):
            return {
                "name": "cat_group_split_denied",
                "reason": "group_dissolved",
                "split": False
            }

        member_objects = (
            self.group_system
            ._member_objects(
                parent,
                cats
            )
        )

        by_name = {
            cat.name: cat
            for cat in member_objects
        }

        departing = [
            by_name[
                name
            ]
            for name in departing_members
            if name in by_name
        ]

        if (
            not departing
            or len(
                departing
            )
            >= len(
                member_objects
            )
        ):
            return {
                "name": "cat_group_split_denied",
                "reason": "invalid_departing_members",
                "split": False
            }

        founder = departing[0]

        # Temporarily detach founder so create_group
        # accepts it.
        for cat in departing:
            if cat.name in parent[
                "members"
            ]:
                parent[
                    "members"
                ].remove(
                    cat.name
                )

            cat.group[
                "group_id"
            ] = None

            cat.group[
                "member"
            ] = False

            cat.group[
                "joined_order"
            ] = None

            cat.group[
                "accepted_members"
            ] = []

        created = (
            self.group_system
            .create_group(
                founder,
                name=new_name
            )
        )

        daughter_id = created[
            "group_id"
        ]

        daughter = self.group_system._group(
            daughter_id
        )

        daughter[
            "parent_group"
        ] = group_id

        CatGroupCulturalInheritanceSystem(
            self.group_system
        ).inherit(
            parent_group_id=group_id,
            child_group_id=daughter_id,
            retention=0.70
        )

        for cat in departing[1:]:
            daughter[
                "members"
            ].append(
                cat.name
            )

            self.group_system._set_membership(
                cat,
                daughter_id,
                joined_order=len(
                    daughter[
                        "members"
                    ]
                )
            )

        parent[
            "split_count"
        ] += 1

        parent[
            "daughter_groups"
        ].append(
            daughter_id
        )

        event = {
            "name": "cat_group_split",
            "parent_group": group_id,
            "daughter_group": daughter_id,
            "departing_members": [
                cat.name
                for cat in departing
            ],
            "remaining_members": list(
                parent[
                    "members"
                ]
            ),
            "reason": reason,
            "split": True
        }

        parent[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        daughter[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        return event
