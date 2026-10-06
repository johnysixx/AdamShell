from dataclasses import dataclass, replace

from cats.cat_group_memory_state import (
    CatGroupMemoryState,
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
