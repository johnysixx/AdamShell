from copy import deepcopy

from cats.cat_group_alliance_break_state import (
    CatGroupAllianceBreakDeniedResult,
    CatGroupAllianceBrokenEvent,
)
from cats.cat_group_alliance_defense_state import (
    CatGroupAlliedDefenseDeniedResult,
    CatGroupAlliedDefenseResult,
)
from cats.cat_group_alliance_proposal_state import (
    CatGroupAllianceDeniedResult,
    CatGroupAllianceFormedEvent,
    CatGroupAlliancePreservedResult,
)
from cats.cat_group_diplomacy_system import (
    CatGroupDiplomacySystem
)
from cats.cat_group_memory_system import (
    CatGroupMemorySystem
)


class CatGroupAllianceSystem:

    def __init__(
        self,
        group_system
    ):
        self.group_system = group_system

        self.diplomacy = (
            CatGroupDiplomacySystem(
                group_system
            )
        )

        self.memory = (
            CatGroupMemorySystem(
                group_system
            )
        )

    def propose(
        self,
        first_group_id,
        second_group_id
    ):
        if first_group_id == second_group_id:
            return CatGroupAllianceDeniedResult(
                first_group=first_group_id,
                second_group=second_group_id,
                reason="same_group",
            )

        first = self.group_system._group(
            first_group_id
        )

        second = self.group_system._group(
            second_group_id
        )

        if (
            second_group_id
            in first.alliances
        ):
            return CatGroupAlliancePreservedResult(
                first_group=first_group_id,
                second_group=second_group_id,
            )

        relation = (
            self.diplomacy.mutual_relation(
                first_group_id,
                second_group_id
            )
        )

        first_memory = relation.first.memory

        second_memory = relation.second.memory

        sufficient_history = bool(
            first_memory.cooperations >= 2
            and second_memory.cooperations >= 2
        )

        no_betrayal = bool(
            first_memory.betrayals == 0
            and second_memory.betrayals == 0
        )

        accepted = bool(
            sufficient_history
            and no_betrayal
            and relation.mutual_score >= 0.30
        )

        if not accepted:
            return CatGroupAllianceDeniedResult(
                first_group=first_group_id,
                second_group=second_group_id,
                reason=(
                    "alliance_requirements_not_met"
                ),
                relation=relation,
            )

        first.alliances.append(
            second_group_id
        )

        second.alliances.append(
            first_group_id
        )

        event = CatGroupAllianceFormedEvent(
            first_group=first_group_id,
            second_group=second_group_id,
            relation=relation,
        )

        first.history.append(
            deepcopy(
                event
            )
        )

        second.history.append(
            deepcopy(
                event
            )
        )

        return event

    def shared_defense(
        self,
        first_group_id,
        second_group_id,
        cats,
        threat
    ):
        first = self.group_system._group(
            first_group_id
        )

        if (
            second_group_id
            not in first.alliances
        ):
            return CatGroupAlliedDefenseDeniedResult(
                first_group=first_group_id,
                second_group=second_group_id,
                reason="groups_not_allied",
            )

        first_response = (
            self.group_system
            .respond_to_threat(
                first_group_id,
                cats,
                threat
            )
        )

        second_response = (
            self.group_system
            .respond_to_threat(
                second_group_id,
                cats,
                threat
            )
        )

        self.memory.record_cooperation(
            first_group_id,
            second_group_id,
            cooperation_type=(
                "shared_defense"
            )
        )

        return CatGroupAlliedDefenseResult(
            first_group=first_group_id,
            second_group=second_group_id,
            first_response=first_response,
            second_response=second_response,
        )

    def break_alliance(
        self,
        first_group_id,
        second_group_id,
        reason,
        betrayal=False
    ):
        first = self.group_system._group(
            first_group_id
        )

        second = self.group_system._group(
            second_group_id
        )

        if (
            second_group_id
            not in first.alliances
        ):
            return CatGroupAllianceBreakDeniedResult(
                first_group=first_group_id,
                second_group=second_group_id,
                reason="not_allied",
            )

        first.alliances.remove(
            second_group_id
        )

        second.alliances.remove(
            first_group_id
        )

        if betrayal:
            self.memory.record_betrayal(
                betrayer_group_id=(
                    first_group_id
                ),
                victim_group_id=(
                    second_group_id
                ),
                reason=reason
            )

        event = CatGroupAllianceBrokenEvent(
            first_group=first_group_id,
            second_group=second_group_id,
            reason=reason,
            betrayal=betrayal,
        )

        first.history.append(
            deepcopy(
                event
            )
        )

        second.history.append(
            deepcopy(
                event
            )
        )

        return event
