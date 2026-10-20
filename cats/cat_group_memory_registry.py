from dataclasses import dataclass, field

from cats.cat_group_memory_state import (
    CatGroupMemoryState,
)


@dataclass(slots=True)
class CatGroupMemoryRegistry:

    _records: list = field(
        default_factory=list
    )

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
        memory,
    ):
        if not isinstance(
            memory,
            CatGroupMemoryState,
        ):
            raise TypeError(
                "Cat group memory registry requires "
                "CatGroupMemoryState."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.other_group_id
                == memory.other_group_id
            ):
                self._records[
                    index
                ] = memory

                return memory

        self._records.append(
            memory
        )

        return memory

    def record(
        self,
        other_group_id,
    ):
        other_group_id = str(
            other_group_id
        )

        for memory in self.records():
            if (
                memory.other_group_id
                == other_group_id
            ):
                return memory

        return None

    def records(
        self,
    ):
        for memory in self._records:
            if not isinstance(
                memory,
                CatGroupMemoryState,
            ):
                raise TypeError(
                    "Cat group memory registry contains "
                    "invalid runtime state."
                )

        return tuple(
            self._records
        )
