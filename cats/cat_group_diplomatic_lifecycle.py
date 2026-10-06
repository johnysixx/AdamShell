from copy import deepcopy

from cats.cat_group_diplomatic_lifecycle_state import (
    CatGroupBetrayalRecoveredResult,
    CatGroupBetrayalRecoveryDeniedResult,
    CatGroupBetrayalRecoverySkippedResult,
    CatGroupDiplomacyDecaySkippedResult,
    CatGroupDiplomacyMemoryAgedEvent,
    CatGroupMemorySnapshot,
)
from cats.cat_group_memory_state import (
    CatGroupMemoryState,
)


class CatGroupDiplomaticLifecycle:

    def __init__(
        self,
        group_system,
    ):
        self.group_system = group_system

    def advance_relation(
        self,
        group_id,
        other_group_id,
    ):
        group = self.group_system._group(
            group_id
        )

        memory = (
            group.group_memory.get(
                other_group_id
            )
        )

        if memory is None:
            return (
                CatGroupDiplomacyDecaySkippedResult(
                    reason="no_shared_history",
                )
            )

        if not isinstance(
            memory,
            CatGroupMemoryState,
        ):
            raise TypeError(
                "Cat group memory record must be "
                "CatGroupMemoryState."
            )

        before = (
            CatGroupMemorySnapshot
            .from_state(
                memory
            )
        )

        if memory.conflicts > 0:
            memory.conflicts -= 1

        if memory.defeats > 0:
            memory.defeats -= 1

        if (
            memory.peaceful_encounters
            > 0
        ):
            memory.peaceful_encounters -= 1

        if (
            memory.cooperations > 0
            and memory.encounters % 2
            == 0
        ):
            memory.cooperations -= 1

        after = (
            CatGroupMemorySnapshot
            .from_state(
                memory
            )
        )

        event = (
            CatGroupDiplomacyMemoryAgedEvent(
                group_id=group_id,
                other_group_id=
                    other_group_id,
                before=before,
                after=after,
            )
        )

        group.history.append(
            deepcopy(
                event
            )
        )

        return event

    def recover_from_betrayal(
        self,
        group_id,
        other_group_id,
    ):
        group = self.group_system._group(
            group_id
        )

        memory = (
            group.group_memory.get(
                other_group_id
            )
        )

        if memory is None:
            return (
                CatGroupBetrayalRecoveryDeniedResult(
                    reason="no_shared_history",
                )
            )

        if not isinstance(
            memory,
            CatGroupMemoryState,
        ):
            raise TypeError(
                "Cat group memory record must be "
                "CatGroupMemoryState."
            )

        if memory.betrayals <= 0:
            return (
                CatGroupBetrayalRecoverySkippedResult(
                    reason="no_betrayal",
                )
            )

        if memory.cooperations < 3:
            return (
                CatGroupBetrayalRecoveryDeniedResult(
                    reason=(
                        "insufficient_new_cooperation"
                    ),
                )
            )

        memory.betrayals -= 1

        return (
            CatGroupBetrayalRecoveredResult(
                group_id=group_id,
                other_group_id=
                    other_group_id,
                remaining_betrayals=
                    memory.betrayals,
            )
        )
