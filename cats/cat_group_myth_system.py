from copy import deepcopy
from uuid import uuid4


class CatGroupMythSystem:

    def __init__(
        self,
        group_system
    ):
        self.group_system = group_system

    def create_from_knowledge(
        self,
        group_id,
        knowledge_id,
        title=None,
        interpretation=None
    ):
        group = self.group_system._group(
            group_id
        )

        knowledge = group[
            "knowledge"
        ].get(
            knowledge_id
        )

        if knowledge is None:
            return {
                "name": "cat_group_myth_creation_denied",
                "reason": "unknown_knowledge",
                "created": False
            }

        myth_id = (
            "cat_myth_"
            + uuid4().hex[:8]
        )

        myth = {
            "myth_id": myth_id,
            "title": (
                title
                if title is not None
                else knowledge_id
            ),
            "source_knowledge": knowledge_id,
            "origin_group": group_id,
            "interpretation": (
                deepcopy(
                    interpretation
                )
                if interpretation is not None
                else deepcopy(
                    knowledge[
                        "content"
                    ]
                )
            ),
            "credibility": self._clamp(
                float(
                    knowledge.get(
                        "confidence",
                        0.5
                    )
                )
                * 0.75
            ),
            "verified": False,
            "retellings": 0,
            "transformations": 0,
            "transmission_path": [
                group_id
            ]
        }

        group[
            "myths"
        ][
            myth_id
        ] = myth

        event = {
            "name": "cat_group_myth_created",
            "group_id": group_id,
            "myth_id": myth_id,
            "source_knowledge": knowledge_id,
            "created": True
        }

        group[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        return event

    def retell(
        self,
        source_group_id,
        target_group_id,
        myth_id,
        transformation=None
    ):
        source = self.group_system._group(
            source_group_id
        )

        target = self.group_system._group(
            target_group_id
        )

        myth = source[
            "myths"
        ].get(
            myth_id
        )

        if myth is None:
            return {
                "name": "cat_group_myth_retelling_denied",
                "reason": "unknown_myth",
                "retold": False
            }

        copied = deepcopy(
            myth
        )

        copied[
            "retellings"
        ] += 1

        copied[
            "credibility"
        ] = self._clamp(
            float(
                copied[
                    "credibility"
                ]
            )
            * 0.92
        )

        copied[
            "transmission_path"
        ].append(
            target_group_id
        )

        if transformation is not None:
            copied[
                "interpretation"
            ] = deepcopy(
                transformation
            )

            copied[
                "transformations"
            ] += 1

            copied[
                "credibility"
            ] = self._clamp(
                copied[
                    "credibility"
                ]
                * 0.85
            )

        copied[
            "verified"
        ] = False

        target[
            "myths"
        ][
            myth_id
        ] = copied

        return {
            "name": "cat_group_myth_retold",
            "source_group": source_group_id,
            "target_group": target_group_id,
            "myth_id": myth_id,
            "credibility": copied[
                "credibility"
            ],
            "transformed": (
                transformation is not None
            ),
            "retold": True
        }

    def tell_members(
        self,
        group_id,
        cats,
        myth_id
    ):
        group = self.group_system._group(
            group_id
        )

        myth = group[
            "myths"
        ].get(
            myth_id
        )

        if myth is None:
            return {
                "name": "cat_group_myth_telling_denied",
                "reason": "unknown_myth",
                "told": False
            }

        listeners = []

        for cat in (
            self.group_system
            ._member_objects(
                group,
                cats
            )
        ):
            heard = cat.knowledge.setdefault(
                "heard_group_myths",
                {}
            )

            personal = deepcopy(
                myth
            )

            personal[
                "heard_from_group"
            ] = group_id

            personal[
                "personally_verified"
            ] = False

            heard[
                myth_id
            ] = personal

            listeners.append(
                cat.name
            )

        return {
            "name": "cat_group_myth_told",
            "group_id": group_id,
            "myth_id": myth_id,
            "listeners": listeners,
            "told": True
        }

    def verify_against_knowledge(
        self,
        group_id,
        myth_id
    ):
        group = self.group_system._group(
            group_id
        )

        myth = group[
            "myths"
        ].get(
            myth_id
        )

        if myth is None:
            return {
                "name": "cat_group_myth_verification_denied",
                "reason": "unknown_myth",
                "verified": False
            }

        knowledge = group[
            "knowledge"
        ].get(
            myth[
                "source_knowledge"
            ]
        )

        if knowledge is None:
            return {
                "name": "cat_group_myth_verification_denied",
                "reason": "source_knowledge_missing",
                "verified": False
            }

        myth[
            "verified"
        ] = bool(
            knowledge.get(
                "verified",
                False
            )
        )

        if myth[
            "verified"
        ]:
            myth[
                "credibility"
            ] = self._clamp(
                max(
                    myth[
                        "credibility"
                    ],
                    float(
                        knowledge.get(
                            "confidence",
                            0.0
                        )
                    )
                )
            )

        return {
            "name": "cat_group_myth_verified",
            "group_id": group_id,
            "myth_id": myth_id,
            "verified": myth[
                "verified"
            ],
            "credibility": myth[
                "credibility"
            ]
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
