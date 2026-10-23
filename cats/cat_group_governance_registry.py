from cats.cat_culture_objects import (
    CatGroupInstitution,
    CatGroupNorm,
    CatGroupTaboo,
    CatInstitutionConflict,
)
from core.entity.domain_object import (
    DomainObject,
)


class _CatGroupTypedRegistry(
    DomainObject
):

    record_type = None
    key_attribute = None
    record_label = "record"

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

    def _key(
        self,
        record,
    ):
        if not isinstance(
            record,
            self.record_type,
        ):
            raise TypeError(
                f"{self.record_label} registry requires "
                f"{self.record_type.__name__}."
            )

        key = getattr(
            record,
            self.key_attribute,
            None,
        )

        if (
            not isinstance(
                key,
                str,
            )
            or not key
        ):
            raise ValueError(
                f"Stored {self.record_label} requires "
                f"{self.key_attribute}."
            )

        return key

    def store(
        self,
        record,
    ):
        key = self._key(
            record
        )

        for index, current in enumerate(
            self.records()
        ):
            if (
                getattr(
                    current,
                    self.key_attribute,
                )
                == key
            ):
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
        key,
    ):
        key = str(
            key
        )

        for record in self.records():
            if (
                getattr(
                    record,
                    self.key_attribute,
                )
                == key
            ):
                return record

        return None

    def has(
        self,
        key,
    ):
        return (
            self.record(
                key
            )
            is not None
        )

    def release(
        self,
        key,
    ):
        key = str(
            key
        )

        for index, record in enumerate(
            self.records()
        ):
            if (
                getattr(
                    record,
                    self.key_attribute,
                )
                == key
            ):
                del self._records[
                    index
                ]

                return record

        return None

    def records(
        self,
    ):
        for record in self._records:
            self._key(
                record
            )

        return tuple(
            self._records
        )


class CatGroupInstitutionRegistry(
    _CatGroupTypedRegistry
):

    record_type = CatGroupInstitution
    key_attribute = "name"
    record_label = "Cat group institution"


class CatGroupNormRegistry(
    _CatGroupTypedRegistry
):

    record_type = CatGroupNorm
    key_attribute = "id"
    record_label = "Cat group norm"


class CatGroupTabooRegistry(
    _CatGroupTypedRegistry
):

    record_type = CatGroupTaboo
    key_attribute = "id"
    record_label = "Cat group taboo"


class CatGroupInstitutionConflictRegistry(
    _CatGroupTypedRegistry
):

    record_type = CatInstitutionConflict
    key_attribute = "id"
    record_label = (
        "Cat group institution conflict"
    )
