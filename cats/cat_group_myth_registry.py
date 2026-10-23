from cats.cat_culture_objects import (
    CatGroupMyth,
)
from cats.cat_myth_lineage_state import (
    CatMythLineageState,
)
from core.entity.domain_object import (
    DomainObject,
)


class CatGroupMythRegistry(
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
        myth,
    ):
        if not isinstance(
            myth,
            CatGroupMyth,
        ):
            raise TypeError(
                "Cat group myth registry requires "
                "CatGroupMyth."
            )

        myth_id = getattr(
            myth,
            "myth_id",
            None,
        )

        if (
            not isinstance(
                myth_id,
                str,
            )
            or not myth_id
        ):
            raise ValueError(
                "Stored cat group myth requires "
                "myth_id."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.myth_id
                == myth_id
            ):
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
            if (
                myth.myth_id
                == myth_id
            ):
                return myth

        return None

    def has(
        self,
        myth_id,
    ):
        return (
            self.record(
                myth_id
            )
            is not None
        )

    def release(
        self,
        myth_id,
    ):
        myth_id = str(
            myth_id
        )

        for index, myth in enumerate(
            self.records()
        ):
            if (
                myth.myth_id
                == myth_id
            ):
                del self._records[
                    index
                ]

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
                    "Cat group myth registry "
                    "contains invalid runtime state."
                )

            myth_id = getattr(
                myth,
                "myth_id",
                None,
            )

            if (
                not isinstance(
                    myth_id,
                    str,
                )
                or not myth_id
            ):
                raise ValueError(
                    "Cat group myth record "
                    "requires myth_id."
                )

        return tuple(
            self._records
        )


class CatGroupMythLineageRegistry(
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
        lineage,
    ):
        if not isinstance(
            lineage,
            CatMythLineageState,
        ):
            raise TypeError(
                "Cat group myth lineage registry "
                "requires CatMythLineageState."
            )

        root_myth = getattr(
            lineage,
            "root_myth",
            None,
        )

        if (
            not isinstance(
                root_myth,
                str,
            )
            or not root_myth
        ):
            raise ValueError(
                "Stored cat myth lineage requires "
                "root_myth."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.root_myth
                == root_myth
            ):
                self._records[
                    index
                ] = lineage

                return lineage

        self._records.append(
            lineage
        )

        return lineage

    def record(
        self,
        root_myth,
    ):
        root_myth = str(
            root_myth
        )

        for lineage in self.records():
            if (
                lineage.root_myth
                == root_myth
            ):
                return lineage

        return None

    def has(
        self,
        root_myth,
    ):
        return (
            self.record(
                root_myth
            )
            is not None
        )

    def release(
        self,
        root_myth,
    ):
        root_myth = str(
            root_myth
        )

        for index, lineage in enumerate(
            self.records()
        ):
            if (
                lineage.root_myth
                == root_myth
            ):
                del self._records[
                    index
                ]

                return lineage

        return None

    def records(
        self,
    ):
        for lineage in self._records:
            if not isinstance(
                lineage,
                CatMythLineageState,
            ):
                raise TypeError(
                    "Cat group myth lineage registry "
                    "contains invalid runtime state."
                )

            root_myth = getattr(
                lineage,
                "root_myth",
                None,
            )

            if (
                not isinstance(
                    root_myth,
                    str,
                )
                or not root_myth
            ):
                raise ValueError(
                    "Cat myth lineage record "
                    "requires root_myth."
                )

        return tuple(
            self._records
        )
