from copy import deepcopy
from uuid import uuid4

from cats.cat import Cat
from cats.cat_territory_system import (
    CatTerritorySystem
)


class CatGroupSystem:

    def __init__(
        self,
        cats_layer=None
    ):
        self.cats_layer = cats_layer

        self.groups = {}

        self.territory_system = (
            CatTerritorySystem(
                cats_layer
            )
        )

    def create_group(
        self,
        founder,
        name=None
    ):
        self._require_cat(
            founder
        )

        if founder.group[
            "member"
        ]:
            return {
                "name": "cat_group_creation_denied",
                "cat": founder.name,
                "reason": "already_group_member",
                "created": False
            }

        group_id = (
            "cat_group_"
            + uuid4().hex[:8]
        )

        group = {
            "id": group_id,
            "name": (
                name
                if name is not None
                else group_id
            ),
            "founder": founder.name,
            "members": [
                founder.name
            ],
            "shared_scent_strength": 0.0,
            "territories": {},
            "threat_events": 0,

            # Group lifecycle
            "state": "forming",
            "age_ticks": 0,
            "migration_count": 0,
            "conflict_count": 0,
            "split_count": 0,
            "parent_group": None,
            "daughter_groups": [],
            "dissolved": False,

            # Persistent inter-group relations
            "group_memory": {},
            "diplomacy": {},
            "alliances": [],

            # Collective knowledge is not automatically
            # believed by every individual cat.
            "knowledge": {},

            # Emergent group culture.
            "culture": {
                "traits": {},
                "traditions": {},
                "preferences": {},
                "history": []
            },

            # Stories derived from knowledge but not
            # necessarily verified as literal fact.
            "myths": {},

            # Novel procedures created from existing
            # knowledge.
            "innovations": {},

            # Federation memberships stay separate
            # from ordinary group alliances.
            "federations": [],

            # Current collective location
            "current_layer": (
                founder.current_layer
            ),
            "current_location": (
                founder.location
            ),

            "history": []
        }

        self.groups[
            group_id
        ] = group

        self._set_membership(
            founder,
            group_id,
            joined_order=1
        )

        event = {
            "name": "cat_group_created",
            "group_id": group_id,
            "group_name": group[
                "name"
            ],
            "founder": founder.name,
            "created": True
        }

        self._record(
            group,
            event,
            cats=[
                founder
            ]
        )

        return {
            **event,
            "group": deepcopy(
                group
            )
        }

    def evaluate_candidate(
        self,
        group_id,
        candidate,
        cats
    ):
        self._require_cat(
            candidate
        )

        group = self._group(
            group_id
        )

        if candidate.name in group[
            "members"
        ]:
            return {
                "group_id": group_id,
                "candidate": candidate.name,
                "accepted": True,
                "reason": "already_member",
                "score": 1.0
            }

        if candidate.group[
            "member"
        ]:
            return {
                "group_id": group_id,
                "candidate": candidate.name,
                "accepted": False,
                "reason": "member_of_other_group",
                "score": 0.0
            }

        members = self._member_objects(
            group,
            cats
        )

        if not members:
            return {
                "group_id": group_id,
                "candidate": candidate.name,
                "accepted": False,
                "reason": "group_members_unavailable",
                "score": 0.0
            }

        total = 0.0

        hostile = 0

        for member in members:
            relation = member.relationships.get(
                candidate.name,
                {}
            )

            trust = self._number(
                relation.get(
                    "trust",
                    0.5
                )
            )

            affiliation = self._number(
                relation.get(
                    "affiliation",
                    0.0
                )
            )

            tension = self._number(
                relation.get(
                    "tension",
                    0.0
                )
            )

            familiarity = self._number(
                relation.get(
                    "familiarity",
                    0.0
                )
            )

            score = (
                trust * 0.40
                + affiliation * 0.25
                + familiarity * 0.15
                + 0.20
                - tension * 0.55
            )

            total += score

            if (
                tension >= 0.70
                or trust <= 0.15
            ):
                hostile += 1

        average = (
            total
            / len(
                members
            )
        )

        accepted = bool(
            hostile == 0
            and average >= 0.35
        )

        return {
            "group_id": group_id,
            "candidate": candidate.name,
            "accepted": accepted,
            "reason": (
                "socially_accepted"
                if accepted
                else "group_social_rejection"
            ),
            "score": round(
                average,
                4
            ),
            "hostile_members": hostile,
            "member_count": len(
                members
            )
        }

    def add_member(
        self,
        group_id,
        candidate,
        cats
    ):
        check = self.evaluate_candidate(
            group_id=group_id,
            candidate=candidate,
            cats=cats
        )

        if not check[
            "accepted"
        ]:
            return {
                "name": "cat_group_join_denied",
                **check,
                "joined": False
            }

        group = self._group(
            group_id
        )

        if candidate.name in group[
            "members"
        ]:
            return {
                "name": "cat_group_join_skipped",
                "group_id": group_id,
                "cat": candidate.name,
                "reason": "already_member",
                "joined": False
            }

        group[
            "members"
        ].append(
            candidate.name
        )

        self._set_membership(
            candidate,
            group_id,
            joined_order=len(
                group[
                    "members"
                ]
            )
        )

        members = self._member_objects(
            group,
            cats
        )

        for member in members:
            if member is candidate:
                continue

            self._ensure_relationship(
                member,
                candidate
            )

            self._ensure_relationship(
                candidate,
                member
            )

            if (
                member.name
                not in candidate.group[
                    "accepted_members"
                ]
            ):
                candidate.group[
                    "accepted_members"
                ].append(
                    member.name
                )

            if (
                candidate.name
                not in member.group[
                    "accepted_members"
                ]
            ):
                member.group[
                    "accepted_members"
                ].append(
                    candidate.name
                )

        event = {
            "name": "cat_joined_group",
            "group_id": group_id,
            "cat": candidate.name,
            "member_count": len(
                group[
                    "members"
                ]
            ),
            "joined": True
        }

        self._record(
            group,
            event,
            cats=members
        )

        return event

    def mix_group_scent(
        self,
        group_id,
        cats,
        amount=0.10
    ):
        group = self._group(
            group_id
        )

        members = self._member_objects(
            group,
            cats
        )

        if len(
            members
        ) < 2:
            return {
                "name": "cat_group_scent_not_mixed",
                "group_id": group_id,
                "reason": "not_enough_members",
                "mixed": False
            }

        amount = max(
            0.0,
            float(
                amount
            )
        )

        group[
            "shared_scent_strength"
        ] = self._clamp(
            self._number(
                group.get(
                    "shared_scent_strength",
                    0.0
                )
            )
            + amount
        )

        for first in members:
            first.group[
                "shared_scent"
            ] = group[
                "shared_scent_strength"
            ]

            for second in members:
                if first is second:
                    continue

                relation = self._ensure_relationship(
                    first,
                    second
                )

                relation[
                    "shared_scent"
                ] = self._clamp(
                    self._number(
                        relation.get(
                            "shared_scent",
                            0.0
                        )
                    )
                    + amount
                )

                relation[
                    "familiarity"
                ] = self._clamp(
                    self._number(
                        relation.get(
                            "familiarity",
                            0.0
                        )
                    )
                    + amount * 0.50
                )

        event = {
            "name": "cat_group_scent_mixed",
            "group_id": group_id,
            "members": [
                cat.name
                for cat in members
            ],
            "shared_scent_strength": (
                group[
                    "shared_scent_strength"
                ]
            ),
            "mixed": True
        }

        self._record(
            group,
            event,
            cats=members
        )

        return event

    def claim_territory(
        self,
        group_id,
        cats,
        layer,
        location,
        strength=0.7
    ):
        group = self._group(
            group_id
        )

        members = self._member_objects(
            group,
            cats
        )

        key = (
            f"{layer}::"
            f"{location}"
        )

        claims = []

        for member in members:
            claim = (
                self.territory_system
                .claim(
                    member,
                    layer=layer,
                    location=location,
                    strength=strength
                )
            )

            claims.append(
                deepcopy(
                    claim
                )
            )

        group[
            "territories"
        ][
            key
        ] = {
            "layer": layer,
            "location": location,
            "strength": self._clamp(
                strength
            ),
            "members": [
                member.name
                for member in members
            ]
        }

        event = {
            "name": "cat_group_territory_claimed",
            "group_id": group_id,
            "territory": key,
            "member_count": len(
                members
            ),
            "claimed": True
        }

        self._record(
            group,
            event,
            cats=members
        )

        return {
            **event,
            "claims": claims
        }

    def respond_to_threat(
        self,
        group_id,
        cats,
        threat
    ):
        group = self._group(
            group_id
        )

        members = self._member_objects(
            group,
            cats
        )

        if isinstance(
            threat,
            dict
        ):
            threat_name = threat.get(
                "name"
            )
        else:
            threat_name = getattr(
                threat,
                "name",
                str(
                    threat
                )
            )

        defenders = []

        withdrawers = []

        for member in members:
            traits = (
                member.personality.get(
                    "traits",
                    {}
                )
            )

            courage = self._number(
                traits.get(
                    "courage",
                    0.5
                )
            )

            aggression = self._number(
                traits.get(
                    "aggression",
                    0.0
                )
            )

            group_support = min(
                0.30,
                max(
                    0,
                    len(
                        members
                    ) - 1
                ) * 0.08
            )

            defense_score = (
                courage
                + aggression * 0.35
                + group_support
            )

            if defense_score >= 0.55:
                member.state = (
                    "group_defending"
                )

                member.group[
                    "defense_events"
                ] += 1

                defenders.append(
                    member.name
                )
            else:
                member.state = (
                    "group_withdrawing"
                )

                withdrawers.append(
                    member.name
                )

        group[
            "threat_events"
        ] += 1

        event = {
            "name": "cat_group_threat_response",
            "group_id": group_id,
            "threat": threat_name,
            "defenders": defenders,
            "withdrawers": withdrawers,
            "member_count": len(
                members
            ),
            "responded": True
        }

        self._record(
            group,
            event,
            cats=members
        )

        return event

    def leave_group(
        self,
        group_id,
        cat
    ):
        self._require_cat(
            cat
        )

        group = self._group(
            group_id
        )

        if cat.name not in group[
            "members"
        ]:
            return {
                "name": "cat_group_leave_denied",
                "group_id": group_id,
                "cat": cat.name,
                "reason": "not_member",
                "left": False
            }

        group[
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
            "shared_scent"
        ] = 0.0

        cat.group[
            "accepted_members"
        ] = []

        event = {
            "name": "cat_left_group",
            "group_id": group_id,
            "cat": cat.name,
            "member_count": len(
                group[
                    "members"
                ]
            ),
            "left": True
        }

        self._record(
            group,
            event,
            cats=[
                cat
            ]
        )

        return event

    def same_group(
        self,
        first,
        second
    ):
        self._require_cat(
            first
        )

        self._require_cat(
            second
        )

        return bool(
            first.group[
                "member"
            ]
            and second.group[
                "member"
            ]
            and first.group[
                "group_id"
            ]
            == second.group[
                "group_id"
            ]
        )

    def _set_membership(
        self,
        cat,
        group_id,
        joined_order
    ):
        cat.group[
            "group_id"
        ] = group_id

        cat.group[
            "member"
        ] = True

        cat.group[
            "joined_order"
        ] = joined_order

        cat.group[
            "group_events"
        ] += 1

    def _member_objects(
        self,
        group,
        cats
    ):
        by_name = {
            cat.name: cat
            for cat in cats
            if isinstance(
                cat,
                Cat
            )
        }

        return [
            by_name[
                name
            ]
            for name in group[
                "members"
            ]
            if name in by_name
        ]

    def _ensure_relationship(
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

        relation.setdefault(
            "last_interaction",
            None
        )

        return relation

    def _group(
        self,
        group_id
    ):
        group = self.groups.get(
            group_id
        )

        if group is None:
            raise KeyError(
                f"Unknown cat group: "
                f"{group_id}"
            )

        return group

    def _record(
        self,
        group,
        event,
        cats
    ):
        group[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        for cat in cats:
            cat.group[
                "group_events"
            ] += 1

            cat.social_interactions.append(
                deepcopy(
                    event
                )
            )

        emit_event = getattr(
            self.cats_layer,
            "emit_event",
            None
        )

        if callable(
            emit_event
        ):
            emit_event(
                deepcopy(
                    event
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

    def _require_cat(
        self,
        cat
    ):
        if not isinstance(
            cat,
            Cat
        ):
            raise TypeError(
                "CatGroupSystem requires Cat."
            )
