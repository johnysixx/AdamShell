from copy import deepcopy

from cats.cat_group_bonding_system import (
    CatGroupBondingSystem,
)
from cats.cat_group_lifecycle_state import (
    CatGroupDissolvedEvent,
    CatGroupLifecycleAdvancedEvent,
    CatGroupLifecycleSkippedResult,
    CatGroupLifecycleState,
)


class CatGroupLifecycleSystem:

    def __init__(
        self,
        group_system,
    ):
        self.group_system = group_system

        self.bonding = (
            CatGroupBondingSystem(
                group_system
            )
        )

    def advance(
        self,
        group_id,
        cats,
    ):
        group = (
            self.group_system
            ._group(
                group_id
            )
        )

        if getattr(
            group,
            "dissolved",
            False,
        ):
            return (
                CatGroupLifecycleSkippedResult(
                    group_id=group_id,
                    state=(
                        CatGroupLifecycleState
                        .DISSOLVED
                    ),
                )
            )

        group.age_ticks += 1

        members = (
            self.group_system
            ._member_objects(
                group,
                cats,
            )
        )

        cohesion = (
            self.bonding.evaluate(
                group_id,
                cats,
            )
        )

        member_count = len(
            members
        )

        previous = group.state

        if member_count == 0:
            state = (
                CatGroupLifecycleState
                .DISSOLVED
            )

        elif member_count == 1:
            state = (
                CatGroupLifecycleState
                .FORMING
            )

        elif cohesion.cohesion >= 0.65:
            state = (
                CatGroupLifecycleState
                .STABLE
            )

        elif (
            group.conflict_count > 0
            and cohesion.cohesion < 0.3
        ):
            state = (
                CatGroupLifecycleState
                .STRAINED
            )

        else:
            state = (
                CatGroupLifecycleState
                .GROWING
            )

        group.state = state

        if (
            state
            is CatGroupLifecycleState
            .DISSOLVED
        ):
            group.dissolved = True

        event = (
            CatGroupLifecycleAdvancedEvent(
                group_id=group_id,
                previous_state=previous,
                state=state,
                age_ticks=(
                    group.age_ticks
                ),
                member_count=(
                    member_count
                ),
                cohesion=(
                    cohesion.cohesion
                ),
            )
        )

        group.history.append(
            deepcopy(
                event
            )
        )

        return event

    def dissolve(
        self,
        group_id,
        cats,
        reason=(
            "group_no_longer_viable"
        ),
    ):
        group = (
            self.group_system
            ._group(
                group_id
            )
        )

        members = list(
            self.group_system
            ._member_objects(
                group,
                cats,
            )
        )

        for cat in members:
            cat.group.group_id = None
            cat.group.member = False
            cat.group.joined_order = None
            cat.group.shared_scent = 0.0
            cat.group.accepted_members = []

        group.members = []

        group.state = (
            CatGroupLifecycleState
            .DISSOLVED
        )

        group.dissolved = True

        event = CatGroupDissolvedEvent(
            group_id=group_id,
            reason=reason,
            former_members=tuple(
                cat.name
                for cat in members
            ),
        )

        group.history.append(
            deepcopy(
                event
            )
        )

        return event
