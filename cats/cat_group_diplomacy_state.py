from dataclasses import dataclass, replace

from cats.cat_group_memory_state import (
    CatGroupMemoryState,
)
from core.entity.domain_object import (
    DomainObject,
)
from core.entity.domain_object import (
    DomainObject,
)


class CatGroupDiplomacyRegistry(
    DomainObject
):

    def __init__(
        self,
    ):
        self._records = []

    @property
    def is_empty(
        self,
    ):
        return not self._records

    @property
    def count(
        self,
    ):
        return len(
            self._records
        )

    def store(
        self,
        state,
    ):
        if not isinstance(
            state,
            CatGroupDiplomacyState,
        ):
            raise TypeError(
                "Cat group diplomacy registry requires "
                "CatGroupDiplomacyState."
            )

        other_group_id = str(
            state.other_group_id
        )

        if not other_group_id:
            raise ValueError(
                "Stored diplomacy state requires "
                "other_group_id."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.other_group_id
                == other_group_id
            ):
                self._records[
                    index
                ] = state

                return state

        self._records.append(
            state
        )

        return state

    def record(
        self,
        other_group_id,
    ):
        other_group_id = str(
            other_group_id
        )

        for state in self.records():
            if (
                state.other_group_id
                == other_group_id
            ):
                return state

        return None

    def has(
        self,
        other_group_id,
    ):
        return (
            self.record(
                other_group_id
            )
            is not None
        )

    def records(
        self,
    ):
        for state in self._records:
            if not isinstance(
                state,
                CatGroupDiplomacyState,
            ):
                raise TypeError(
                    "Cat group diplomacy registry "
                    "contains invalid runtime state."
                )

        return tuple(
            self._records
        )


@dataclass(slots=True, frozen=True)
class CatGroupDiplomacyState:
    group_id: str
    other_group_id: str
    score: float
    status: str
    memory: CatGroupMemoryState

    def __post_init__(self):
        if not isinstance(
            self.memory,
            CatGroupMemoryState,
        ):
            raise TypeError(
                "Cat group diplomacy memory must be "
                "CatGroupMemoryState."
            )

    def with_score_delta(
        self,
        delta: float,
    ):
        return replace(
            self,
            score=max(
                -1.0,
                min(
                    1.0,
                    self.score + delta,
                ),
            ),
        )


@dataclass(slots=True, frozen=True)
class CatGroupMutualRelationResult:
    first: CatGroupDiplomacyState
    second: CatGroupDiplomacyState
    mutual_score: float
