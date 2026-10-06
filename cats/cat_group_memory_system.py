from copy import deepcopy

from cats.cat_group_memory_state import (
    CatGroupBetrayalEvent,
    CatGroupCooperationEvent,
    CatGroupEncounterRememberedResult,
    CatGroupMemoryEventKind,
    CatGroupMemorySignal,
    CatGroupMemoryState,
)


class CatGroupMemorySystem:
    MAX_RECENT_EVENTS = 12

    def __init__(
        self,
        group_system,
    ):
        self.group_system = group_system

    def remember_encounter(
        self,
        first_group_id,
        second_group_id,
        signal,
    ):
        if not isinstance(
            signal,
            CatGroupMemorySignal,
        ):
            raise TypeError(
                "Cat group encounter memory "
                "requires CatGroupMemorySignal."
            )

        first = (
            self.group_system
            ._group(
                first_group_id
            )
        )

        second = (
            self.group_system
            ._group(
                second_group_id
            )
        )

        first_memory = self._memory(
            first,
            second_group_id,
        )

        second_memory = self._memory(
            second,
            first_group_id,
        )

        self._apply(
            first_memory,
            signal,
            own_group_id=(
                first_group_id
            ),
        )

        self._apply(
            second_memory,
            signal,
            own_group_id=(
                second_group_id
            ),
        )

        return (
            CatGroupEncounterRememberedResult(
                first_group=first_group_id,
                second_group=second_group_id,
            )
        )

    def record_cooperation(
        self,
        first_group_id,
        second_group_id,
        cooperation_type,
    ):
        event = CatGroupCooperationEvent(
            first_group=first_group_id,
            second_group=second_group_id,
            cooperation_type=(
                cooperation_type
            ),
        )

        self.remember_encounter(
            first_group_id,
            second_group_id,
            CatGroupMemorySignal(
                kind=(
                    CatGroupMemoryEventKind
                    .COOPERATION
                ),
            ),
        )

        return event

    def record_betrayal(
        self,
        betrayer_group_id,
        victim_group_id,
        reason,
    ):
        event = CatGroupBetrayalEvent(
            betrayer=(
                betrayer_group_id
            ),
            victim=(
                victim_group_id
            ),
            reason=reason,
        )

        self.remember_encounter(
            betrayer_group_id,
            victim_group_id,
            CatGroupMemorySignal(
                kind=(
                    CatGroupMemoryEventKind
                    .BETRAYAL
                ),
            ),
        )

        return event

    def relation_memory(
        self,
        group_id,
        other_group_id,
    ):
        group = (
            self.group_system
            ._group(
                group_id
            )
        )

        return deepcopy(
            self._memory(
                group,
                other_group_id,
            )
        )

    def _memory(
        self,
        group,
        other_group_id,
    ):
        memory = (
            group.group_memory.get(
                other_group_id
            )
        )

        if memory is None:
            memory = (
                CatGroupMemoryState()
            )

            group.group_memory[
                other_group_id
            ] = memory

        elif not isinstance(
            memory,
            CatGroupMemoryState,
        ):
            raise TypeError(
                "Cat group memory record "
                "must be "
                "CatGroupMemoryState."
            )

        return memory

    def _apply(
        self,
        memory,
        signal,
        own_group_id,
    ):
        memory.encounters += 1

        if (
            signal.kind
            is CatGroupMemoryEventKind.BETRAYAL
        ):
            memory.betrayals += 1
            outcome = "betrayal"

        elif (
            signal.kind
            is CatGroupMemoryEventKind.COOPERATION
        ):
            memory.cooperations += 1
            outcome = "cooperation"

        elif (
            signal.kind
            is CatGroupMemoryEventKind.CONFLICT
        ):
            memory.conflicts += 1

            if signal.winner is None:
                memory.standoffs += 1
                outcome = "standoff"

            elif (
                signal.winner
                == own_group_id
            ):
                memory.victories += 1
                outcome = "victory"

            elif (
                signal.loser
                == own_group_id
            ):
                memory.defeats += 1
                outcome = "defeat"

            else:
                outcome = "conflict"

        else:
            memory.peaceful_encounters += 1
            outcome = "peaceful"

        memory.last_outcome = (
            outcome
        )

        recent = list(
            memory.recent_events
        )

        recent.append(
            outcome
        )

        memory.recent_events = (
            recent[
                -self.MAX_RECENT_EVENTS:
            ]
        )
