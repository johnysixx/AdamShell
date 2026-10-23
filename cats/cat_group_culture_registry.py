from core.entity.domain_object import (
    DomainObject,
)
from cats.cat_cultural_preference_state import (
    CatCulturalPreferenceState,
)
from cats.cat_cultural_tradition_state import (
    CatCulturalTraditionState,
)


class CatGroupTraditionRegistry(
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
        record,
    ):
        if not isinstance(
            record,
            CatCulturalTraditionState,
        ):
            raise TypeError(
                "Cat group tradition registry requires "
                "CatCulturalTraditionState."
            )

        name = getattr(
            record,
            "name",
            None,
        )

        if (
            not isinstance(
                name,
                str,
            )
            or not name
        ):
            raise ValueError(
                "Stored group tradition requires name."
            )

        for index, current in enumerate(
            self.records()
        ):
            if current.name == name:
                self._records[
                    index
                ] = record

                return record

        self._records.append(
            record
        )

        return record

    def record(
        self,
        name,
    ):
        name = str(
            name
        )

        for record in self.records():
            if record.name == name:
                return record

        return None

    def has(
        self,
        name,
    ):
        return (
            self.record(
                name
            )
            is not None
        )

    def release(
        self,
        name,
    ):
        name = str(
            name
        )

        for index, record in enumerate(
            self.records()
        ):
            if record.name == name:
                del self._records[
                    index
                ]

                return record

        return None

    def records(
        self,
    ):
        for record in self._records:
            if not isinstance(
                record,
                CatCulturalTraditionState,
            ):
                raise TypeError(
                    "Cat group tradition registry "
                    "contains invalid runtime state."
                )

            if (
                not isinstance(
                    record.name,
                    str,
                )
                or not record.name
            ):
                raise ValueError(
                    "Cat group tradition record "
                    "requires name."
                )

        return tuple(
            self._records
        )


class CatGroupPreferenceRegistry(
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
        record,
    ):
        if not isinstance(
            record,
            CatCulturalPreferenceState,
        ):
            raise TypeError(
                "Cat group preference registry requires "
                "CatCulturalPreferenceState."
            )

        name = getattr(
            record,
            "name",
            None,
        )

        if (
            not isinstance(
                name,
                str,
            )
            or not name
        ):
            raise ValueError(
                "Stored group preference requires name."
            )

        for index, current in enumerate(
            self.records()
        ):
            if current.name == name:
                self._records[
                    index
                ] = record

                return record

        self._records.append(
            record
        )

        return record

    def record(
        self,
        name,
    ):
        name = str(
            name
        )

        for record in self.records():
            if record.name == name:
                return record

        return None

    def has(
        self,
        name,
    ):
        return (
            self.record(
                name
            )
            is not None
        )

    def release(
        self,
        name,
    ):
        name = str(
            name
        )

        for index, record in enumerate(
            self.records()
        ):
            if record.name == name:
                del self._records[
                    index
                ]

                return record

        return None

    def records(
        self,
    ):
        for record in self._records:
            if not isinstance(
                record,
                CatCulturalPreferenceState,
            ):
                raise TypeError(
                    "Cat group preference registry "
                    "contains invalid runtime state."
                )

            if (
                not isinstance(
                    record.name,
                    str,
                )
                or not record.name
            ):
                raise ValueError(
                    "Cat group preference record "
                    "requires name."
                )

        return tuple(
            self._records
        )
