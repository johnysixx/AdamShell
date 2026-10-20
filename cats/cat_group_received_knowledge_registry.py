from dataclasses import dataclass, field

from cats.cat_social_objects import (
    CatGroupKnowledgeRecord,
)


@dataclass(slots=True)
class CatGroupReceivedKnowledgeRegistry:

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
        record,
    ):
        if not isinstance(
            record,
            CatGroupKnowledgeRecord,
        ):
            raise TypeError(
                "Received group knowledge registry "
                "requires CatGroupKnowledgeRecord."
            )

        if not hasattr(
            record,
            "knowledge_id",
        ):
            raise ValueError(
                "Received group knowledge record "
                "requires knowledge_id."
            )

        knowledge_id = str(
            record.knowledge_id
        )

        for index, current in enumerate(
            self.records()
        ):
            if str(
                current.knowledge_id
            ) == knowledge_id:
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
            if str(
                record.knowledge_id
            ) == knowledge_id:
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
                    "Received group knowledge registry "
                    "contains invalid runtime state."
                )

            if not hasattr(
                record,
                "knowledge_id",
            ):
                raise ValueError(
                    "Received group knowledge record "
                    "requires knowledge_id."
                )

        return tuple(
            self._records
        )
