from copy import deepcopy

from cats.cat_group_role_system import (
    CatGroupRoleSystem,
)
from cats.cat_group_succession_state import (
    CatGroupDepartureWithSuccessionResult,
    CatGroupRoleBecameVacantEvent,
    CatGroupRoleSucceededEvent,
    CatGroupSuccessionCandidate,
)


class CatGroupSuccessionSystem:

    def __init__(
        self,
        group_system,
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
        exclude=None,
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
                cats,
            )
        )

        ranked = []

        for cat in members:
            if cat.name in excluded:
                continue

            check = self.roles.suitability(
                group_id,
                cat,
                role,
            )

            if not check.eligible:
                continue

            score = (
                float(
                    check.score
                )
                + min(
                    0.15,
                    int(
                        cat.group.group_events
                    )
                    * 0.005,
                )
                + float(
                    cat.group.influence
                )
                * 0.1
            )

            ranked.append(
                CatGroupSuccessionCandidate(
                    cat=cat,
                    score=round(
                        min(
                            1.0,
                            score,
                        ),
                        4,
                    ),
                )
            )

        ranked.sort(
            key=lambda item: (
                item.score,
                item.cat_name,
            ),
            reverse=True,
        )

        return tuple(
            ranked
        )

    def succeed(
        self,
        group_id,
        vacated_cat,
        role,
        cats,
        reason="role_vacated",
    ):
        group = self.group_system._group(
            group_id
        )

        holders = group.roles.get(
            role,
            [],
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
                reason=reason,
            )

        ranked = self.candidates(
            group_id,
            role,
            cats,
            exclude=[
                vacated_cat.name
            ],
        )

        if not ranked:
            self._weaken_dependent_institutions(
                group,
                role,
                amount=0.2,
            )

            event = (
                CatGroupRoleBecameVacantEvent(
                    group_id=group_id,
                    role=role,
                    previous_holder=(
                        vacated_cat.name
                    ),
                    reason=reason,
                )
            )

            group.succession_history.append(
                deepcopy(
                    event
                )
            )

            group.history.append(
                deepcopy(
                    event
                )
            )

            return event

        selected = ranked[0]

        successor = selected.cat

        assigned = self.roles.assign(
            group_id,
            successor,
            role,
        )

        if not assigned.assigned:
            raise RuntimeError(
                "Selected succession candidate "
                "could not be assigned."
            )

        self._strengthen_dependent_institutions(
            group,
            role,
            amount=0.05,
        )

        event = CatGroupRoleSucceededEvent(
            group_id=group_id,
            role=role,
            previous_holder=(
                vacated_cat.name
            ),
            successor=successor.name,
            successor_score=(
                selected.score
            ),
            reason=reason,
        )

        group.succession_history.append(
            deepcopy(
                event
            )
        )

        group.history.append(
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
        reason="cat_left_group",
    ):
        roles = tuple(
            cat.group_roles.active.keys()
        )

        succession_events = tuple(
            self.succeed(
                group_id,
                cat,
                role,
                cats,
                reason=reason,
            )
            for role in roles
        )

        leave_result = (
            self.group_system.leave_group(
                group_id,
                cat,
            )
        )

        return (
            CatGroupDepartureWithSuccessionResult(
                group_id=group_id,
                cat=cat.name,
                roles=roles,
                successions=(
                    succession_events
                ),
                leave_result=leave_result,
            )
        )

    def _weaken_dependent_institutions(
        self,
        group,
        role,
        amount,
    ):
        for institution in (
            group.institutions.values()
        ):
            if role not in getattr(
                institution,
                "roles",
                [],
            ):
                continue

            institution.continuity = max(
                0.0,
                float(
                    getattr(
                        institution,
                        "continuity",
                        1.0,
                    )
                )
                - amount,
            )

            if (
                institution.continuity
                <= 0.1
            ):
                institution.active = False

    def _strengthen_dependent_institutions(
        self,
        group,
        role,
        amount,
    ):
        for institution in (
            group.institutions.values()
        ):
            if role not in getattr(
                institution,
                "roles",
                [],
            ):
                continue

            institution.continuity = min(
                1.0,
                float(
                    getattr(
                        institution,
                        "continuity",
                        1.0,
                    )
                )
                + amount,
            )
