from core.entity.domain_object import (
    DomainObject,
)
from cats.cat_social_objects import (
    CatGroupKnowledgeRecord,
)


class CatGroupKnowledgeRegistry(
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
            CatGroupKnowledgeRecord,
        ):
            raise TypeError(
                "Cat group knowledge registry requires "
                "CatGroupKnowledgeRecord."
            )

        if not hasattr(
            record,
            "knowledge_id",
        ):
            raise ValueError(
                "Stored group knowledge requires "
                "knowledge_id."
            )

        knowledge_id = str(
            record.knowledge_id
        )

        if not knowledge_id:
            raise ValueError(
                "Stored group knowledge requires "
                "non-empty knowledge_id."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                str(
                    current.knowledge_id
                )
                == knowledge_id
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
        knowledge_id,
    ):
        knowledge_id = str(
            knowledge_id
        )

        for record in self.records():
            if (
                str(
                    record.knowledge_id
                )
                == knowledge_id
            ):
                return record

        return None

    def has(
        self,
        knowledge_id,
    ):
        return (
            self.record(
                knowledge_id
            )
            is not None
        )

    def release(
        self,
        knowledge_id,
    ):
        knowledge_id = str(
            knowledge_id
        )

        for index, record in enumerate(
            self.records()
        ):
            if (
                str(
                    record.knowledge_id
                )
                == knowledge_id
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
            if not isinstance(
                record,
                CatGroupKnowledgeRecord,
            ):
                raise TypeError(
                    "Cat group knowledge registry "
                    "contains invalid runtime state."
                )

            if not hasattr(
                record,
                "knowledge_id",
            ):
                raise ValueError(
                    "Cat group knowledge record "
                    "requires knowledge_id."
                )

        return tuple(
            self._records
        )
