from cats.cat_culture_objects import (
    CatGroupRitual,
)
from cats.cat_ritual_lineage_state import (
    CatRitualLineageState,
)
from core.entity.domain_object import (
    DomainObject,
)


class CatGroupRitualRegistry(
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
        ritual,
    ):
        if not isinstance(
            ritual,
            CatGroupRitual,
        ):
            raise TypeError(
                "Cat group ritual registry requires "
                "CatGroupRitual."
            )

        name = getattr(
            ritual,
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
                "Stored cat group ritual requires name."
            )

        for index, current in enumerate(
            self.records()
        ):
            if current.name == name:
                self._records[
                    index
                ] = ritual

                return ritual

        self._records.append(
            ritual
        )

        return ritual

    def record(
        self,
        name,
    ):
        name = str(
            name
        )

        for ritual in self.records():
            if ritual.name == name:
                return ritual

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

        for index, ritual in enumerate(
            self.records()
        ):
            if ritual.name == name:
                del self._records[
                    index
                ]

                return ritual

        return None

    def records(
        self,
    ):
        for ritual in self._records:
            if not isinstance(
                ritual,
                CatGroupRitual,
            ):
                raise TypeError(
                    "Cat group ritual registry "
                    "contains invalid runtime state."
                )

            name = getattr(
                ritual,
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
                    "Cat group ritual record requires name."
                )

        return tuple(
            self._records
        )


class CatGroupRitualLineageRegistry(
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
            CatRitualLineageState,
        ):
            raise TypeError(
                "Cat group ritual lineage registry "
                "requires CatRitualLineageState."
            )

        root_ritual = getattr(
            lineage,
            "root_ritual",
            None,
        )

        if (
            not isinstance(
                root_ritual,
                str,
            )
            or not root_ritual
        ):
            raise ValueError(
                "Stored cat ritual lineage requires "
                "root_ritual."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.root_ritual
                == root_ritual
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
        root_ritual,
    ):
        root_ritual = str(
            root_ritual
        )

        for lineage in self.records():
            if (
                lineage.root_ritual
                == root_ritual
            ):
                return lineage

        return None

    def has(
        self,
        root_ritual,
    ):
        return (
            self.record(
                root_ritual
            )
            is not None
        )

    def release(
        self,
        root_ritual,
    ):
        root_ritual = str(
            root_ritual
        )

        for index, lineage in enumerate(
            self.records()
        ):
            if (
                lineage.root_ritual
                == root_ritual
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
                CatRitualLineageState,
            ):
                raise TypeError(
                    "Cat group ritual lineage registry "
                    "contains invalid runtime state."
                )

            root_ritual = getattr(
                lineage,
                "root_ritual",
                None,
            )

            if (
                not isinstance(
                    root_ritual,
                    str,
                )
                or not root_ritual
            ):
                raise ValueError(
                    "Cat ritual lineage record requires "
                    "root_ritual."
                )

        return tuple(
            self._records
        )
