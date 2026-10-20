from dataclasses import dataclass, field

from cats.cat_culture_objects import (
    CatGroupMyth,
)


@dataclass(slots=True)
class CatHeardGroupMythRegistry:

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
        myth,
    ):
        if not isinstance(
            myth,
            CatGroupMyth,
        ):
            raise TypeError(
                "Heard group myth registry requires "
                "CatGroupMyth records."
            )

        if not hasattr(
            myth,
            "myth_id",
        ):
            raise ValueError(
                "Heard group myth requires myth_id."
            )

        myth_id = str(
            myth.myth_id
        )

        for index, current in enumerate(
            self.records()
        ):
            if str(
                current.myth_id
            ) == myth_id:
                self._records[
                    index
                ] = myth

                return myth

        self._records.append(
            myth
        )

        return myth

    def record(
        self,
        myth_id,
    ):
        myth_id = str(
            myth_id
        )

        for myth in self.records():
            if str(
                myth.myth_id
            ) == myth_id:
                return myth

        return None

    def records(
        self,
    ):
        for myth in self._records:
            if not isinstance(
                myth,
                CatGroupMyth,
            ):
                raise TypeError(
                    "Heard group myth registry contains "
                    "invalid runtime state."
                )

            if not hasattr(
                myth,
                "myth_id",
            ):
                raise ValueError(
                    "Heard group myth record requires "
                    "myth_id."
                )

        return tuple(
            self._records
        )
